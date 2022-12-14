# Feature Engineering API for ML purposes
The objective of this **project** is to create a simple feature engineering module that generates some features/variables that are useful for further Machine & Deep Learning modeling. The python module (which is dockerized) is called via an API endpoint, returning some features/variables. 11 more endpoints were built to support the functionality



## π TECH STACK

For project the following tech stack, APIs, architecture was used and applied: 

* Pythonβ
* FastAPI β
* Docker Compose β
* Logger β
* Mark1 System Design + Configuration β
* Spreadsheet API (through gspread wrapper) β




## π FILES HIERARCHY

```
api
β   requirements.txt
β   Dockerfile    
β   docker-compose.yml   
β
ββββsrc
β   β    __init__.py
β   β    config.ini
β   β    config.py
β   β    data_loading.py 
β   β    feature_engineering.py
β   β    data_reporting.py 
β   β    main.py
β   β    models.py
β   ββββ markI.py
β
ββββdata
β   β    data.csv
β   ββββ data.json
β  
ββββfeatures
β   β    features_loans.csv
β   ββββ features_customers.csv
β 
ββββdb
β   β    db.db
β   ββββ db.py
β  
ββββconfig
    ββββ gspread
          ββββ service.json
```









## π ENDPOINTS

Please feel free to hit all our endpoints by visiting http://localhost:8000/docs#/. The list of the endpoints is the following

![Alt text](https://github.com/jimmyg1997/ml-feature-engineering-fastapi-docker/blob/main/images/fastapi.png?raw=true "Feature Engineering API")



#### Endpoints for features
* ```[GET] /api/v1/features/{ontology}``` : The basic endpoint which returns all the features generated after applying the feature engineering analysis. The permitted ontologies here are (a) customers (b) loans. In the project requirements we are asked to create the endpoint only for customers, however we expanded our work. This permit us eg. to create a machine learning model that is dedicated to loans analysis, so having features in a loan-based level may be proven useful
* ```[GET] /api/v1/api_status``` : The endpoint which returns {βstatusβ : βUPβ} if both our basic endpoints /api/v1/features/customers  and /api/v1/features/loans return a status code of 200 after being hit

#### Endpoints for loans
* ```[GET] /api/v1/loans/``` : This endpoint is used when we need to fetch the list of loans currently existing
* ```[GET] /api/v1/loans/{loand_id}``` : This endpoint is used when we need to fetch a specific loan currently existing
* ```[POST] /api/v1/loans/``` : This endpoint can be used to register a new loan (for a specific customer)
* ```[DELETE]  /api/v1/loans/{loan_id}``` : This endpoint can be used to delete a specific loan

#### Endpoints for customers
* ```[GET] /api/v1/customers/``` : This endpoint is used when we need to fetch the list of customers currently existing
* ```[GET] /api/v1/customers/{customer_id}``` : This endpoint is used when we need to fetch a specific customer currently existing
* ```[POST] /api/v1/customers/``` : This endpoint can be used to register a new customer
* ```[DELETE]  /api/v1/customers/{customer_id}``` : This endpoint can be used to delete a specific customer


#### Endpoints for the local db
* ```[GET] /api/v1/database``` : Fetches the list of customers defined in the ./db/optasia_db.py file, creates local dbs, serialises the data and pushes them into these 2 new data tables (of the same ./db/optasia_db.db database)
* ```[POST] /api/v1/database/{db_name}``` : This endpoint is used to clear (recreate an empty data table) for a specific datatable options are (customers, loans) 





## 1οΈβ£ UNIT TESTING

In order for the unit testing to be successful we moved from a 

* *json loading* logic to a dual 
* *json loading* and *local db loading* logic, so that the code is not hard coded only for the provided given data. 


Therefore, during the unit testing (all the tests can be found under **/tests/test_api.py**) we can now create *customer* and *loan* objects that are properly pushed to a local db (2 respective data tables). All the endpoints retrieve the necessary data from the local db (which is smoothly and systematically updated), except for the **[POST] /api/v1/features/{ontology}** endpoint (which works smoothly for both *json* and *local db* cases)





## π SPREADSHEET

In the spreadsheet [Feature Engineering API Reporter](https://docs.google.com/spreadsheets/d/1iIBuignJj5oPW7NDRlirenACJuEEeV2RZOi5X9NSH7A/edit#gid=822346508) several tabs can be found and all are split into 2 clusters

* *api analysis tabs* (1) `customers_features` (2) `loans_features` in which the features generated by the feature engineering process are pushed here
* *custom analysis tabs* : Firstly, we can push (manually, or automatically) data to the following tabs : (1) `customers_raw` and (2) `loans_raw` tabs. Then we calculated some statistics (normal distribution) for some of the features at (3) `customers_statistics` and (4) `loans_statistics` tabs and finally we gathered all the visualisations under the tab called `visualisations` for further inspection. This approach is considered scalable and is useful when tech people should provide business insights to their stakeholders.




## π RECOMMENDED USAGE

####  Setup Python Virtual Environment
1. apt-get update
2. sudo apt install python3-pip
3. download the [installer](https://docs.conda.io/en/latest/miniconda.html#linux-installers) for your python version 
(run "python -V" or "python3 -V" to see your version)
4. run the installer and follow instructions
5. source ~/.bashrc #or restart shell
6. conda install python=3.8
7. conda create --name featengapi python=3.8
8. conda activate featengapi

#### Export PYTHONPATH  
export PYTHONPATH="${PYTHONPATH}:/path/to/your/project/"

#### Deploy with docker compose
Execute the command 

```$ docker-compose up --build```

After the application starts, navigate to http://localhost:8000 in your web browser and you should see the following json response:

```
{
"Hello": "World"
}
```


#### Hit the Endpoints
Visit http://localhost:8000/docs#/.


1. Hit endpoint ```[POST] /api/v1/database/customers```  with arguments (customers, customer_id) to flush the local db βcustomersβ 
2. Hit endpoint ```[POST] /api/v1/database/loans```  with arguments (loans, loan_id) to flush the local db βloansβ 
3. Hit endpoint ```[GET] /api/v1/api_status``` to validate that both [GET] /api/v1/features/customers and [GET] /api/v1/features/loans are running smoothly 
4. Hit endpoint ```[GET] /api/v1/features/customers``` to retrieve the features of customers in json format 
5. Hit endpoint ```[GET] /api/v1/features/loans``` to retrieve the features in json format 
8. Hit endpoint ```[POST] /api/v1/features/customers``` to upload the customers features on the Optasia API Reporter 
9. Hit endpoint ```[POST] /api/v1/features/loans``` to upload the loans features on the Optasia API Reporter 


#### Stop and remove the containers 

```$ docker-compose down```


## π? FUTURE WORK 

Feature Work would be 

* To build more endpoints
* To extract more **features** manually
* To build **baseline machine learning models** and extract **feature importances* (eg. through the use of the LIME algorithm)
* To optimise **machine learning models* by experimenting (by properly storing the experiment configurations and results eg. Spreadsheet)
* To optimise **deep learning models** 
