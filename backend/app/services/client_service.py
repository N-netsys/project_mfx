from sqlalchemy.orm import Session
from typing import List
from ..schemas.client import ClientCreate # Import ClientCreate directly
from ..models.client import Client
from ..models.user import User

def create_client(db: Session, client: ClientCreate, user: User) -> Client:
    db_client = Client( # Use 'Client'
        **client.dict(),
        created_by_user_id=user.id,
        tenant_id=user.tenant_id
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def get_clients(db: Session, tenant_id: int, skip: int = 0, limit: int = 100) -> List[Client]: # Use 'List[Client]'
    return db.query(Client).filter(Client.tenant_id == tenant_id).offset(skip).limit(limit).all()

def get_client_by_id(db: Session, client_id: int, tenant_id: int) -> Client | None: # Use 'Client'
    return db.query(Client).filter(Client.id == client_id, Client.tenant_id == tenant_id).first()