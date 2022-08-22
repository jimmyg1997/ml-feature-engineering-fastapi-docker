from dateutil    import parser
from typing      import Optional, List, Dict, Any
from src.models  import Customer, LoanStatus, Term, Customer, Loan


db : List[Customer] = [
						Customer(id            = 1090,
							     annual_income = 41333,
  								 loans = [	Loan(id     = 1,
											 	 loan_date   = parser.parse("15/11/2021"),
											 	 amount      = 2426,
											 	 term        = Term.long,
											 	 fee         = 199,
											 	 loan_status = LoanStatus.not_paid
										 	)	
  								 ]
						),

						Customer(id            = 3565,
							     annual_income = 76498,
							     loans = [ Loan(id          = 2,
												 loan_date   = parser.parse("07/03/2021"),
												 amount      = 2153,
												 term        = Term.short,
												 fee         = 53,
												 loan_status = LoanStatus.not_paid
											),

											Loan(id          = 3,
												 loan_date   = parser.parse("06/08/2021"),
												 amount      = 1538,
												 term        = Term.long,
												 fee         = 89,
												 loan_status = LoanStatus.paid
											)

							     ]
						),
]