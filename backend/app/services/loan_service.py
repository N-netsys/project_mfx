# backend/app/services/loan_service.py

"""
Service layer to orchestrate all business logic related to loans.
This includes application, approval, disbursement, and triggering other services.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from decimal import Decimal
import uuid

# --- CORRECTED: Specific imports for clarity and correctness ---
from .. import models
from ..schemas import loan as loan_schema
from . import repayment_service, accounting_service

def create_loan_application(db: Session, loan_in: loan_schema.LoanApply, user: models.User) -> models.Loan:
    """
    Creates a new loan application record for a client.
    Validates that the user is a client and the chosen loan product is valid for their tenant.
    """
    if not user.client_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not linked to a client profile.")
    
    # Check if the loan product exists for the tenant
    product = db.query(models.loan.LoanProduct).filter(
        models.loan.LoanProduct.id == loan_in.loan_product_id,
        models.loan.LoanProduct.tenant_id == user.tenant_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan product not found.")
        
    db_loan = models.Loan(
        amount_requested=loan_in.amount_requested,
        tenure_months=loan_in.tenure_months,
        loan_product_id=loan_in.loan_product_id,
        client_id=user.client_id,
        tenant_id=user.tenant_id,
        status=models.loan.LoanStatus.PENDING # Explicitly set initial status
    )
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

def approve_loan(db: Session, loan_id: uuid.UUID) -> models.Loan:
    """
    Sets a loan's status to 'approved'.
    """
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not db_loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found.")
    
    if db_loan.status != models.loan.LoanStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot approve loan with status '{db_loan.status}'.")

    db_loan.status = models.loan.LoanStatus.APPROVED
    db_loan.approved_at = datetime.utcnow()
    db.commit()
    db.refresh(db_loan)
    return db_loan

def disburse_loan(db: Session, loan_id: uuid.UUID) -> models.Loan:
    """
    Orchestrates the loan disbursement process:
    1. Updates loan status.
    2. Generates the repayment schedule.
    3. Posts the disbursement transaction to the General Ledger.
    """
    db_loan = db.query(models.Loan).filter(
        models.Loan.id == loan_id,
        models.Loan.status == models.loan.LoanStatus.APPROVED
    ).first()
    
    if not db_loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approved loan not found.")

    # 1. Update loan status
    db_loan.status = models.loan.LoanStatus.DISBURSED
    db_loan.disbursed_at = datetime.utcnow()
    
    # 2. Generate Repayment Schedule
    repayment_service.generate_schedule(db, loan=db_loan, grace_days=db_loan.product.grace_period_days)

    # 3. Post to Accounting
    accounting_service.post_transaction(
        db,
        tenant_id=db_loan.tenant_id,
        description=f"Loan disbursement for client {db_loan.client.first_name} {db_loan.client.last_name}",
        debit_account_code=accounting_service.LOANS_RECEIVABLE_ACCOUNT, # Debit asset (Loans Receivable)
        credit_account_code=accounting_service.CASH_ACCOUNT, # Credit asset (Cash)
        amount=Decimal(db_loan.amount_requested)
    )

    db.commit()
    db.refresh(db_loan)
    return db_loan