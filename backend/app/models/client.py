import uuid
from enum import Enum
from sqlalchemy import Column, String, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class KycStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Client(Base):
    __tablename__ = "clients"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    tenant = relationship("Tenant")

    # --- THIS IS THE KEY FIX ---
    # We use a string "User" to break the import cycle.
    # `back_populates` links this to the 'client_profile' relationship in User.
    user_account = relationship("User", back_populates="client_profile", uselist=False)
    
    documents = relationship("KYCDocument", back_populates="client", cascade="all, delete-orphan")


class KYCDocument(Base):
    """Stores information about uploaded KYC documents."""
    __tablename__ = "kyc_documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="documents")
    
    document_type = Column(String, nullable=False) # e.g., "National ID", "Proof of Address"
    storage_url = Column(String, nullable=False) # URL to the file in S3/Cloud Storage
    
    # This line will now work correctly
    status = Column(SQLAlchemyEnum(KycStatus), default=KycStatus.PENDING, nullable=False)
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)