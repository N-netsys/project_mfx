from pydantic import BaseModel
from datetime import date

class ClientBase(BaseModel):
    first_name: str
    last_name: str
    phone_number: str | None = None
    date_of_birth: date | None = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    pass

class Client(ClientBase):
    id: int
    tenant_id: int
    created_by_user_id: int

    class Config:
        from_attributes = True