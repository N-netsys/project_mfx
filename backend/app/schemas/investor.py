# backend/app/schemas/investor.py

import uuid
from pydantic import BaseModel, EmailStr

class InvestorBase(BaseModel):
    name: str
    email: EmailStr | None = None

class InvestorCreate(InvestorBase):
    pass

class Investor(InvestorBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    
    class Config:
        from_attributes = True

# You would add schemas for Fund and Investment here as well