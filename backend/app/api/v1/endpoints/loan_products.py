# backend/app/api/v1/endpoints/loan_products.py

"""
API endpoints for managing Loan Products.
These are the templates for loans that an MFI can offer.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

# --- CORRECTED: Specific and correct imports ---
from .... import models, schemas
from ....core.dependencies import get_db, allow_admin_only, get_current_user

router = APIRouter()

@router.post(
    "/", 
    response_model=schemas.loan.LoanProduct, 
    dependencies=[Depends(allow_admin_only)],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Loan Product (Admin Only)"
)
def create_loan_product(
    product_in: schemas.loan.LoanProductCreate,
    current_user: models.User = Depends(allow_admin_only),
    db: Session = Depends(get_db)
):
    """
    Allows an Admin to define a new loan product for their organization.
    """
    db_product = models.loan.LoanProduct(
        # The **product_in.dict() call was missing, which is a latent bug
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
    summary="List all Loan Products for a Tenant"
)
def list_loan_products(
    # --- THIS IS THE CORRECTED FUNCTION SIGNATURE ---
    # It depends on the current user to get their tenant_id.
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns a list of all available loan products for the currently
    authenticated user's tenant. Accessible by any authenticated user.
    """
    products = db.query(models.loan.LoanProduct).filter(
        models.loan.LoanProduct.tenant_id == current_user.tenant_id
    ).all()
    return products