import os
import json
import numpy        as np
import pandas       as pd
import featuretools as ft
import datetime     as dt
from typing           import Callable, Dict, Generic, Optional, Set, Tuple, TypeVar, Deque, List
from IPython.display  import display
from collections      import defaultdict


# Project modules
from src.markI          import MkI
from src.config         import Config
from src.data_loading   import DataLoader
from src.data_reporting import DataReporter




class FeatureEngineer(object) : 
	def __init__(self, mk1 : MkI, config : Config):
		# system design
		self.mk1    = mk1
		self.config = config

		# optasia features
		self.features_dir   = str(config.get("features","features_dir"))
		self.features_paths = { 
			"features_customers"  : str(config.get("features","features_customers_path")),
			"features_loans"      : str(config.get("features","features_loans_path")),
		}	

		self.dataframes     = defaultdict(set)
		self.relationships  = []
		self.feature_matrix = None
		self.features_defs  = None



	#*-*-*-*-*-*-*-*-*-*-*-*-*-*#
	#          Utilities        #
	#*-*-*-*-*-*-*-*-*-*-*-*-*-*#

	def store_features(self, 
					   features_df : pd.DataFrame, 
					   fn_path     : str = "./features/features.csv"
					   ) :
		"""
			:param: `type` - It can be either (json, csv)
		""" 
		try : 

			fn_type = fn_path.split(".")[-1]

			if fn_type == "json" :  
				features_df.to_json(fn_path)

			elif fn_type == "csv" : 
				features_df.to_csv(fn_path)

			#logger
			self.mk1.logging.logger.info("(FeatureEngineer.store_features) Features were sucessfully saved as a {} file ✅".format(fn_type))

		except Exception as e:
			self.mk1.logging.logger.error("(FeatureEngineer.store_features) Features file saving failed : {}".format(e))
			raise e

		return 


	#*-*-*-*-*-*-*-*-*-*-*-*#
	#      featuretools     #
	#*-*-*-*-*-*-*-*-*-*-*-*#

	def add_dataframe(self, 
					  df_name : str, 
					  df      : pd.DataFrame, 
					  pk      : str) :
		"""
			First, we specify a dictionary with all the DataFrames in our dataset. 
			The DataFrames are passed in with their index column and time index column 
			if one exists for the DataFrame.

			:param: `pk` - primary key
		"""
		try : 

			self.dataframes[df_name] = (df, pk)
			#logger
			self.mk1.logging.logger.info("(FeatureEngineer.add_dataframe) Dataframe was sucessfully added to the dictionary of dataframes ✅")

		except Exception as e:
			self.mk1.logging.logger.error("(FeatureEngineer.add_dataframe) Dataframe adding to the dict of dataframess failed : {}".format(e))
			raise e


	def add_relationship(self, 
						 parent_dataframe : str, 
						 parent_column    : str, 
						 child_dataframe  : str, 
						 child_column     : str) -> None :

		try :

			rel = (parent_dataframe, parent_column, child_dataframe, child_column) 
			self.relationships.append(rel)
			#logger
			self.mk1.logging.logger.info("(FeatureEngineer.add_relationship) The tuple indicating the relationship between 2 dataframes was sucessfully added to the list of relationshipss ✅")

		except Exception as e:
			self.mk1.logging.logger.error("(FeatureEngineer.add_relationship) The relationship tuple was not added. Failure  : {}".format(e))
			raise e


	# def clean_feature_matrix(self, feature_matrix):
	# 	feature_matrix = feature_matrix.fillna(0.0)
	# 	return feature_matrix


	def run_dfs(self, target_name : str = "customers") :
		"""
			A minimal input to DFS is a dictionary of DataFrames, a list of relationships, and 
			the name of the target DataFrame whose features we want to calculate. The ouput of 
			DFS is a feature matrix and the corresponding list of feature definitions.
		"""

		try :


			feature_matrix, features_defs = ft.dfs(
			    dataframes            = self.dataframes,
			    relationships         = self.relationships,
			    target_dataframe_name = target_name,
			)

			#logger
			self.mk1.logging.logger.info("(FeatureEngineer.run_dfs) DFS was sucessfully executed for all dataframes and relationships ✅")
			return (feature_matrix, features_defs)

		except Exception as e:
			self.mk1.logging.logger.error("(FeatureEngineer.run_dfs) DFS execution failed  : {}".format(e))
			raise e


	def describe_feature(self, feature_idx : int) : 

		feature = self.features_defs[feature_idx]
		display(ft.describe_feature(feature))
		ft.graph_feature(feature)


	#*-*-*-*-*-*-*-*-*-*-*-*-*-*#
	#     Manual Extraction     #
	#*-*-*-*-*-*-*-*-*-*-*-*-*-*#

	def extract_days(self, row) :

		return (dt.datetime.now() - row["loan_date"]).days



	def extract_features_loans(self, loans_df : pd.DataFrame):

		try : 

			loans_df["fee_pct"]      = loans_df["fee"] / loans_df["amount"] 
			loans_df["total_amount"] = loans_df["amount"] + loans_df["fee"] 
			loans_df["days"]         = loans_df.apply(lambda x : self.extract_days(x), axis = 1) 
			#logger
			self.mk1.logging.logger.info("(FeatureEngineer.extract_features_loans) Manual extraction of features for the loans dataframe was successful ✅")
			return loans_df

		except Exception as e:
			self.mk1.logging.logger.error("(FeatureEngineer.extract_features_loans) Manual extraction of features for the loans dataframe failed  : {}".format(e))
			raise e


	def extract_features_customers(self, customers_df : pd.DataFrame) : 

		# 1. `annual income` binning
		min_value = float(customers_df["annual_income"].min())
		max_value = float(customers_df["annual_income"].max())
		bins      = np.linspace(min_value, max_value, 6)
		labels    = ['very low', 'low', 'middle', 'high', 'very high']
		customers_df['annual_income_bins'] = pd.cut(customers_df['annual_income'], bins = bins, labels = labels, include_lowest = True)


		return customers_df




	#*-*-*-*-*-*-*-*-*-*-*-*-*-*#
	#     Combine Features      #
	#*-*-*-*-*-*-*-*-*-*-*-*-*-*#

	def combine_features(self, 
						 df1 : pd.DataFrame, 
						 df2 : pd.DataFrame,
						 pk  : str,
						 ) : 

		"""Merge Features from both processes (featuretools, manual extraction)"""
		try : 
			cols        = df2.columns.difference(df1.columns)
			features_df = pd.merge(df1, df2[cols], on = [pk])
			#logger
			self.mk1.logging.logger.info("(FeatureEngineer.combine_features) Merging of 2 different features dataframes was successful ✅")
			return features_df

		except Exception as e:
			self.mk1.logging.logger.error("(FeatureEngineer.combine_features) Merging of 2 different features dataframes failed  : {}".format(e))
			raise e

		return features_df


	def delete_features(self,
						features_df : pd.DataFrame, 
						fts         : List[str]) :
		"""Delete Features that are not useful"""
		try : 
			features_df = features_df.drop(fts, axis = 1)
			self.mk1.logging.logger.info("(FeatureEngineer.delete_features) # {} features were deleted successfully ✅".format(len(fts)))
			return features_df

		except Exception as e:
			self.mk1.logging.logger.error("(FeatureEngineer.delete_features) Deleting # {} features failed  : {}".format(len(fts), e))
			raise e



	#*-*-*-*-*-*-*-*-*-*-*-*-*-*#
	#     Feature Importance    #
	#*-*-*-*-*-*-*-*-*-*-*-*-*-*#





