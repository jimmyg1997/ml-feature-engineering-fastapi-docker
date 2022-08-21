import json
from dateutil           import parser
from typing             import Optional, List, Dict, Any
from fastapi.testclient import TestClient
from IPython.display    import display


from src.main         import app
from src.markI        import MkI
from src.config       import Config
from src.data_loading import DataLoader
from src.models       import Customer, LoanStatus, Term, Customer, Loan, CustomerUpdateRequest


client      = TestClient(app)
mk1         = MkI.get_instance(_logging = True, _dataset = True)
config      = Config().parser
data_loader = DataLoader(mk1, config)


def test_create_local_dbs() :
	response = client.get("/api/v1/database") 
	


def test_fetch_customer():
	response = client.get("/api/v1/customers/1090")
	response_dict = json.loads(response.json())
	#response_dict = response.json()

	try :
		assert response.status_code == 200
		assert response_dict[0]["customer_id"]   == '1090'
		assert response_dict[0]["annual_income"] == 41333
		# logger
		mk1.logging.logger.info("(test_api.test_fetch_customer) Endpoint /api/v1/customers/1090 runs sucessfully ✅")

	except Exception as e:
		mk1.logging.logger.error("(test_api.test_fetch_customer) Hitting endpoint /api/v1/customers/1090 failed (status code {}) : {}".format(response.status_code, e))
		raise e



def test_register_customer():
	data = { "customer_id"    : 1423,
			  "annual_income" : 34513
	}

	response = client.post("/api/v1/customers", json.dumps(data))
	response_dict = json.loads(response.json())
	#response_dict = response.json()


	try : 
		assert response.status_code == 200 
		assert response_dict[0]["customer_id"]   == "1423"
		assert response_dict[0]["annual_income"] == 34513
		# logger
		mk1.logging.logger.info("(test_api.test_register_customer) Endpoint /api/v1/customers/ runs sucessfully ✅")

	except Exception as e:
		mk1.logging.logger.error("(test_api.test_register_customer) Hitting endpoint /api/v1/customers/ failed (status code {}) : {}".format(response.status_code, e))
		raise e


def test_delete_customer() : 

	response = client.delete("/api/v1/customers/1090")
	#response_dict = response.json()
	response_dict = json.loads(response.json())

	try :
		assert response.status_code == 200
		assert response_dict        == []
		# logger
		mk1.logging.logger.info("(test_api.test_delete_customer) Endpoint /api/v1/customers/1090 runs sucessfully ✅")

	except Exception as e:
		mk1.logging.logger.error("(test_api.test_delete_customer) Hitting endpoint /api/v1/customers/1090 failed (status code {}) : {}".format(response.status_code, e))
		raise e



#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#
#          Endpoint : Loans         #
#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#

def test_fetch_loan():
	response      = client.get("/api/v1/loans/1")
	#response_dict = response.json()
	response_dict = json.loads(response.json())

	try :
		assert response.status_code == 200
		assert response_dict[0]["loan_id"]     == "1" 
		assert response_dict[0]["loan_date"]   == "11/15/2021"
		assert response_dict[0]["amount"]      == 2426.0
		assert response_dict[0]["term"]        == "long" 
		assert response_dict[0]["fee"]         == 199.0 
		assert response_dict[0]["loan_status"] == "1" 
		assert response_dict[0]["customer_id"] == "1090"
		# logger
		mk1.logging.logger.info("(test_api.test_fetch_loan) Endpoint /api/v1/customers/1090 runs sucessfully ✅")

	except Exception as e:
		mk1.logging.logger.error("(test_api.test_fetch_loan) Hitting endpoint /api/v1/customers/1090 failed (status code {}) : {}".format(response.status_code, e))
		raise e



def test_register_loan():
	data = { 
			      "loan_id"     : 15,
			      "loan_date"   : "08/20/2022",
			      "amount"      : 1000,
			      "term"        : "long",
			      "fee"         : 100,
			      "loan_status" : "0",
			      "customer_id" : 1090
	}

	response = client.post("/api/v1/loans", json.dumps(data))
	#response_dict = response.json()
	response_dict = json.loads(response.json())


	try : 
		assert response.status_code == 200 
		assert response_dict[0]["loan_id"]     == "15"
		assert response_dict[0]["loan_date"]   == "08/20/2022"
		assert response_dict[0]["amount"]      == 1000.0
		assert response_dict[0]["term"]        == "long"
		assert response_dict[0]["fee"]         == 100.0
		assert response_dict[0]["loan_status"] == "0"
		assert response_dict[0]["customer_id"] == "1090"

		# logger
		mk1.logging.logger.info("(test_api.test_register_loan) Endpoint /api/v1/loans for the loan registration was sucessful ✅")

	except Exception as e:
		mk1.logging.logger.error("(test_api.test_register_loan) Hitting endpoint /api/v1/loans for loan registration failed (status code {}) : {}".format(response.status_code, e))
		raise e


