# backend/app/models/__init__.py

"""
This file serves as the central registry for all SQLAlchemy models.
Importing them here and adding them to __all__ ensures that SQLAlchemy's
Base metadata is aware of them and that they can be easily imported elsewhere.
"""

from .base import Base
from .tenant import Tenant, TenantSettings
from .user import User
from .client import Client, KYCDocument, KycStatus
from .loan import Loan, LoanProduct, LoanStatus
from .repayment import RepaymentSchedule, RepaymentTransaction, RepaymentStatus
from .accounting import ChartOfAccount, GeneralLedgerEntry, AccountType, DEFAULT_COA
from .investor import Investor, Fund, Investment

# --- NEW: Define the public API of the 'models' package ---
__all__ = [
    "Base",
    "Tenant",
    "TenantSettings",
    "User",
    "Client",
    "KYCDocument",
    "KycStatus",
    "Loan",
    "LoanProduct",
    "LoanStatus",
    "RepaymentSchedule",
    "RepaymentTransaction",
    "RepaymentStatus",
    "ChartOfAccount",
    "GeneralLedgerEntry",
    "AccountType",
    "DEFAULT_COA",
    "Investor",
    "Fund",
    "Investment",
]