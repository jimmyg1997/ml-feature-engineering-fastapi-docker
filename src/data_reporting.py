"""
    [*] Description : Google Sheets API reporting
    [*] Author      : dgeorgiou3@gmail.com
    [*] Date        : Aug, 2022
    [*] Links       :  
"""

import os.path
import warnings
import gspread
import ujson
import argparse
import numpy    as np 
import pandas   as pd 
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.cm     as cm
import seaborn           as sns

from IPython.display     import display
from tqdm                import tqdm
from collections         import defaultdict
from typing              import Any, List, Dict

# Project modules
from src.config       import Config
from src.markI        import MkI
from src.data_loading import DataLoader

class DataReporter(object) : 

	def __init__(self,  mk1 : MkI, config : Config):
		"""
			* overview
			* customers
			* loans
			* visualizations (basics from customers, loans)
		"""
		# system design
		self.mk1    = mk1
		self.config = config

		# google sheets api
		self.service_token_path = str(config.get("google_sheets_api","service_token_path"))
		self.google_sheets_api  = gspread.service_account(filename = self.service_token_path)

		
		# google sheets
		self.optasia_reporter_spreadsheet_id = str(config.get("google_sheets","api_reporter_spreadsheet_id"))
		self.tabs = { 
			"customers"          : str(config.get("google_sheets","api_reporter_tab_customers")),
			"loans"              : str(config.get("google_sheets","api_reporter_tab_loans")),
			"overview"           : str(config.get("google_sheets","api_reporter_tab_overview")),
			"customers_features" : str(config.get("google_sheets","api_reporter_tab_customers_features")),
			"loans_features"     : str(config.get("google_sheets","api_reporter_tab_loans_features"))
		
		}	

	#*-*-*-*-*-*-*-*-*-*-*-*-*-*#
	#          Utilities        #
	#*-*-*-*-*-*-*-*-*-*-*-*-*-*#

	def df_to_list(self, 
				   df          : pd.DataFrame, 
				   has_index   : bool = True,
				   has_headers : bool = True) -> List[Any]:

		if has_index :
			index_name = df.index.name
			l = df.reset_index().values.tolist()

			if has_headers:
				l.insert(0, [index_name] + list(df.columns))

		else : 
			l = df.values.tolist()

			if has_headers:
				l.insert(0, list(df.columns))

		return l




	def cast_to_spreadsheet_friendly_format(self, df : pd.DataFrame) :

		datatype_map = df.dtypes.to_dict()


		try : 
			for col in df.columns :
				df[col] = df[col].astype(str) 
			# logger
			self.mk1.logging.logger.info("(DataReporter.cast_to_spreadsheet_friendly_format) Columns casted to string for compatability with Spreadsheets API ✅")

		except Exception as e:
			self.mk1.logging.logger.error("(DataReporter.cast_to_spreadsheet_friendly_format) Columns casting to string failed : {}".format(e))
			raise e
		
		return df



	#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#
	#          HTTP Requests        #
	#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#

	def write_data_overview(self, features):
		"""
			Analytis (per customer)
			* avg loan number
			* avg
		"""

		pass

	def write_to_spreadsheet(self,
							 df          : pd.DataFrame,
							 tab_name    : str  = "customers",
							 has_index   : bool = False,
							 has_headers : bool = False ) : 
		l  = self.df_to_list(df, has_index, has_headers)

		try : 

			spreadsheet = self.google_sheets_api.open_by_key(self.optasia_reporter_spreadsheet_id)
			tab         = spreadsheet.worksheet(self.tabs[tab_name])
			tab.clear()
			tab.append_rows(l, table_range = 'A1')

			#logger
			self.mk1.logging.logger.info("(DataReporter.write_to_spreadsheet) Data uploaded to Spreadsheet successfully ✅")

		except Exception as e:
			self.mk1.logging.logger.error("(DataReporter.write_to_spreadsheet) Data uploading to spreadsheet failed : {}".format(e))
			raise e