def test_delete_loan() : 

	response = client.delete("/api/v1/loans/1")
	#response_dict = response.json()
	response_dict = json.loads(response.json())


	try :
		assert response.status_code == 200
		assert response_dict        == []
		# logger
		mk1.logging.logger.info("(test_api.test_delete_loan) Endpoint /api/v1/loans/15 runs sucessfully ✅")

	except Exception as e:
		mk1.logging.logger.error("(test_api.test_delete_loan) Hitting endpoint /api/v1/loans/15 failed (status code {}) : {}".format(response.status_code, e))
		raise e



#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#
#        Endpoint : Feature Engineering       #
#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#

def test_fetch_features_customers():
	response = client.get("/api/v1/features/customers")
	print(json.dumps(json.loads(response.json()), indent = 4, sort_keys = True))

	try :
		assert response.status_code == 200
		mk1.logging.logger.info("(test_api.test_fetch_customers_features) Endpoint /api/v1/features/customers runs sucessfully ✅")

	except Exception as e:
		mk1.logging.logger.error("(test_api.test_delete_loan) Hitting endpoint /api/v1/features/customers failed (status code {}) : {}".format(response.status_code, e))
		raise e

def test_fetch_features_loans():
	response = client.get("/api/v1/features/loans")
	print(json.dumps(json.loads(response.json()), indent = 4, sort_keys = True))

	try :
		assert response.status_code == 200
		mk1.logging.logger.info("(test_api.test_fetch_customers_features) Endpoint /api/v1/features/customers runs sucessfully ✅")

	except Exception as e:
		mk1.logging.logger.error("(test_api.test_delete_loan) Hitting endpoint /api/v1/features/customers failed (status code {}) : {}".format(response.status_code, e))
		raise e

def test_upload_features_customers():
	response = client.post("/api/v1/features/customers", "customers")

	try :
		assert response.status_code == 200
		mk1.logging.logger.info("(test_api.test_upload_features_customers) Endpoint /api/v1/features/customers for features uploading runs sucessfully ✅")

	except Exception as e:
		mk1.logging.logger.error("(test_api.test_upload_features_customers) Hitting endpoint /api/v1/features/customers for features uploading failed (status code {}) : {}".format(response.status_code, e))
		raise e


def test_upload_features_loans():
	response = client.post("/api/v1/features/loans", "loans")

	try :
		assert response.status_code == 200
		mk1.logging.logger.info("(test_api.test_upload_features_loans) Endpoint /api/v1/features/loans for features uploading runs sucessfully ✅")

	except Exception as e:
		mk1.logging.logger.error("(test_api.test_upload_features_loans) Hitting endpoint /api/v1/features/loans for features uploading failed (status code {}) : {}".format(response.status_code, e))
		raise e


def test_api_status() : 
	response = client.get("/api/v1/api_status")
	response_dict = json.loads(response.json())
	print(response, response_dict, response_dict["status"])

	try :
		assert response.status_code == 200
		assert response_dict["status"] == "UP"
		mk1.logging.logger.info("(test_api.test_api_status) Both endpoints /api/v1/features/loans and /api/v1/features/customers runs sucessfully ✅")

	except Exception as e:
		mk1.logging.logger.error("(test_api.test_api_status) 1 and/or 2 of the endpoints /api/v1/features/loans and /api/v1/features/customers failed (status code {}) : {}".format(response.status_code, e))
		raise e
	



if __name__ == '__main__':
	print("----- Initial Databases")
	test_create_local_dbs()
	test_fetch_customer()
	print("----- Registering Customer")
	test_register_customer()
	display(mk1.dataset.db_query(query_str = "SELECT * FROM customers"))
	test_fetch_loan()
	print("----- Registering Loan")
	test_register_loan()
	display(mk1.dataset.db_query(query_str = "SELECT * FROM loans"))
	print("----- Deleting Customer & Loan")
	test_delete_customer()
	test_delete_loan()
	display(mk1.dataset.db_query(query_str = "SELECT * FROM customers"))
	display(mk1.dataset.db_query(query_str = "SELECT * FROM loans"))

	print("----- Final Merged Datatable")
	display(mk1.dataset.db_query(query_str = "SELECT * FROM customers c INNER JOIN loans l ON l.customer_id = c.customer_id"))


	print("----- Feature Engineering")
	test_fetch_features_customers()
	test_fetch_features_loans()
	test_upload_features_customers()
	test_upload_features_loans()
	#test_api_status()









