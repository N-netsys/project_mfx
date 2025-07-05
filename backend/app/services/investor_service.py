"""
Service for managing investors, funds, and their capital contributions.
"""
from sqlalchemy.orm import Session
import uuid
from .. import models, schemas

def create_investor(db: Session, investor_in: schemas.investor.InvestorCreate, tenant_id: uuid.UUID):
    db_investor = models.investor.Investor(**investor_in.dict(), tenant_id=tenant_id)
    db.add(db_investor)
    db.commit()
    db.refresh(db_investor)
    return db_investor

# ... other functions for managing funds and investments