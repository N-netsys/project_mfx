# backend/app/services/investor_service.py

"""
Service for managing investors, funds, and their capital contributions.
"""
from sqlalchemy.orm import Session
import uuid

# --- CORRECTED: Specific imports ---
from .. import models
from ..schemas import investor as investor_schema

def create_investor(db: Session, investor_in: investor_schema.InvestorCreate, tenant_id: uuid.UUID) -> models.Investor:
    """
    Creates a new Investor record for the given tenant.
    """
    db_investor = models.investor.Investor(**investor_in.dict(), tenant_id=tenant_id)
    db.add(db_investor)
    db.commit()
    db.refresh(db_investor)
    return db_investor

# ... other functions for managing funds and investments would go here