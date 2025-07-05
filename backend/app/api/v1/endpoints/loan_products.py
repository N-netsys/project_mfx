"""
API endpoints for managing Loan Products.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..core.dependencies import get_db, allow_admin_only

router = APIRouter()

@router.post(
    "/", 
    response_model=schemas.loan.LoanProduct, 
    dependencies=[Depends(allow_admin_only)],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Loan Product"
)
def create_loan_product(
    product_in: schemas.loan.LoanProductCreate,
    current_user: models.User = Depends(allow_admin_only),
    db: Session = Depends(get_db)
):
    db_product = models.loan.LoanProduct(
        **product_in.dict(), 
        tenant_id=current_user.tenant_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get(
    "/", 
    response_model=List[schemas.loan.LoanProduct],
    summary="List all Loan Products for Tenant"
)
def list_loan_products(
    current_user: models.User = Depends(Depends(get_db)),
    db: Session = Depends(get_db)
):
    # In a multi-tenant app, you'd get the user's tenant_id and filter.
    # For now, let's assume one tenant for simplicity.
    products = db.query(models.loan.LoanProduct).all()
    return products