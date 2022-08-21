# Feature Engineering API for ML purposes
The objective of this prohcet is to create a simpl feature engineering module that generates some features/variables that are useful for modeling. The python module (which is dockerized) is called via an API endpoint, returning some features/variables. 11 more endpoints were built to support the functionality



## TECH STACK

For project the following tech stack, APIs, architecture was used and applied: 

* Python✅
* FastAPI ✅
* Docker Compose ✅
* Logger ✅
* Mark1 System Design + Configuration ✅
* Spreadsheet API (through gspread wrapper) ✅




## FILES HIERARCHY



The files are organised as following

requirements.txt  : All the requirements that should (and they are) after the project is deployed through docker. 
Dockerfile :  The simple text file that contains the commands a user could call to assemble an image
docker-compose.yml : Docker Compose defines the services that make up your app in docker-compose.yml. In our case the only app we host is the “api” (the name we gave for the process)
data/
cvas_data.csv 
cvas_data.json : we used this for our feature engineering analysis
config/
gspread/
service-optasia.json : It used by the spread wrapper to connect at the Optasia API Reporter and push data
features/ : Initially is empty. If the endpoint [GET] /api/v1/features/{ontology}  is hit this folder will store the “.csv” files of the features
features_loans.csv
features_customers.csv
logs/ : Initially is empty. It stores all the logs for the feature engineering process when the proper endpoints are hit
optasia_logs.logs
tests/
test_api.py : All the 12 unit tests are under this file. Here we retrieve the initial db which is under the folder ./db/optasia_db.py and then we hit our endpoints for customers and loans (register, fetch, delete). Finally we test the most important endpoints concerning the (1) features and th(2) uploading to spreadsheet process
db/
optasia_db.py / This is used for the Unit testing. It has a List of Customer objects
optasia_db.db / This is a local database in which the data tables `customers` and `loans` will be stored.
src/
__init__.py
config.ini : It stores all the variables that will be parsed by the Config object of the module ‘config.py’
config.py : The parser of the 'config.ini' file. 
data_loading.py : It contains the class “DataLoader” it is used to fetch all the data, split them into 2 different ontologies of data frames (customers, loans) and also create the proper objects (as defined in the module ‘models.py’). There are 2 different fetching data options (1) Retrieve data from a local db (2) Retrieve data from a json file.
feature_engineering.py : This is the most useful python file of the project and contains the class “FeatureEngineer”. It used to (1) extract manual features (2) and automatic features through the ‘feature tools’ library for both ontologies (customers, loans). Finally the features data are properly stored :
data_reporting.py : This is used as a customized wrapper , which uses the library ‘gspread’ to properly communicate with the spreadsheet Optasia API Reporter . We can use it to push data (raw, features) into the reporter
data_visualization.py : 
main.py : The main REST API module. The tech stack preferred here was fastAPI eventually as indicated at the instructions of the project
markI.py : The word mark, followed by number, is a method of designating a version of a product. It is often abbreviated as Mk or M. Here we have a first MVP of the API so the number notation is “I” or 1
models.py : All the respective classes for our ontologies (Customer, Loan etc)






## ENDPOINTS

Please feel free to hit all our endpoints by visiting http://localhost:8000/docs#/. The list of the endpoints is the following


#### Endpoints for features
* ```[GET] /api/v1/features/{ontology}``` : The basic endpoint which returns all the features generated after applying the feature engineering analysis. The permitted ontologies here are (a) customers (b) loans. In the project requirements we are asked to create the endpoint only for customers, however we expanded our work. This permit us eg. to create a machine learning model that is dedicated to loans analysis, so having features in a loan-based level may be proven useful
* **[GET] /api/v1/api_status** : The endpoint which returns {“status” : “UP”} if both our basic endpoints /api/v1/features/customers  and /api/v1/features/loans return a status code of 200 after being hit

#### Endpoints for loans
* [GET] /api/v1/loans/ : This endpoint is used when we need to fetch the list of loans currently existing
* [GET] /api/v1/loans/{loand_id} : This endpoint is used when we need to fetch a specific loan currently existing
* [POST] /api/v1/loans/ : This endpoint can be used to register a new loan (for a specific customer)
* [DELETE]  /api/v1/loans/{loan_id} : This endpoint can be used to delete a specific loan

#### Endpoints for customers
* [GET] /api/v1/customers/ : This endpoint is used when we need to fetch the list of customers currently existing
* [GET] /api/v1/customers/{customer_id} : This endpoint is used when we need to fetch a specific customer currently existing
* [POST] /api/v1/customers/ : This endpoint can be used to register a new customer
* [DELETE]  /api/v1/customers/{customer_id} : This endpoint can be used to delete a specific customer


#### Endpoints for the local db
* [GET] /api/v1/database : Fetches the list of customers defined in the ./db/optasia_db.py file, creates local dbs, serialises the data and pushes them into these 2 new data tables (of the same ./db/optasia_db.db database)
* [POST] /api/v1/database/{db_name} : This endpoint is used to clear (recreate an empty data table) for a specific datatable options are (customers, loans) 





## UNIT TESTING

In order for the unit testing to be successful I had to move from a 

* *json loading* logic to a dual 
* *json loading* and “local db loading” logic, so that the code is not hard coded only for our given data. 


Therefore, now with the unit testing (all the tests can be found under **/tests/test_api.py**) we can create *customer* and *loan* objects that are properly pushed to a local db. All the endpoints retrieve the necessary data from the local db (which is smoothly and systematically updated), except for the **[POST] /api/v1/features/{ontology}** endpoint (which works smoothly for both json and local db cases)





## SPREADSHEET

In the spreadsheet Optasia API Reporter several tabs can be found and all are split into 2 clusters

* *api analysis tabs* (1) `customers_features` (2) `loans_features` in which the features generated by the feature engineering process are pushed here
* *custom analysis tabs* : We first manually inserted all data at (1) `customers_raw` and (2) `loans_raw` tabs. Then we calculated some statistics (normal distribution) for some of the features at (3) `customers_statistics` and (4) `loans_statistics` and finally we gathered all the visualisations under the tab called `visualisations` for further inspection. This is very scalable and this is the reason it was built as a tool. 




## RECOMMENDED USAGE

#### step #1
Execute the command 

```docker-compose up --build```


#### step #2
Visit http://localhost:8000/docs#/.


1. Hit endpoint ```[POST] /api/v1/database/customers```  with arguments (customers, customer_id) to flush the local db “customers” 
2. Hit endpoint ```[POST] /api/v1/database/loans```  with arguments (loans, loan_id) to flush the local db “loans” 
3. Hit endpoint ```[GET] /api/v1/api_status``` to validate that both [GET] /api/v1/features/customers and [GET] /api/v1/features/loans are running smoothly 
4. Hit endpoint ```[GET] /api/v1/features/customers``` to retrieve the features of customers in json format 
5. Hit endpoint ```[GET] /api/v1/features/loans``` to retrieve the features in json format 
8. Hit endpoint ```[POST] /api/v1/features/customers``` to upload the customers features on the Optasia API Reporter 
9. Hit endpoint ```[POST] /api/v1/features/loans``` to upload the loans features on the Optasia API Reporter 
```



## FEATURE WORK 

Feature Work would be 

* To build more endpoints
* To extract more features manually
* To build baseline machine learning models and extracts feature importances (through the use of the LIME algorithm)
* To optimise machine learning models by experimenting (and also saving the experiment configurations and results properly eg. Spreadsheet)
* To optimise deep learning models (maybe it is not required in our case the we only have 100 samples of customers) 
