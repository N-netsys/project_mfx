import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class Investor(Base):
    """Represents an individual or entity providing capital."""
    __tablename__ = "investors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

class Fund(Base):
    """Represents a pool of capital from one or more investors."""
    __tablename__ = "funds"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    investments = relationship("Investment", back_populates="fund")

class Investment(Base):
    """Links an Investor to a Fund with a specific amount."""
    __tablename__ = "investments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investor_id = Column(UUID(as_uuid=True), ForeignKey("investors.id"), nullable=False)
    investor = relationship("Investor")
    fund_id = Column(UUID(as_uuid=True), ForeignKey("funds.id"), nullable=False)
    fund = relationship("Fund", back_populates="investments")
    amount_invested = Column(Numeric(12, 2), nullable=False)
    investment_date = Column(DateTime, default=datetime.utcnow)