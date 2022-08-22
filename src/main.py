import os
import json
import numpy    as np
import pandas   as pd
import datetime as dt
from uuid            import UUID, uuid4
from dateutil        import parser
from typing          import Optional, List, Dict, Any
from IPython.display import display

## API modules
from fastapi            import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
import docker

## Project modules

from src.models              import Customer, LoanStatus, Term, Customer, Loan, CustomerUpdateRequest
from src.markI               import MkI
from src.config              import Config
from src.data_loading        import DataLoader
from src.data_reporting      import DataReporter
from src.feature_engineering import FeatureEngineer

## Testing db
from db.db import db


# client = docker.from_env()
# container = client.containers.run("bfirsh/reticulate-splines", detach=True)
# print(container.id)


app    = FastAPI()
client = TestClient(app)
mk1    = MkI.get_instance(_logging = True, _dataset = True)
config = Config().parser


# db : List[Customer] = []
# @staticmethod
# def insert(db : Session, item : Item) -> None:
# 	db.add(item)
#  	db.commit()
   
 
# @staticmethod
# def update(db : Session, item : Item) -> None:
# 	db.commit()


@app.get("/")
async def root():
	return {"msg" : "Hello World"}



#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#
#        Endpoint : Feature Engineering       #
#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#


@app.get("/api/v1/api_status")
async def fetch_api_status():

	# Check endpoints : "Customers Features", "Loans Features"
	response_customers = client.get("/api/v1/features/customers")
	response_loans     = client.get("/api/v1/features/loans")

	try : 
		assert response_customers.status_code == 200
		assert response_loans.status_code == 200
		return json.dumps({"status" : "UP"})
	except Exception as e:
		return json.dumps({"status" : "DOWN"})



@app.get("/api/v1/features/{ontology}")
async def fetch_features(ontology : str):
	"""Choose the ontology for which features will be fetched {customers, loans}"""

	# Data Loading & Preprocessing
	data_loader  = DataLoader(mk1, config)
	customers_df, loans_df = data_loader.load_data()
	customers_df, loans_df = data_loader.preprocess_data(customers_df, loans_df)
	loans_df               = data_loader.postprocess_loans_dataframe(loans_df)


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
			fn_path     = feature_engineer.features_paths["features_loans"] 
	)

	feature_engineer.store_features(
			features_df = customers_features_df,
			fn_path     = feature_engineer.features_paths["features_customers"]
	)

	## 5. Convert to json format
	customers_features_json = customers_features_df.to_json(orient = "records", indent = 2)
	customers_features_dict = json.loads(customers_features_json)

	loans_features_json = loans_features_df.to_json(orient = "records", indent = 2)
	loans_features_dict = json.loads(loans_features_json)


	jsons = {
		"customers" : customers_features_json,
		"loans"     : loans_features_json
	}

	## 6. Return 
	return jsons[ontology]

@app.post("/api/v1/features/{ontology}")
async def upload_features(ontology : str):

	data_reporter = DataReporter(mk1, config)
	features_path = str(config.get("features",f"features_{ontology}_path"))
	features_tab  = str(config.get("google_sheets", f"api_reporter_tab_{ontology}_features"))
	features_df   = pd.read_csv(features_path, index_col = 0)
	features_df   = data_reporter.cast_to_spreadsheet_friendly_format(features_df)

	data_reporter.write_to_spreadsheet(
	   df          = features_df,
	   tab_name    = features_tab,
	   has_index   = False,
	   has_headers = True
	)


#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#
#        Endpoint : Local DB        #
#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#



@app.post("/api/v1/database/{db_name}")
async def clear_local_db(db_name : str, pk_name : str):
	data_loader  = DataLoader(mk1, config)

	# 1. Delete if existing
	data_loader.delete_local_db(db_name = db_name)

	# 2. Create Local DB
	data_loader.create_local_db(db_name = db_name, pk_name = pk_name, pk_str = "str")



