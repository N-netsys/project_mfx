from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ....core import dependencies
from ....models.user import User
from ....models.client import Client as ClientModel # Use an alias to avoid name conflict
from ....schemas.client import Client as ClientSchema, ClientCreate # Use aliases
from ....services import client_service

router = APIRouter()

@router.post("/", response_model=ClientSchema, status_code=status.HTTP_201_CREATED)
def create_client(
    client: ClientCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_user)
):
    return client_service.create_client(db=db, client=client, user=current_user)

@router.get("/", response_model=List[ClientSchema])
def read_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_user)
):
    clients = client_service.get_clients(db, tenant_id=current_user.tenant_id, skip=skip, limit=limit)
    return clients

@router.get("/{client_id}", response_model=ClientSchema) 
def read_client(
    client_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_user)
):
    db_client = client_service.get_client_by_id(db, client_id=client_id, tenant_id=current_user.tenant_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client