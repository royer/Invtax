# vim: tabstop=4 softtabstop=4 shiftwidth=4

module QifLibaray
	
	ACCOUNT_TYPES = [
		"Cash",
		"Bank",
		"Ccard",
		"Oth A",
		"Oth L",
		"Invst",
		"Invoice"
	]


	class Qif
		
		def initialize
			@accounts = {}
			@categories = []
			@classes = []
			@securities = []
			@transactions = {}
		end

		def accounts
			@accounts.clone.freeze
		end
	end

	class Account
		
		attr_accessor :currency
		attr_accessor :name
		attr_accessor :type
		attr_accessor :balance
		attr_accessor :balance_date
		attr_accessor :credit_limit
		attr_accessor :description

		def initialize
			@currency = 'US$'

			@transcations = []
		end
	end

	# Transcation except investment account
	class Transcation

		attr_accessor :date
		attr_accessor :num
		attr_accessor :cleared
		attr_accessor :payee
		attr_accessor :memo
		attr_accessor :address
		attr_accessor :category
		attr_accessor :to_account
	end

	# Transcation of inverstment account
	class Investment

		attr_accessor :date
		attr_accessor :action
		attr_accessor :security
		attr_accessor :price
		attr_accessor :quantity
		attr_accessor :cleared
		attr_accessor :amount
		attr_accessor :memo
		attr_accessor :first_line
		attr_accessor :to_account
		attr_accessor :amount_transfer
		attr_accessor :commission
	end

	class Category
		
		attr_accessor :name
		attr_accessor :description
		attr_accessor :tax_related
		attr_accessor :expense
		attr_accessor :income
		attr_accessor :buget_amount
		attr_accessor :tax_schedule_amount
	end

	class Class
		
		attr_accessor :name
		attr_accessor :description
	end

	class Security
		
		attr_accessor :name
		attr_accessor :symbol
		attr_accessor :security_type
	end
