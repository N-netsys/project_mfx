from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    # In a real app, you might restrict who can set roles/tenants
    role: str = 'loan_officer'
    tenant_id: int

class User(UserBase):
    id: int
    role: str
    is_active: bool
    tenant_id: int

    class Config:
        from_attributes = True