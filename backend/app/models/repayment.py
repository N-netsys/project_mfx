import uuid
from datetime import datetime, date
from sqlalchemy import Column, ForeignKey, Numeric, DateTime, Date, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base
from enum import Enum

class RepaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    LATE = "late"

class RepaymentSchedule(Base):
    """Represents a single installment due for a loan."""
    __tablename__ = "repayment_schedules"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    loan_id = Column(UUID(as_uuid=True), ForeignKey("loans.id"), nullable=False)
    loan = relationship("Loan")
    
    due_date = Column(Date, nullable=False)
    amount_due = Column(Numeric(10, 2), nullable=False)
    principal_due = Column(Numeric(10, 2), nullable=False)
    interest_due = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLAlchemyEnum(RepaymentStatus), default=RepaymentStatus.PENDING, nullable=False)
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

class RepaymentTransaction(Base):
    """Records an actual payment made by a client."""
    __tablename__ = "repayment_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    loan_id = Column(UUID(as_uuid=True), ForeignKey("loans.id"), nullable=False)
    loan = relationship("Loan")

    schedule_id = Column(UUID(as_uuid=True), ForeignKey("repayment_schedules.id"), nullable=True)
    schedule = relationship("RepaymentSchedule")

    amount_paid = Column(Numeric(10, 2), nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # MFI staff member who recorded the payment
    recorded_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    recorder = relationship("User")

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)