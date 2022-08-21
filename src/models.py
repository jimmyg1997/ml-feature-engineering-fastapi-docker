import datetime as dt

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from enum import Enum


class LoanStatus(str, Enum) : 
	paid = "0"
	not_paid = "1"

class Term(str, Enum) : 
	long = "long"
	short = "short"



class Loan(BaseModel) : 
	id            : int
	loan_date     : dt.datetime
	amount        : float
	term          : Term
	fee           : float
	loan_status   : LoanStatus


class Customer(BaseModel):
	id            : int
	annual_income : float
	loans         : Optional[List[Loan]]


class CustomerUpdateRequest(BaseModel):
	annual_income : Optional[float]
	loans         : Optional[List[Loan]]


	


