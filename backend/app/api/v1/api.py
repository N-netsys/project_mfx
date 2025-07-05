from fastapi import APIRouter
from .endpoints import auth, team, settings, clients, loan_products, loans, repayments, reports

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Onboarding"])
api_router.include_router(team.router, prefix="/team", tags=["Team Management"])
api_router.include_router(settings.router, prefix="/settings", tags=["Tenant Settings"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients & KYC"])
api_router.include_router(loan_products.router, prefix="/loan-products", tags=["Loan Products"])
api_router.include_router(loans.router, prefix="/loans", tags=["Loan Lifecycle"])
api_router.include_router(repayments.router, prefix="/repayments", tags=["Repayments"])
api_router.include_router(investors.router, prefix="/investors", tags=["Investor Management"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])