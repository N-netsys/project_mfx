"""
Service for aggregating data and generating reports.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
from .. import models, schemas

def get_dashboard_metrics(db: Session, tenant_id: uuid.UUID) -> schemas.reporting.DashboardMetrics:
    """
    Calculates key performance indicators for the MFI admin dashboard.
    """
    total_clients = db.query(func.count(models.Client.id)).filter(models.Client.tenant_id == tenant_id).scalar()

    active_loans = db.query(func.count(models.Loan.id)).filter(
        models.Loan.tenant_id == tenant_id,
        models.Loan.status.in_([models.loan.LoanStatus.DISBURSED])
    ).scalar()
    
    total_disbursed_query = db.query(func.sum(models.Loan.amount_requested)).filter(
        models.Loan.tenant_id == tenant_id,
        models.Loan.status.in_([models.loan.LoanStatus.DISBURSED, models.loan.LoanStatus.PAID_OFF])
    ).scalar()
    
    total_repaid_query = db.query(func.sum(models.repayment.RepaymentTransaction.amount_paid)).filter(
        models.repayment.RepaymentTransaction.tenant_id == tenant_id
    ).scalar()

    # In a real app, PAR would be more complex, checking due dates
    portfolio_at_risk_par30 = 0.0 

    return schemas.reporting.DashboardMetrics(
        total_clients=total_clients or 0,
        active_loans=active_loans or 0,
        total_disbursed=float(total_disbursed_query or 0.0),
        total_repaid=float(total_repaid_query or 0.0),
        portfolio_at_risk_par30=portfolio_at_risk_par30
    )