@app.get("/api/v1/database")
async def create_local_dbs():
	data_loader  = DataLoader(mk1, config)

	# 1. Delete if existing
	data_loader.delete_local_db(db_name = "customers")
	data_loader.delete_local_db(db_name = "loans")

	# 2. Create 
	data_loader.create_local_db(db_name = "customers", pk_name = "customer_id", pk_str = "str")
	data_loader.create_local_db(db_name = "loans", pk_name = "loan_id", pk_str = "str")

	# 3. Clear if not empty
	if not data_loader.check_if_local_db_empty(db_name = "customers") : 
		data_loader.clear_local_db(db_name = "customers", pk = "customer_id")

	if not data_loader.check_if_local_db_empty(db_name = "loans") :
		data_loader.clear_local_db(db_name = "loans", pk = "loan_id")


	# 4. Serialize & Push data to both data tables
	customers_l, loans_l = data_loader.serialize_data(db)
	data_loader.push_data_to_local_db(db_name = "customers", data = customers_l)
	data_loader.push_data_to_local_db(db_name = "loans", data = loans_l)


	# 5. Check rows of local dbs
	display(mk1.dataset.db_query(query_str = "SELECT * FROM loans"))
	display(mk1.dataset.db_query(query_str = "SELECT * FROM customers"))


#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#
#        Endpoint : Customers       #
#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#

@app.get("/api/v1/customers")
async def fetch_customers():
	return mk1.dataset.db_query(query_str = "SELECT * FROM customers").to_json(orient = "records", indent = 2)
	


@app.get("/api/v1/customers/{customer_id}")
async def fetch_customer(customer_id : int):
	return mk1.dataset.db_query(query_str = f"SELECT * FROM customers WHERE customer_id == {customer_id}").to_json(orient = "records", indent = 2)



@app.post("/api/v1/customers")
async def register_customer(customer_dict : Dict[str, Any]):
	mk1.dataset.db_append_row(table_name = "customers", input_dict = customer_dict)
	customer_id = customer_dict["customer_id"]
	return mk1.dataset.db_query(query_str = f"SELECT * FROM customers WHERE customer_id == {customer_id}").to_json(orient = "records", indent = 2)
	

@app.delete("/api/v1/customers/{customer_id}")
async def delete_customer(customer_id : int):

	try :
		mk1.dataset.db_delete(table_name = "customers", filters_dict = {"customer_id": customer_id})
		return mk1.dataset.db_query(query_str = f"SELECT * FROM customers WHERE customer_id == {customer_id}").to_json(orient = "records", indent = 2)
	

	except HTTPException : 
		raise HTTPException(
			status_code = 404,
			detail = f"Customer with id : {customer_id} does not exist"
		)



# @app.put("/api/v1/customers/{customer_id}")
# async def update_customer(customer_update : CustomerUpdateRequest, customer_id : int):
# 	for customer in db : 
# 		if customer.id == customer_id:

# 			if customer_update.annual_income is not None : 
# 				customer.annual_income = customer_update.annual_income

# 			if customer_update.loans is not None : 
# 				customer.loans = customer_update.loans

# 			return 

# 		raise HTTPException(
# 			status_code = 404,
# 			detail = f"Customer with id : {customer_id} does not exist"
# 		)


#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#
#          Endpoint : Loans         #
#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#

@app.get("/api/v1/loans")
async def fetch_loans():
	return mk1.dataset.db_query(query_str = "SELECT * FROM loans").to_json(orient = "records", indent = 2)


@app.get("/api/v1/loans/{loan_id}")
async def fetch_loan(loan_id : int):
	return mk1.dataset.db_query(query_str = f"SELECT * FROM loans WHERE loan_id == {loan_id}").to_json(orient = "records", indent = 2)

	
@app.post("/api/v1/loans")
async def register_loan(loan_dict : Dict[str, Any]):
	mk1.dataset.db_append_row(table_name = "loans", input_dict = loan_dict)
	loan_id = loan_dict["loan_id"]
	return mk1.dataset.db_query(query_str = f"SELECT * FROM loans WHERE loan_id == {loan_id}").to_json(orient = "records", indent = 2)
	



@app.delete("/api/v1/loans/{loan_id}")
async def delete_loan(loan_id : int):

	try :
		mk1.dataset.db_delete(table_name = "loans", filters_dict = {"loan_id": loan_id})
		return mk1.dataset.db_query(query_str = f"SELECT * FROM loans WHERE loan_id == {loan_id}").to_json(orient = "records")
	

	except HTTPException : 
		raise HTTPException(
			status_code = 404,
			detail = f"Loan with id : {loan_id} does not exist"
		)









