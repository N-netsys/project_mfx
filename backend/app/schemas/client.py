import uuid
from pydantic import BaseModel
from .user import UserCreate

class ClientBase(BaseModel):
    first_name: str
    last_name: str

# Schema for MFI staff to create a client
class ClientCreateByStaff(ClientBase):
    pass

# Schema for a client to sign themselves up
class ClientSelfSignUp(ClientBase):
    user_info: UserCreate # Nest user creation details

class Client(ClientBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    class Config:
        from_attributes = True