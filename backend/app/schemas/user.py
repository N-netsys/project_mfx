import uuid
from pydantic import BaseModel, EmailStr
from ..core.security import UserRole

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: uuid.UUID
    role: UserRole
    tenant_id: uuid.UUID
    client_id: uuid.UUID | None = None
    is_active: bool

    class Config:
        from_attributes = True

class TeamMemberCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole