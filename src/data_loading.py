import os
import json
import ujson
import numpy    as np
import pandas   as pd
import datetime as dt
from IPython.display import display
from collections     import defaultdict
from typing 		 import Callable, Dict, Generic, Optional, Set, Tuple, TypeVar, Deque, List, Any


from src.models import Customer, LoanStatus, Term, Customer, Loan, CustomerUpdateRequest
from src.config import Config
from src.markI  import MkI


class DataLoader(object) : 
	def __init__(self, mk1 : MkI, config : Config):

		# system design
		self.mk1    = mk1
		self.config = config

		# self.customer_features = ["customer_ID", "annual_income", "loans"]
		# self.loans_features    = ["customer_ID",  "loan_date", "amount", "term", "fee", "loan_status"]

		# data
		self.data_dir       = str(config.get("data","data_dir"))
		self.data_json_path = str(config.get("data","data_json_path"))
		self.data_csv_path  = str(config.get("data","data_csv_path"))


		self.customers_df = None
		self.customers    = []
		self.loans_df     = None
		self.loans        = []
		self.data_df      = None
		pass


	#*-*-*-*-*-*-*-*-*-*-*-*#
	#       Dataframes      #
	#*-*-*-*-*-*-*-*-*-*-*-*#

	def preprocess_customers_dataframe(self, customers_df : pd.DataFrame) :
		try : 

			# 1. Extract `annual_income` feature & deletion
			customers_df["annual_income"] = customers_df.apply(lambda x : float(x["loans"][0]["annual_income"]), axis = 1)
			
			# 2. Deletions
			customers_df = customers_df.drop(["loans"], axis = 1, errors = 'ignore')

			# 3. Renamings
			customers_df = customers_df.rename(columns = {"customer_ID"  : "customer_id"})
	
			# logger
			self.mk1.logging.logger.info("(DataLoader.preprocess_customers_dataframe) Customer Data are preprocessed sucessfully ✅")
			return customers_df

		except Exception as e:
			self.mk1.logging.logger.error("(DataLoader.preprocess_customers_dataframe) Customer Data preprocessing failed : {}".format(e))
			raise e

	def preprocess_loans_dataframe(self, loans_df : pd.DataFrame) -> pd.DataFrame:

		try : 

			# 1. Explode loans into multiple rows & normalize
			loans_df = loans_df.explode()
			loans_df = pd.json_normalize(loans_df)

			# 2. Deletions
			loans_df = loans_df.drop(["annual_income"], axis = 1, errors = 'ignore')

			# 2. Renamings & index
			loans_df = loans_df.rename(columns = {"customer_ID"  : "customer_id"})
			loans_df = loans_df.rename_axis("loan_id").reset_index().astype(str)

			# logger
			self.mk1.logging.logger.info("(DataLoader.preprocess_loans_dataframe) Loans Data are preprocessed sucessfully ✅")
			return loans_df

		except Exception as e:
			self.mk1.logging.logger.error("(DataLoader.preprocess_loans_dataframe) Loans Data preprocessing failed : {}".format(e))
			raise e

	def postprocess_loans_dataframe(self, loans_df : pd.DataFrame) -> pd.DataFrame : 
		try : 
			# Fix Datatypes
			loans_df["loan_date"] = pd.to_datetime(loans_df["loan_date"], dayfirst = True)
			loans_df["amount"]    = loans_df["amount"].apply(pd.to_numeric)
			loans_df["fee"]       = loans_df["fee"].apply(pd.to_numeric)

			# logger
			self.mk1.logging.logger.info("(DataLoader.postprocess_loans_dataframe) Loans Data are postprocessed sucessfully ✅")
			return loans_df

		except Exception as e:
			self.mk1.logging.logger.error("(DataLoader.postprocess_loans_dataframe) Loans Data postprocessing failed : {}".format(e))
			raise e


	def split_dataframes(self, data_df : pd.DataFrame) : 

		customers_df = data_df.copy()
		loans_df     = data_df["loans"]

		return (customers_df, loans_df)




	# def get_customers_dataframe(self, data_df : pd.DataFrame) -> pd.DataFrame :

	# 	try : 

	# 		self.customers_df = data_df.copy()
	# 		self.customers_df["annual_income"] = self.customers_df.apply(lambda x : float(x["loans"][0]["annual_income"]), axis = 1)
	# 		del self.customers_df["loans"]
	# 		self.customers_df = self.customers_df.rename(columns = {"customer_ID"  : "customer_id"})
	# 		#self.customers_df = self.customers_df.reset_index(drop = True)
	# 		# logger
	# 		self.mk1.logging.logger.info("(DataLoader.get_customers_dataframe) Customer Data are retrieved sucessfully ✅")
	# 		return self.customers_df

	# 	except Exception as e:
	# 		self.mk1.logging.logger.error("(DataLoader.get_customers_dataframe) Customer Data retrieval failed : {}".format(e))
	# 		raise e



	# def get_customers_objects(self):
	# 	""" Iterate over all customer key, values and create a list of customer objects"""
	# 	for _, row in self.customers_df.iterrows():

	# 		try : 

	# 			customer = Customer(
	# 							id            = row["customer_id"],
	# 							annual_income = row["annual_income"],
	# 						)
	# 			self.customers.append(customer)
	# 			# logger
	# 			self.mk1.logging.logger.info("(DataLoader.get_customers_objects) Customer object was created sucessfully ✅")

	# 		except Exception as e:
	# 			self.mk1.logging.logger.error("(DataLoader.get_customers_objects) Customer object creation failed: {}".format(e))
	# 			raise e



	# def get_loans_dataframe(self, data_df : pd.DataFrame) -> pd.DataFrame:

	# 	try : 

	# 		# 1. Explore loans into multiple rows & normalize
	# 		self.loans_df = data_df["loans"].explode()
	# 		self.loans_df = pd.json_normalize(self.loans_df)

	# 		del self.loans_df["annual_income"]

	# 		# 2. Renamings & index
	# 		self.loans_df = self.loans_df.rename(columns = {"customer_ID"  : "customer_id"})
	# 		self.loans_df = self.loans_df.rename_axis("loan_id").reset_index().astype(str)

	# 		# 3. Fix Datatypes
	# 		self.loans_df["loan_date"] = pd.to_datetime(self.loans_df["loan_date"], dayfirst = True)
	# 		self.loans_df["amount"]    = self.loans_df["amount"].apply(pd.to_numeric)
	# 		self.loans_df["fee"]       = self.loans_df["fee"].apply(pd.to_numeric)

	# 		# logger
	# 		self.mk1.logging.logger.info("(DataLoader.get_loans_dataframe) Loans Data are retrieved sucessfully ✅")
	# 		return self.loans_df

	# 	except Exception as e:
	# 		self.mk1.logging.logger.error("(DataLoader.get_loans_dataframe) Loans Data retrieval failed : {}".format(e))
	# 		raise e



	# def get_loans_objects(self):
	# 	""" Iterate over all customer key, values and create a list of loans objects"""
	# 	for _, row in self.loans_df.iterrows():


	# 		try : 
	# 			loan = Loan(
	# 					id     = row["loan_id"],
	# 					date   = row["loan_date"],
	# 					amount = float(row["amount"]),
	# 					term   = Term(row["term"]),
	# 					fee    = float(row["fee"]),
	# 					status = LoanStatus(row["loan_status"])
	# 				   )
	# 			self.loans.append(loan)

	# 			# logger
	# 			self.mk1.logging.logger.info("(DataLoader.get_loans_objects) Loan object was created sucessfully ✅")

	# 		except Exception as e:
	# 			self.mk1.logging.logger.error("(DataLoader.get_loans_objects) Loan object creation failed: {}".format(e))
	# 			raise e


	#*-*-*-*-*-*-*-*-*-*-*-*#
	#          json         #
	#*-*-*-*-*-*-*-*-*-*-*-*#

	def load_data_from_json(self) -> pd.DataFrame: 


		try:
			with open(self.data_json_path, "r") as fn:
				entries = fn.read()
			entries = ujson.loads(entries)["data"]
			data_df = pd.DataFrame.from_dict(entries)
			# logger
			self.mk1.logging.logger.info("(DataLoader.load_data) Data loaded sucessfully ✅")
			return data_df
		except Exception as e:
			self.mk1.logging.logger.error("(DataLoader.load_data) Data loading failed. File name was mistype : {}".format(e))
			raise e


	#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#
	#       Dataset : Local DB      #
	#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#


	def serialize_data(self, db : List[Customer]) -> Dict[str, Any] : 
		customers_l = []
		loans_l     = []

		for customer in db :
			loans_l       += self.serialize_loans(customer)
			customers_l   += [ self.serialize_customer(customer) ]
			
			
		return (customers_l, loans_l)


	def serialize_customer(self, customer : Customer) -> Dict[str, Any] : 
		customer_dict = vars(customer)
		customer_dict["customer_id"] = customer_dict.pop("id")
		del customer_dict["loans"]
		
		return customer_dict


	def serialize_loans(self, customer : Customer) :
		loans_list = [] 
		customer_dict = vars(customer)
		for loan_id, loan in enumerate(customer_dict["loans"]) :
			loan_dict = self.serialize_loan(loan, customer_dict["id"], customer_dict["annual_income"])
			loan_dict["loan_id"] = loan_dict.pop("id")
			loans_list.append(loan_dict)

		return loans_list

	def serialize_loan(self, loan : Loan, customer_id : str, annual_income : float) : 
		loan_dict = vars(loan)
		loan_dict["customer_id"]   = str(customer_id)
		loan_dict["loan_date"]     = loan_dict["loan_date"].strftime('%m/%d/%Y')
		loan_dict["term"]          = loan_dict["term"].value
		loan_dict["loan_status"]   = loan_dict["loan_status"].value

		return loan_dict


	def clear_local_db(self, db_name : str, pk : str ) : 

		ids = self.mk1.dataset.db_query(query_str = f"SELECT {pk} FROM {db_name}")[pk].values

		for id in ids : 

			try : 
				self.mk1.dataset.db_delete(table_name = f"{db_name}", filters_dict = {f"{pk}": id})
				self.mk1.logging.logger.info("(test_api.clear_local_db) Object (id = {}) deleted from db named '{}' sucessfully ✅".format(id, db_name))

			except Exception as e:
				self.mk1.logging.logger.error("(test_api.clear_local_db) Object (id = {}) deletion from local db named '{}' failed {}".format(id, db_name, e))
				raise e


	def push_data_to_local_db(self, db_name : str, data :  List[Dict[str, Any]]) : 

		for d_dict in data : 
			self.mk1.dataset.db_append_row(table_name = db_name, input_dict = d_dict)
		

	def load_data_from_local_db(self, db_name : str ) -> pd.DataFrame:
		return self.mk1.dataset.db_query(query_str = f"SELECT * FROM {db_name}")


	def check_if_local_db_empty(self, db_name : str) -> bool: 

		if db_name in self.mk1.dataset.get_tables() : 

			query_response = self.mk1.dataset.db_query(query_str = f"SELECT count(*) FROM {db_name}")
			num_rows       = query_response.iloc[0].values[0]
			
			if num_rows > 0 :
				return False 

		return True

	def create_local_db(self, db_name : str, pk_name : str,  pk_str : str) :
		self.mk1.dataset.db_create_table(table_name = db_name, pk_name = pk_name, pk_str = pk_str)
	 
	def delete_local_db(self, db_name : str ) :
		self.mk1.dataset.db_delete_table(table_name = db_name)



	#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#
	#            General            #
	#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#

	def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame] : 

		if not self.check_if_local_db_empty("customers") : 
			customers_df = self.load_data_from_local_db(db_name = "customers") 
			loans_df     = self.load_data_from_local_db(db_name = "loans") 

		else :
			data_df                = self.load_data_from_json()
			customers_df, loans_df = self.split_dataframes(data_df)

		return (customers_df, loans_df)


	def preprocess_data(self, customers_df : pd.DataFrame, loans_df : pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame] : 

		if self.check_if_local_db_empty("customers") : 
			customers_df = self.preprocess_customers_dataframe(customers_df)
			loans_df     = self.preprocess_loans_dataframe(loans_df)
			
		return (customers_df, loans_df) 

	
