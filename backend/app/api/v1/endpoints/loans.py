from fastapi import APIRouter, Depends, BackgroundTasks # Add BackgroundTasks
from sqlalchemy.orm import Session
from typing import List # Add List
import uuid
# --- CORRECTED: Specific imports ---
from .... import models, schemas
from ....core.dependencies import get_db, allow_clients_only, allow_admin_only
from ....services import loan_service, notification_service # Import services

router = APIRouter()

# --- CORRECTED: Removed redefinition of apply_for_loan and fixed all names ---

@router.post("/apply", response_model=schemas.loan.Loan, dependencies=[Depends(allow_clients_only)])
def apply_for_loan(
    loan_in: schemas.loan.LoanApply,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(allow_clients_only),
    db: Session = Depends(get_db)
):
    new_loan = loan_service.create_loan_application(db, loan_in=loan_in, user=current_user)
    background_tasks.add_task(
        notification_service.send_loan_application_confirmation,
        user_email=current_user.email,
        loan_id=new_loan.id
    )
    return new_loan

@router.get("/my-loans", response_model=List[schemas.loan.Loan], dependencies=[Depends(allow_clients_only)])
def get_my_loans(
    current_user: models.User = Depends(allow_clients_only),
    db: Session = Depends(get_db)
):
    if not current_user.client_id:
        return []
    return db.query(models.Loan).filter(models.Loan.client_id == current_user.client_id).all()


@router.post("/{loan_id}/approve", response_model=schemas.loan.Loan, dependencies=[Depends(allow_admin_only)])
def approve_loan(
    loan_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    approved_loan = loan_service.approve_loan(db, loan_id=loan_id)
    background_tasks.add_task(
        notification_service.send_loan_status_update,
        loan_id=approved_loan.id,
        new_status="Approved"
    )
    return approved_loan

@router.post("/{loan_id}/disburse", response_model=schemas.loan.Loan, dependencies=[Depends(allow_admin_only)])
def disburse_loan(
    loan_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    disbursed_loan = loan_service.disburse_loan(db, loan_id=loan_id)
    background_tasks.add_task(
        notification_service.send_loan_status_update,
        loan_id=disbursed_loan.id,
        new_status="Disbursed"
    )
    return disbursed_loan