from pydantic import BaseModel

class DashboardMetrics(BaseModel):
    total_clients: int
    active_loans: int
    total_disbursed: float
    total_repaid: float
    portfolio_at_risk_par30: float