# backend/app/api/v1/endpoints/investors.py

"""
API endpoints for managing Investors and Funds.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

# --- CORRECTED: Specific imports ---
from .... import models
from ....schemas import investor as investor_schema
from ....core.dependencies import get_db, allow_admin_only
from ....services import investor_service

router = APIRouter()

@router.post(
    "/",
    response_model=investor_schema.Investor,
    dependencies=[Depends(allow_admin_only)],
    status_code=status.HTTP_201_CREATED,
    summary="Create a New Investor (Admin Only)"
)
def create_investor(
    investor_in: investor_schema.InvestorCreate,
    current_user: models.User = Depends(allow_admin_only),
    db: Session = Depends(get_db)
):
    """
    Allows an Admin to add a new investor to their organization's records.
    """
    return investor_service.create_investor(db, investor_in, tenant_id=current_user.tenant_id)

# ... other endpoints for listing investors, creating funds, etc. would go here