# This file serves as the central registry for all SQLAlchemy models.
# Importing them here ensures that SQLAlchemy's Base metadata is aware of them
# all, which is crucial for resolving relationships and for tools like Alembic.

from .base import Base
from .tenant import Tenant, TenantSettings
from .user import User
from .client import Client, KYCDocument, KycStatus
from .loan import Loan, LoanProduct, LoanStatus
from .repayment import RepaymentSchedule, RepaymentTransaction, RepaymentStatus
from .accounting import ChartOfAccount, GeneralLedgerEntry, AccountType
from .investor import Investor, Fund, Investment