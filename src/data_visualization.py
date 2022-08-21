import os
import json
import numpy        as np
import pandas       as pd
import featuretools as ft
import datetime     as dt
from typing           import Callable, Dict, Generic, Optional, Set, Tuple, TypeVar, Deque, List
from IPython.display  import display


# Project modules
from config         import Config
from data_loading   import DataLoader
from data_reporting import DataReporter





class Visualization(object) : 
	def __init__(self, ):
		"""	
			Notes
			------
			[1] First, we specify a dictionary with all the DataFrames in our dataset. 
				The DataFrames are passed in with their index column and time index column 
				if one exists for the DataFrame.

			[2] Second, we specify how the DataFrames are related.
		"""

		# visualizations
		self.visualization_dir  = str(config.get("google_sheets","optasia_reporter_spreadsheet_id"))
	

	def barplot(self, ) :
		"""
			* Status <> Amount (is it unpaid because it is too much?)
		    * Status <> Term (is it unpaid because it is long ?)
		    * Days unpaid <> Amount (how many days have passed being unpaid?  Is it unpaid because it is hig amount)
		    * Days unpaid <> Term (how many days have passed being unpaid?  Is it unpaid because it is long)
		    * Fee percetange <> days

		"""


