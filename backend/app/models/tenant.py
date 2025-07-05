import uuid
from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True, nullable=False)
    settings = relationship("TenantSettings", back_populates="tenant", uselist=False, cascade="all, delete-orphan")

class TenantSettings(Base):
    """Holds all tenant-specific configurations."""
    __tablename__ = "tenant_settings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, unique=True)
    tenant = relationship("Tenant", back_populates="settings")
    currency = Column(String, default="USD", nullable=False)
    # penalty_type, penalty_value, repayment_rules etc. would go here
    # Using JSONB for flexibility is also a great option.
    configurations = Column(JSON, default={})