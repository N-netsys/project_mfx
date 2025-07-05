# backend/app/api/v1/endpoints/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .... import models
from ....schemas import tenant as tenant_schema
from ....schemas import user as user_schema
from ....schemas import token as token_schema
from ....services import user_service
from ....core import security, dependencies
from ....core.security import UserRole
from ....models.accounting import DEFAULT_COA

router = APIRouter()

@router.post(
    "/register-organization", 
    response_model=user_schema.User, 
    status_code=status.HTTP_201_CREATED,
    summary="Register a New Organization and its First Admin User"
)
def register_organization(
    org_in: tenant_schema.OrganizationRegistration,
    db: Session = Depends(dependencies.get_db)
):
    """
    Onboards a new MFI by creating their Tenant, Subdomain, default Settings,
    Chart of Accounts, and the first Admin User. This is a single, atomic transaction.
    """
    # Check if subdomain or email is already taken
    if db.query(models.Tenant).filter(models.Tenant.subdomain == org_in.subdomain).first():
        raise HTTPException(status_code=400, detail="Subdomain is already in use. Please choose another.")
    if user_service.get_user_by_email(db, email=org_in.admin_email):
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    
    try:
        # 1. Create Tenant with subdomain
        tenant = models.Tenant(
            name=org_in.organization_name,
            subdomain=org_in.subdomain
        )
        db.add(tenant)
        db.flush() # Use flush to get the tenant's generated ID before committing

        # 2. Create default Tenant Settings
        settings = models.TenantSettings(tenant_id=tenant.id, currency="KES")
        db.add(settings)

        # 3. Create a default Chart of Accounts for the new tenant
        for acc_data in DEFAULT_COA:
            db_acc = models.accounting.ChartOfAccount(**acc_data, tenant_id=tenant.id)
            db.add(db_acc)
        
        # 4. Create the first Admin User for this tenant
        admin_user = user_service.create_user(
            db,
            user_in=user_schema.UserCreate(email=org_in.admin_email, password=org_in.admin_password),
            role=UserRole.ADMIN,
            tenant_id=tenant.id
        )
        
        db.commit()
        db.refresh(admin_user)
        return admin_user
    except Exception:
        db.rollback()
        # In production, you would log the error for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register organization due to an internal error."
        )

@router.post("/token", response_model=token_schema.Token, summary="User Login")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)
):
    """
    Standard OAuth2 password flow. Takes a username and password, returns a JWT access token.
    This works for all user roles (Admin, Client, etc.).
    """
    user = user_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=user_schema.User, summary="Get Current User Details")
def read_current_user(current_user: models.User = Depends(dependencies.get_current_user)):
    """
    Returns the details of the currently authenticated user based on the provided JWT.
    """
    return current_user