if __name__ == "__main__":

	mk1    = MkI.get_instance(_logging = True)
	config = Config().parser


	# Data Loading
	data_loader = DataLoader(mk1, config)
	data_loader.load_data()
	customers_df = data_loader.get_customers_dataframe()
	loans_df     = data_loader.get_loans_dataframe()

	# ------------------- #


	# Feature Engineering
	## 1. Extract features for both loans and customers
	feature_engineer = FeatureEngineer(mk1, config)
	loans_df         = feature_engineer.extract_features_loans(loans_df)
	customers_df     = feature_engineer.extract_features_customers(customers_df)
	

	## 2. Create feature tools (dataframes, relationships)
	feature_engineer.add_dataframe("customers", customers_df, "customer_id")
	feature_engineer.add_dataframe("loans", loans_df, "loan_id")
	feature_engineer.add_relationship("customers", "customer_id", "loans", "customer_id")
	

	## 3. Use "featuretools" to extract extra feature
	loans_features_df, _     = feature_engineer.run_dfs(target_name = "loans")
	customers_features_df, _ = feature_engineer.run_dfs(target_name = "customers")
	
	## 4. Store features as ".csv" file
	feature_engineer.store_features(
			features_df = loans_features_df,
			fn_path     = self.features_paths["features_loans"]
	)

	feature_engineer.store_features(
			features_df = customers_features_df,
			fn_path     = self.features_paths["features_customers"]
	)


	# ------------------- #

	# Data Reporting
	data_reporter         = DataReporter(mk1, config)
	loans_features_df     = data_reporter.cast_to_spreadsheet_friendly_format(loans_features_df)
	customers_features_df = data_reporter.cast_to_spreadsheet_friendly_format(customers_features_df)


	data_reporter.write_to_spreadsheet(
	   df          = loans_features_df,
	   tab_name    = data_reporter.optiasia_reporter_tabs["loans_features"],
	   has_index   = False,
	   has_headers = True
	)


	data_reporter.write_to_spreadsheet(
	   df          = customers_features_df,
	   tab_name    = data_reporter.optiasia_reporter_tabs["customers_features"],
	   has_index   = False,
	   has_headers = True
	)




