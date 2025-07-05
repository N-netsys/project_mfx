import uuid
from pydantic import BaseModel
from datetime import datetime
from ..models.loan import LoanStatus

class LoanProductBase(BaseModel):
    name: str
    interest_rate: float
    max_tenure_months: int

class LoanProductCreate(LoanProductBase):
    pass

class LoanProduct(LoanProductBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    class Config:
        from_attributes = True

class LoanBase(BaseModel):
    amount_requested: float
    tenure_months: int

class LoanCreate(LoanBase):
    loan_product_id: uuid.UUID
    client_id: uuid.UUID # MFI staff must specify the client

class LoanApply(LoanBase):
    loan_product_id: uuid.UUID # Client applies for a specific product

class Loan(LoanBase):
    id: uuid.UUID
    status: LoanStatus
    client_id: uuid.UUID
    loan_product_id: uuid.UUID
    applied_at: datetime
    class Config:
        from_attributes = True