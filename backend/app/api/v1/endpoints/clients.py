from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import uuid
from app.models import User, Client
from app import schemas
from app.services import user_service
from app.core.dependencies import get_db, allow_mfi_staff
from app.core.security import UserRole

router = APIRouter()

# --- MFI STAFF ENDPOINT ---
@router.post(
    "/", 
    response_model=schemas.client.Client, 
    dependencies=[Depends(allow_mfi_staff)],
    status_code=status.HTTP_201_CREATED
)
def create_client_by_staff(
    client_in: schemas.client.ClientCreateByStaff,
    current_user: User = Depends(allow_mfi_staff),
    db: Session = Depends(get_db)
):
    # Business logic to create a client record by staff
    pass

# --- PUBLIC/CLIENT PORTAL ENDPOINT ---
@router.post("/signup", response_model=schemas.user.User, status_code=status.HTTP_201_CREATED)
def client_self_signup(
    signup_data: schemas.client.ClientSelfSignUp, 
    db: Session = Depends(get_db)
):
    # This assumes a single-tenant scenario for signup, or tenant is determined differently
    # For now, let's assume a default tenant for public signups.
    default_tenant_id = uuid.UUID("your_default_tenant_uuid_here")

    # 1. Create the Client record
    db_client = Client(
        first_name=signup_data.first_name,
        last_name=signup_data.last_name,
        tenant_id=default_tenant_id
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)

    # 2. Create the User record linked to the Client
    user = user_service.create_user(
        db, 
        user_in=signup_data.user_info, 
        role=UserRole.CLIENT, 
        tenant_id=default_tenant_id,
        client_id=db_client.id
    )
    return user