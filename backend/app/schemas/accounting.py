import uuid
from pydantic import BaseModel
from ..models.accounting import AccountType

class TrialBalanceEntry(BaseModel):
    account_code: str
    account_name: str
    total_debits: float
    total_credits: float