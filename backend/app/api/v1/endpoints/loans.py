
"""
API Endpoints for Loan Management.
This includes loan application by clients and processing by MFI staff.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from .. import models, schemas
from ..core.dependencies import get_db, allow_mfi_staff, allow_clients_only, allow_admin_only
from ..core.security import UserRole

router = APIRouter()

# --- Client Portal Endpoint ---
@router.post(
    "/apply", 
    response_model=schemas.loan.Loan, 
    dependencies=[Depends(allow_clients_only)],
    summary="Client Applies for a New Loan",
    description="Allows an authenticated client to submit a new loan application."
)
def apply_for_loan(
    loan_in: schemas.loan.LoanApply,
    background_tasks: BackgroundTasks, # For sending notifications
    current_user: models.User = Depends(allow_clients_only),
    db: Session = Depends(get_db)
):

    """
    Creates a new loan application record for the currently logged-in client.
    """

    if not current_user.client_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User is not linked to a client profile.")
    
    db_loan = models.Loan(
        **loan_in.dict(),
        client_id=current_user.client_id,
        tenant_id=current_user.tenant_id
    )
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

# --- MFI Staff Endpoints ---
@router.post(
    "/{loan_id}/approve",
    response_model=schemas.loan.Loan,
    dependencies=[Depends(allow_admin_only)]
)
def apply_for_loan(
    loan_in: schemas.loan.LoanApply,
    background_tasks: BackgroundTasks, # For sending notifications
    current_user: models.User = Depends(allow_clients_only),
    db: Session = Depends(get_db)
):
    """
    Creates a new loan application record for the currently logged-in client.
    """
    new_loan = loan_service.create_loan_application(db, loan_in=loan_in, user=current_user)
    
    # --- Fledged Feature: Background Task for Notifications ---
    background_tasks.add_task(
        notification_service.send_loan_application_confirmation,
        user_email=current_user.email,
        loan_id=new_loan.id
    )
    return new_loan

@router.post(
    "/{loan_id}/approve",
    response_model=schemas.loan.Loan,
    dependencies=[Depends(allow_admin_only)],
    summary="Approve a Loan Application"
)
def approve_loan(
    loan_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Marks a loan's status as 'approved'. Restricted to Admins.
    """
    approved_loan = loan_service.approve_loan(db, loan_id=loan_id)
    
    background_tasks.add_task(
        notification_service.send_loan_status_update,
        loan_id=approved_loan.id,
        new_status="Approved"
    )
    return approved_loan

@router.post(
    "/{loan_id}/disburse",
    response_model=schemas.loan.Loan,
    dependencies=[Depends(allow_admin_only)],
    summary="Disburse an Approved Loan"
)
def disburse_loan(
    loan_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Marks an approved loan as 'disbursed' and creates the repayment schedule.
    """
    disbursed_loan = loan_service.disburse_loan(db, loan_id=loan_id)
    
    background_tasks.add_task(
        notification_service.send_loan_status_update,
        loan_id=disbursed_loan.id,
        new_status="Disbursed"
    )
    return disbursed_loan

@router.get(
    "/my-loans", 
    response_model=List[schemas.loan.Loan],
    dependencies=[Depends(allow_clients_only)],
    summary="Get All Loans for the Logged-in Client"
)
def get_my_loans(
    current_user: models.User = Depends(allow_clients_only),
    db: Session = Depends(get_db)
):
    """Fetches the loan history for the currently authenticated client."""
    if not current_user.client_id:
        return [] # Or raise an error
    
    return db.query(models.Loan).filter(models.Loan.client_id == current_user.client_id).all()