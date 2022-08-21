import os
import json
import dataset
import numpy as np
import pandas as pd
from datetime import datetime

import logging
import logging.handlers as handlers
from typing import Callable, Dict, Generic, Optional, Set, Tuple, TypeVar, Deque, List


from src.config import Config



######################################################################################################

class MkI(object):
    """Builds the Singleton interface for all the contemplated features (treated as attributes)"""
    instance = None

    def __init__(self):
        pass

    @staticmethod
    def get_instance(**kwargs):
        if not MkI.instance:
            MkI.instance = MkI.__MkI(**kwargs)
        return MkI.instance

    class __MkI:
        def __init__(self, **kwargs):
            self.config  = self.get_config() # default: config_path="./config.ini"
            self.dataset = self.get_dataset() if kwargs.get("_dataset", False) else None
            self.logging = self.get_logging() if kwargs.get("_logging", False) else None

        # Initialize Methods
        def get_config(self):
            return Config().parser
        def get_dataset(self):
            return DataSet(self.config)
        def get_logging(self):
            return Logging(self.config)


######################################################################################################

class Logging(object):
    """Logging provides a flexible event logging system for applications and libraries"""
    def __init__(self, config_obj):
        self.config    = config_obj
        self.level     = self.config.get("logger","level")
        self.formatter = self.set_formatter()
        self.handler   = self.set_handler()
        self.logger    = self.start_logger()

    def set_formatter(self):
        """Instantiates the Formatter class and sets the messages/dates formats

           :param: None
           :returns: Formatter class instance with format from "self.format"
        """
        return logging.Formatter(fmt = self.config.get("logger","format"),
                                 datefmt = self.config.get("logger","asctime"))

    def set_handler(self):
        """Instantiates the FileHandler class, sets it as a handler, sets its level and receives the 
        Formatter instance ("self.formatter")

           :param: None
           :returns: FileHandler class instance with "self.formatter" as formatter
        """
        # Creating a handler
        handler = logging.FileHandler(os.path.join(self.config.get("logger","log_path"),
                                                   self.config.get("logger","log_file")))
        # Adding the formatter to the handler
        handler.setFormatter(self.formatter)
        return handler

    def start_logger(self):
        """Instantiates a logger and receives a handler("self.handler")

           :param:   None
           :returns: Customized logger class with a INFO message to states the beginning of a session
        """
        # Creating and storing a new logger
        logger = logging.getLogger(self.config.get("logger","log_name"))
        # Setting the level on the handler
        logger.setLevel(self.level)
        # Adding the handler to "my_logger"
        logger.addHandler(self.handler)
        # Starting the session
        logger.info("---------------------------------- {} Started".format(self.config.get("app","app_name")))
        return logger


######################################################################################################

