# backend/app/services/client_service.py

import uuid
from sqlalchemy.orm import Session

from .. import models
# --- CORRECTED: Import the specific schemas we actually use ---
from ..schemas.client import ClientCreateByStaff, ClientSelfSignUp
from ..core.security import UserRole
from . import user_service

def create_client_by_staff(db: Session, client_in: ClientCreateByStaff, user: models.User) -> models.Client:
    """
    Creates a simple client record without a user account.
    Used by MFI staff. The logged-in user's tenant is used.
    """
    db_client = models.Client(
        first_name=client_in.first_name,
        last_name=client_in.last_name,
        tenant_id=user.tenant_id
    )
    db.add(db_client)
    # The commit is handled by the endpoint's session management
    return db_client


def create_client_and_user_account(db: Session, signup_data: ClientSelfSignUp, tenant_id: uuid.UUID) -> models.User:
    """
    A transactional function to create both a Client profile and a User login.
    Used for the public signup portal.
    """
    # Check if a user with this email already exists
    if user_service.get_user_by_email(db, email=signup_data.user_info.email):
        raise ValueError("A user with this email already exists.")

    # Create the Client record first
    db_client = models.Client(
        first_name=signup_data.first_name,
        last_name=signup_data.last_name,
        tenant_id=tenant_id
    )
    db.add(db_client)
    db.flush() # Use flush to get the client's ID without ending the transaction

    # Create the User record and link it to the new Client profile
    user = user_service.create_user(
        db, 
        user_in=signup_data.user_info, 
        role=UserRole.CLIENT, 
        tenant_id=tenant_id,
        client_id=db_client.id # Link them here
    )
    
    # The commit will happen in the endpoint after the service call returns.
    return user