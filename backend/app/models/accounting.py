import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Enum as SQLAlchemyEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base
from enum import Enum

class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"

class ChartOfAccount(Base):
    """Defines the accounts for the General Ledger."""
    __tablename__ = "chart_of_accounts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    account_code = Column(String, nullable=False) # Should be unique per tenant
    account_type = Column(SQLAlchemyEnum(AccountType), nullable=False) # This line relies on the import
    is_active = Column(Boolean, default=True)
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

DEFAULT_COA = [
    {"name": "Cash on Hand", "account_code": "1010", "type": AccountType.ASSET},
    {"name": "Loans Receivable", "account_code": "1100", "type": AccountType.ASSET},
    {"name": "Interest Revenue", "account_code": "4010", "type": AccountType.REVENUE},
    {"name": "Client Savings", "account_code": "2010", "type": AccountType.LIABILITY},
]

class GeneralLedgerEntry(Base):
    """A single entry (debit or credit) in the General Ledger."""
    __tablename__ = "general_ledger_entries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    transaction_id = Column(String, index=True, nullable=False) # Groups entries for one event
    transaction_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    description = Column(String, nullable=False)
    
    account_id = Column(UUID(as_uuid=True), ForeignKey("chart_of_accounts.id"), nullable=False)
    account = relationship("ChartOfAccount")
    
    debit = Column(Numeric(12, 2), default=0.00)
    credit = Column(Numeric(12, 2), default=0.00)
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)