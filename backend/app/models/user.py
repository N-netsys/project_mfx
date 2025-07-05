# backend/app/models/user.py

import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    tenant = relationship("Tenant")

    # This user's corresponding client profile, if they have the 'client' role.
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True, unique=True)
    
    # --- THIS IS THE KEY FIX ---
    # We use a string "Client" to break the import cycle.
    # `back_populates` tells SQLAlchemy how to link this to the other side.
    client_profile = relationship("Client", back_populates="user_account", foreign_keys=[client_id])