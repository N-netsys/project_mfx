import uuid
from pydantic import BaseModel
from datetime import date
from ..models.repayment import RepaymentStatus

class RepaymentRecord(BaseModel):
    schedule_id: uuid.UUID
    amount_paid: float

class RepaymentSchedule(BaseModel):
    id: uuid.UUID
    due_date: date
    amount_due: float
    status: RepaymentStatus
    class Config:
        from_attributes = True