"""
Service for handling repayment schedules and transactions.
"""
from sqlalchemy.orm import Session
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from .. import models, schemas
from . import accounting_service

def generate_schedule(db: Session, loan: models.Loan):
    """
    Generates a simple, flat-interest repayment schedule for a loan.
    """
    principal = Decimal(loan.amount_requested)
    interest_rate = Decimal(loan.product.interest_rate) / Decimal(100)
    tenure = loan.tenure_months

    # Simple flat interest calculation
    total_interest = principal * interest_rate * (Decimal(tenure) / Decimal(12))
    total_repayment = principal + total_interest
    monthly_payment = total_repayment / Decimal(tenure)
    monthly_principal = principal / Decimal(tenure)
    monthly_interest = total_interest / Decimal(tenure)
    
    for i in range(1, tenure + 1):
        due_date = date.today() + relativedelta(months=i)
        schedule_entry = models.repayment.RepaymentSchedule(
            loan_id=loan.id,
            due_date=due_date,
            amount_due=monthly_payment,
            principal_due=monthly_principal,
            interest_due=monthly_interest,
            tenant_id=loan.tenant_id
        )
        db.add(schedule_entry)

def record_payment(
    db: Session, 
    payment_in: schemas.repayment.RepaymentRecord,
    loan: models.Loan,
    user: models.User
):
    """
    Records a repayment transaction and posts it to the GL.
    """
    # 1. Create the repayment transaction record
    transaction = models.repayment.RepaymentTransaction(
        loan_id=loan.id,
        schedule_id=payment_in.schedule_id,
        amount_paid=Decimal(payment_in.amount_paid),
        recorded_by_user_id=user.id,
        tenant_id=user.tenant_id
    )
    db.add(transaction)

    # 2. Post to accounting
    accounting_service.post_transaction(
        db,
        tenant_id=user.tenant_id,
        description=f"Repayment for Loan ID {loan.id}",
        debit_account_code=accounting_service.CASH_ACCOUNT,
        credit_account_code=accounting_service.LOANS_RECEIVABLE_ACCOUNT,
        amount=Decimal(payment_in.amount_paid)
    )

    # 3. Update schedule status (simplified)
    schedule_entry = db.query(models.repayment.RepaymentSchedule).filter(
        models.repayment.RepaymentSchedule.id == payment_in.schedule_id
    ).first()
    if schedule_entry:
        schedule_entry.status = models.repayment.RepaymentStatus.PAID
    
    # Commit will be handled by the endpoint function's db session management

def apply_late_penalties(db: Session, loan: models.Loan):
    """
    Checks for overdue payments and applies penalties based on the loan product rules.
    This would ideally be run by a scheduled background job (e.g., nightly).
    """
    product = loan.product
    if not product.penalty_type or not product.penalty_value:
        return # No penalty configured

    today = date.today()
    overdue_installments = db.query(models.repayment.RepaymentSchedule).filter(
        models.repayment.RepaymentSchedule.loan_id == loan.id,
        models.repayment.RepaymentSchedule.status == models.repayment.RepaymentStatus.PENDING,
        models.repayment.RepaymentSchedule.due_date < today
    ).all()
    
    for installment in overdue_installments:
        # Simple example: Apply a flat penalty
        # A more robust system would check if a penalty for this installment was already applied.
        if product.penalty_type == 'flat':
            # Add logic here to create a penalty transaction or add to the due amount
            print(f"Applying flat penalty of {product.penalty_value} to installment {installment.id}")
            # installment.amount_due += Decimal(product.penalty_value)
        
        installment.status = models.repayment.RepaymentStatus.LATE