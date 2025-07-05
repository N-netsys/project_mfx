import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Enum as SQLAlchemyEnum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class LoanStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISBURSED = "disbursed"
    PAID_OFF = "paid_off"

class LoanProduct(Base):
    __tablename__ = "loan_products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False)
    max_tenure_months = Column(Integer, nullable=False)
    grace_period_days = Column(Integer, default=0)
    penalty_type = Column(String, nullable=True)
    penalty_value = Column(Numeric(10, 2), default=0.00)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    tenant = relationship("Tenant")

class Loan(Base):
    __tablename__ = "loans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount_requested = Column(Numeric(10, 2), nullable=False)
    tenure_months = Column(Integer, nullable=False)
    status = Column(SQLAlchemyEnum(LoanStatus), default=LoanStatus.PENDING, nullable=False)
    assigned_officer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    officer = relationship("User")
    repayment_schedule = relationship("RepaymentSchedule", back_populates="loan", cascade="all, delete-orphan")
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    client = relationship("Client")
    
    loan_product_id = Column(UUID(as_uuid=True), ForeignKey("loan_products.id"), nullable=False)
    product = relationship("LoanProduct")
    
    applied_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    disbursed_at = Column(DateTime, nullable=True)
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    tenant = relationship("Tenant")