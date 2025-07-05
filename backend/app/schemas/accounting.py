from pydantic import BaseModel

class TrialBalanceEntry(BaseModel):
    account_code: str
    account_name: str
    total_debits: float
    total_credits: float