class DataSet(object):
    """Dataset provides a simple abstraction layer that removes most direct SQL statements without the
       necessity for a full ORM model - essentially, databases can be used like a JSON file
    """
    def __init__(self, config_obj):
        self.config = config_obj
        self.db = self.db_connect()

    def auto_search(self):
        """Searches for ".db" files within folders in this file's root directory

           :param: None
           :returns: dictionary with database's path/name (.db extension)
        """
        db_dict = {"path": None, "name": None}
        # "os.walk" on this file's root folder (./)
        for root, dirs, files in os.walk("./"):
            # Loop files
            for file in files:
                # Check for ".db" files
                if file.endswith(".db"):
                    db_dict["path"], db_dict["name"] = root, file
        return db_dict

    def auto_update(self, db_dict):
        """Updates the database's path/name, found with "auto_search()", in the "config.ini" params

           :param: dict db_dict: dictionary with database path/name (.db extension)
           :returns: None
        """
        # Updating the "path"/"name" in "config.ini" file
        self.config.set('db', 'db_path', db_dict["path"])
        self.config.set('db', 'db_file', db_dict["name"])
        # # Writing our configuration file to 'example.ini'
        # with open("./config.ini", 'w') as config_file:
        #     self.config.write(config_file)
        return None

    def db_connect(self):
        """Connects to an existing database or creates a new database from "config.ini" params

           :param: None
           :returns: dataset database object
        """
        # Searching an existing database
        db_info = self.auto_search()
        # If database already exists...
        if db_info["name"] is not None:
            # Connect to existing database
            db_obj = dataset.connect(os.path.join("sqlite:///", db_info["path"], db_info["name"]))

            # Updating the "config.ini" file
            self.auto_update(db_info)
        else:
            # Create new database
            db_obj = dataset.connect(os.path.join("sqlite:///",
                                                  self.config.get("db","db_path"),
                                                     self.config.get("db","db_file")))
            
        return db_obj

    def db_disconnect(self):
        """Disconnects from the database object stored in "self.db"

           :param: None
           :returns: None
        """
        # Disconnecting from the database
        self.db.executable.close()
        return None

    def db_create_table(self, table_name = None, pk_name = None, pk_str = None):
        """Creates a table with name and primary key (with type) in the "self.db" database object

           :param str table_name: name of the table being created
           :param str pk_name: name of the column to be used as primary key

           :returns: None
        """
        try:
            # Creating the table and commiting changes
            self.db.create_table(table_name, primary_id = pk_name, primary_type = self.get_pk_type(pk_str))
            self.db.commit()
        except:
            # Rolling changes back
            self.db.rollback()
        return None

    def db_delete_table(self, table_name = None):
        """Deletes a table (by its name) in the "self.db" database object

           :param str table_name: name of the table being deleted
           :returns: None
        """
        try:
            # Deleting the table and commiting changes
            self.db[table_name].drop()
            self.db.commit()
        except:
            # Rolling changes back
            self.db.rollback()
        return None

    def db_append_row(self, table_name = None, input_dict = None):
        """Appends a single row (through a dictionary) to the "self.db" database object

           :param str table_name: name of the table receiving the row
           :param dict input_dict: dictionary holding data to be appended (keys as columns, values as values)
           :returns: None
        """
        try:
            # Inserting a row (through a dictionary) and commiting changes
            self.db[table_name].insert(input_dict)
            self.db.commit()
        except:
            # Rolling changes back
            self.db.rollback()
        return None

    def db_append_df(self, table_name = None, input_df = None):
        """Appends multiple rows (through a dataframe) to the "self.db" database object

           :param str table_name: name of the table receiving the rows
           :param df input_df: dataframe holding data to be appended (headers as columns, values as values)
           :returns: None
        """
        # Preparing the Dataframe
        df = input_df.to_dict(orient = "records")
        try:
            # Inserting a row (through df) and commiting changes
            self.db[table_name].insert_many(df)
            self.db.commit()
        except:
            # Rolling changes back
            self.db.rollback()
        return None

    def db_update(self, table_name=None, values_dict=None, col_filter=None):
        """Updates all rows filtered by the "col_filter" list with key/values specified by "values_dict"

           :param str table_name: name of the table receiving the data
           :param dict values_dict: dictionary with values for "col_filter" and additional columns to be updated
           :param lst col_filter: list with columns' names used to filter rows to be updated (value must be inputed in "values_dict")
           :returns: None
        """
        try:
            # Updating rows (based on "col_filter" and "values_dict") and commiting changes
            self.db[table_name].update(row = values_dict, keys = col_filter)
            self.db.commit()
        except:
            # Rolling changes back
            self.db.rollback()
        return None

    def db_upsert(self, table_name=None, values_dict=None, col_filter=None):
        """Updates all rows (present in "table_name") filtered by "col_filter" with key/values specified by "values_dict"
           Inserts "values_dict" as a new row, otherwise (columns not mentioned in "values_dict" get None as value)

           :param str table_name: name of the table receiving the data
           :param dict values_dict: dictionary with values for "col_filter" and additional columns to be updated
           :param lst col_filter: list with columns' names used to filter rows to be updated (value must be inputed in "values_dict")
           :returns: None
        """
        try:
            # Updating rows (based on "col_filter" and "values_dict") and commiting changes
            self.db[table_name].upsert(row=values_dict, keys=col_filter)
            self.db.commit()
        except:
            # Rolling changes back
            self.db.rollback()
        return None

    def db_delete(self, table_name = None, filters_dict = None):
        """Deletes rows by filters (conditions are joined with ANDs statements)

           :param str table_name: name of the table losing the data
           :param dict values_dict: dictionary with values for "col_filter" and additional columns to be updated
           :returns: None
        """
        try:
            # Deleting rows (based on "filters_dict") and commiting changes
            self.db[table_name].delete(**filters_dict)
            self.db.commit()
        except:
            # Rolling changes back
            self.db.rollback()
        return None

    def db_query(self, query_str=None):
        """Queries against the "self.db" database object

           :param str query_str: complete query string
           :returns: dataframe with query results
        """
        try:
            # Querying the db and commiting changes
            result = self.db.query(query_str)
            self.db.commit()
            # Pushing "result" to a Dataframe
            df = pd.DataFrame(data=list(result))
            return df
        except:
            # Rolling changes back
            self.db.rollback()
        return None

    def get_pk_type(self, pk_str):
        """Translates pre-defined strings to SQLite data types, used on "db_create_table"s "primary_type" parameter

           :param str pk_type: String representation of data type. Any of:
               - "b_int": for big integers (returns db.types.biginteger)
               - "int": for integers (returns db.types.integer)
               - "s_int": for small integers (returns db.types.smallinteger)
               - "float": for floats (returns db.types.float)
               - "str": for fixed-sized strings (returns db.types.string)
               - "txt": for variable-sized strings (returns db.types.text)
               - "bool": for booleans (returns db.types.boolean)
               - "date": for datetime.date() objects (returns db.types.date)
               - "datetime": for datetime.datetime() objects (returns db.types.datetime)
           :returns: SQLite data type obj
        """
        # Translating "pk_type" into a SQLite data type object
        if pk_str.lower() == "b_int":
            return self.db.types.biginteger
        elif pk_str.lower() == "int":
            return self.db.types.integer
        elif pk_str.lower() == "s_int":
            return self.db.types.smallinteger
        elif pk_str.lower() == "float":
            return self.db.types.float
        elif pk_str.lower() == "str":
            return self.db.types.string
        elif pk_str.lower() == "txt":
            return self.db.types.string
        elif pk_str.lower() == "bool":
            return self.db.types.boolean
        elif pk_str.lower() == "date":
            return self.db.types.date
        elif pk_str.lower() == "datetime":
            return self.db.types.datetime
        else:
            return None

    def get_tables(self):
        """Lists all existing tables in the database

           :param: None
           :returns: list with existing tables' names in the database
        """
        return self.db.tables

    def get_cols(self, table_name = None):
        """Lists all existing columns in a table

           :param str table_name: name of the table containing the columns
           :returns: list with existing columns in "table_name"
        """
        return self.db[table_name].columns

    def get_rows(self, table_name=None):
        """Gets the total rows in a table

           :param str table_name: name of the table containing the rows
           :returns: total rows (integer) in the "table_name"
        """
        return len(self.db[table_name])

    def get_unique(self, table_name=None, col_name=None):
        """Gets unique values for a column in a table

           :param str table_name: name of the table containing the column
           :param str col_name: name of the column to be analyzed
           :returns: list with unique values in "col_name"
        """
        return [list(each.values())[0] for each in self.db[table_name].distinct(col_name)]