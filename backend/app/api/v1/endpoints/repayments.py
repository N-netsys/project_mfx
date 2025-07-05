"""
API endpoints for recording loan repayments.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from .. import models, schemas
from ..core.dependencies import get_db, allow_mfi_staff
from ..services import repayment_service

router = APIRouter()

@router.post(
    "/{loan_id}/record",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(allow_mfi_staff)],
    summary="Record a client's loan repayment"
)
def record_repayment(
    loan_id: uuid.UUID,
    payment_in: schemas.repayment.RepaymentRecord,
    current_user: models.User = Depends(allow_mfi_staff),
    db: Session = Depends(get_db)
):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
        
    repayment_service.record_payment(db, payment_in=payment_in, loan=loan, user=current_user)
    db.commit()
    return