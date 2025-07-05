"""
API endpoints for managing Investors and Funds.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..core.dependencies import get_db, allow_admin_only
from ..services import investor_service

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.investor.Investor,
    dependencies=[Depends(allow_admin_only)],
    status_code=status.HTTP_201_CREATED
)
def create_investor(
    investor_in: schemas.investor.InvestorCreate,
    current_user: models.User = Depends(allow_admin_only),
    db: Session = Depends(get_db)
):
    return investor_service.create_investor(db, investor_in, tenant_id=current_user.tenant_id)

# ... other endpoints for funds, etc.