#!/usr/bin/python
#
# vim: tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
#
# Investment Statment Generator.
# 
# This script process transcation file of inverstment that gernated by
# iBank, then output security holding infomation at the end of each
# year.

from __future__ import print_function
import math
import sys
import copy
import operator
import datetime
import argparse
import calendar

import six
from qifparse.parser import QifParser
from qifparse.parser import Investment
COL_SECURITY_NAME    = 0
COL_MAXCOST_INYEAR   = 1
COL_COST_END_OF_YEAR = 2

class SecurityStatement(object):
	def __init__(self, name):
		self.name = name
		self.shares = 0.0
		self.cost = 0.0
		self.maxcost = 0.0
		self.sellamount = 0.0
	
	def __str__(self):
		return '%s, %.3f, %.2f, %.2f' % (self.name, self.shares, \
				self.maxcost, self.cost)
	
	def buy(self, shares, amount):
		self.shares += shares
		self.cost += amount
		if self.cost > self.maxcost:
			self.maxcost = self.cost
	
	def sell(self, shares, amount):
		if self.shares <= 0: #for short sell or option's sell to open operator
			avgprice = 0.0
			self.sellamount += amount
		else:
			avgprice = self.cost / self.shares
			deductcost = avgprice * shares
			self.cost -= deductcost
		self.shares -= shares

		#return amount - deductcost


	def sell_to_open(self, shares, amount):
		self.shares -= shares
		self.cost -= amount
		if self.cost < self.maxcost:
			self.maxcost = self.cost

	def buy_to_close(self, shares, amount):
		avgprice = self.cost / self.shares
		deductcost = avgprice * shares
		self.shares += shares
		self.cost += deductcost
		if (self.shares > 0):
			raise RuntimeError(six.u("%s hold shares great 0 is impossible for short" % (self.name)))
		if (self.cost > 0.01):
			raise RuntimeError(six.u("%s hold cost(%.2f) great 0 is impossible for short" % (self.name, self.cost)))



        

class Statement(object):

	def __init__(self, date):
		self._date = date
		self._securities = {}

		
	def buy(self, name, shares, amount):
		ss = None
		if name not in self._securities:
			ss = SecurityStatement(name)
			self._securities[name] = ss
		else:
			ss = self._securities[name]
		ss.buy(shares,amount)

	def sell(self, name, shares, amount):
		ss = None
		if name not in self._securities:
			ss = SecurityStatement(name)
			self._securities[name] = ss
		else:
			ss = self._securities[name]
		ss.sell(shares,amount)

	def sell_to_open(self, name, shares, amount):
		ss = None
		if name not in self.securities:
			ss = SecurityStatement(name)
			self._securities[name] = ss
		else:
			ss = self._securities[name]
		ss.sell_to_open( shares, amount)

	def buy_to_close(self, name, shares, amount):
		if name not in self._securities:
			raise RuntimeError(six.u("buy to close has no secrity"))
		self._securities[name].buy_to_close(shares, amount)


	def __str__(self):
		res = []
		res.append(str(self._date))
		for s in self._securities.values():
			res.append(str(s))

		return '\n'.join(res)

	def rebuild(self, date):
		"""
		"""
		self._date = date
		for s in self._securities.items():
			s[1].maxcost = s[1].cost
			if s[1].shares == 0:
				del self._securities[s[0]]



class Statements(object):
	def __init__(self, begin_date=None,s_type='yearly') :
		"""
			s_type: 'yearly' or 'monthly' 
		"""

		self._statement_type = s_type
		self._lastest_date = begin_date
		self._statements = {}

		if begin_date:
			keydate = self._to_keydate(begin_date)
			if self._statement_type == 'yearly':
				self._statements[keydate] = Statement(keydate)
			elif self._statement_type == 'monthly':
				self._statements[keydate] = Statement(keydate)
	
	def __str__(self):
		res = []
		sorted_s = sorted(self._statements.items(), key = operator.itemgetter(0))
		for s in sorted_s:
			res.append(str(s[1]))
		return '\n'.join(res)

	def to_keydate(self, date):
		"""
			convert date to key depend _statement_type
		"""
		if self._statement_type == 'yearly':
			return datetime.date(date.year,12,31)
		else:
			return datetime.date(date.year, date.month,\
					calendar.monthrange(date.year, date.month)[1])

	def get_prev_statement(self, date):
		if len(self._statements) == 0:
			return None
		keys = self._statements.keys()
		keys = sorted(keys,reverse=True)
		for key in keys:
			if key < date:
				return self._statements[key]

		return None


		


	def new_statement(self,date):
		keydate = self.to_keydate(date)
		if (keydate in self._statements):
			raise RuntimeError(six.u("the %s statement already exist." % str(keydate)))

		prevstatement = self.get_prev_statement(date)
		statement = copy.deepcopy(prevstatement) \
				if prevstatement != None else Statement(keydate) 
	
		if self._lastest_date == None:
			self._lastest_date = keydate
		else:
			if self._lastest_date < keydate:
				self._lastest_date = keydate
		statement.rebuild(keydate)
		self._statements[keydate] = statement

		return statement
			


	def buy(self, security_name, shares, amount, date):
		key_date = self.to_keydate(date)

		if self._lastest_date and key_date < self._lastest_date :
			raise RuntimeError(six.u("transcation is not order by date."))
		statement = None
		if key_date in self._statements :
			statement = self._statements[key_date]
		else:
			statement = self.new_statement(key_date)

		statement.buy(security_name,shares, amount)


	def sell(self, security_name, shares, amount, date):
		key_date = self.to_keydate(date)

		if self._lastest_date and key_date < self._lastest_date:
			raise RuntimeError(six.u("transcation is not order by date"))
		statement = None
		if key_date in self._statements:
			statement = self._statements[key_date]
		else:
			statement = self.new_statement(key_date)

		statement.sell(security_name, shares, amount)



Securities = []

argParse = argparse.ArgumentParser(description='Generate security holding statement')
argParse.add_argument("qiffile", help='the transcation file(.qif) file',\
		nargs='?',type=argparse.FileType('r'),default=sys.stdin)
argParse.add_argument("outfile",help="the output file",\
		nargs='?', type=argparse.FileType('w'),default=sys.stdout)
argParse.add_argument("-y", help="only output this year",type=int)

args = argParse.parse_args()

qif = QifParser.parse(args.qiffile)



statements = Statements(s_type = 'yearly')

for ac in qif.get_accounts():
	for trs in ac._transactions.values():
		for tr in trs:
			if tr.action == None:
				continue
			action = tr.action.upper()

			if action == 'BUY' or \
				action == 'BUY TO CLOSE' or \
				action == 'BUY TO OPEN':
				statements.buy(tr.security, tr.quantity, tr.amount, tr.date)
			elif action == 'SELL' or \
					action == 'SELL TO OPEN' or \
					action == 'SELLX':
				statements.sell(tr.security, tr.quantity, tr.amount, tr.date)
			else:
				print ("unknown action:" + tr.action, file=sys.stderr)

#print str(qif)

print (statements)
