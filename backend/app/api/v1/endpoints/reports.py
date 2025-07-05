"""
API endpoints for generating financial and operational reports.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ....core.dependencies import get_db, allow_mfi_staff, allow_admin_only, allow_auditor_and_admin
from ....services import reporting_service
from .... import models, schemas
# --- For Excel Export ---
import pandas as pd
from io import BytesIO
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get(
    "/trial-balance",
    response_model=List[schemas.accounting.TrialBalanceEntry],
    dependencies=[Depends(allow_mfi_staff)],
    summary="Generate a Trial Balance Report"
)
def get_trial_balance(
    current_user: models.User = Depends(allow_mfi_staff),
    db: Session = Depends(get_db)
):
    """
    Calculates the total debits and credits for each account to ensure the books are balanced.
    """
    results = db.query(
        models.accounting.ChartOfAccount.account_code,
        models.accounting.ChartOfAccount.name,
        func.sum(models.accounting.GeneralLedgerEntry.debit).label("total_debits"),
        func.sum(models.accounting.GeneralLedgerEntry.credit).label("total_credits")
    ).join(
        models.accounting.GeneralLedgerEntry, 
        models.accounting.ChartOfAccount.id == models.accounting.GeneralLedgerEntry.account_id
    ).filter(
        models.accounting.ChartOfAccount.tenant_id == current_user.tenant_id
    ).group_by(
        models.accounting.ChartOfAccount.account_code,
        models.accounting.ChartOfAccount.name
    ).order_by(
        models.accounting.ChartOfAccount.account_code
    ).all()
    
    return [
        schemas.accounting.TrialBalanceEntry(
            account_code=r.account_code,
            account_name=r.name,
            total_debits=float(r.total_debits),
            total_credits=float(r.total_credits)
        )
        for r in results
    ]

@router.get("/dashboard", response_model=schemas.reporting.DashboardMetrics, dependencies=[Depends(allow_admin_only)])
def get_dashboard_data(
    current_user: models.User = Depends(allow_admin_only), # Now correct
    db: Session = Depends(get_db)
):
    return reporting_service.get_dashboard_metrics(db, tenant_id=current_user.tenant_id)

@router.get("/export/loans", dependencies=[Depends(allow_auditor_and_admin)])
def export_loans_to_excel(
    current_user: models.User = Depends(allow_auditor_and_admin), # Now correct
    db: Session = Depends(get_db)
):
    loans = db.query(models.Loan).filter(models.Loan.tenant_id == current_user.tenant_id).all()
    
    loan_data = [
        {
            "loan_id": str(loan.id), # CORRECTED: Changed 'l' to 'loan'
            "client_id": str(loan.client_id),
            "amount_requested": float(loan.amount_requested),
            "status": loan.status.value,
            "applied_at": loan.applied_at.strftime("%Y-%m-%d %H:%M:%S") if loan.applied_at else None
        } 
        for loan in loans # CORRECTED: Changed 'l' to 'loan' to fix E741
    ]
    
    df = pd.DataFrame(loan_data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Loans')
    
    output.seek(0)
    
    headers = {'Content-Disposition': 'attachment; filename="loan_report.xlsx"'}
    return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')