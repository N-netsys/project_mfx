# backend/app/api/v1/endpoints/clients.py

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

# --- Specific imports for clarity and correctness ---
from .... import models
from ....schemas import client as client_schema
from ....schemas import user as user_schema
from ....services import client_service
from ....core.dependencies import get_db, allow_mfi_staff, get_tenant_from_subdomain

router = APIRouter()

@router.post(
    "/", 
    response_model=client_schema.Client, 
    dependencies=[Depends(allow_mfi_staff)],
    status_code=status.HTTP_201_CREATED,
    summary="Create a New Client Record (by MFI Staff)"
)
def create_client_by_staff(
    client_in: client_schema.ClientCreateByStaff,
    current_user: models.User = Depends(allow_mfi_staff),
    db: Session = Depends(get_db)
):
    """
    Allows an authenticated MFI staff member (Admin, Loan Officer, etc.) to create a new
    client profile within their organization's tenant.
    This action does NOT create a user account for the client.
    """
    return client_service.create_client_by_staff(db=db, client_in=client_in, user=current_user)

@router.post(
    "/signup", 
    response_model=user_schema.User, 
    status_code=status.HTTP_201_CREATED,
    summary="Client Self-Registration (via Subdomain)"
)
def client_self_signup(
    signup_data: client_schema.ClientSelfSignUp, 
    # The current tenant is now automatically resolved from the request's host/header.
    tenant: models.Tenant = Depends(get_tenant_from_subdomain),
    db: Session = Depends(get_db)
):
    """
    Allows a new person to sign up for the MFI corresponding to the subdomain used.
    A request to `apex.mfx.com/api/v1/clients/signup` (or a request with the header
    `X-Tenant-Subdomain: apex`) will sign up a client for the 'Apex' tenant.
    This creates both a Client profile and a User account for the client portal.
    """
    try:
        user = client_service.create_client_and_user_account(
            db,
            signup_data=signup_data,
            tenant_id=tenant.id
        )
        return user
    except ValueError as e:
        # Catches errors from the service layer, like "email already exists".
        raise HTTPException(status_code=400, detail=str(e))