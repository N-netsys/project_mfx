from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .... import models, schemas
from ....services import user_service
from ....core import security, dependencies
from ....core.security import UserRole
from ....models.accounting import DEFAULT_COA
from ....schemas import token as token_schema
from ....schemas import user as user_schema
from ....models.user import User as UserModel

router = APIRouter()

@router.post(
    "/register-organization", 
    response_model=schemas.user.User, 
    status_code=status.HTTP_201_CREATED,
    summary="Register a New Organization and its First Admin User"
)
def register_organization(
    org_in: schemas.tenant.OrganizationRegistration,
    db: Session = Depends(dependencies.get_db)
):
    """
    A single transactional endpoint to onboard a new MFI. Creates:
    1. The Tenant (Organization)
    2. Default Tenant Settings
    3. Default Chart of Accounts
    4. The first Admin User
    """
    if user_service.get_user_by_email(db, email=org_in.admin_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )
    
    # Use a single transaction for all creation steps
    try:
        # 1. Create Tenant
        tenant = models.tenant.Tenant(name=org_in.organization_name)
        db.add(tenant)
        db.flush() # Flush to get the tenant ID before committing

        # 2. Create Tenant Settings
        settings = models.tenant.TenantSettings(tenant_id=tenant.id, currency="KES")
        db.add(settings)

        # 3. Create Chart of Accounts
        for acc_data in DEFAULT_COA:
            db_acc = models.accounting.ChartOfAccount(**acc_data, tenant_id=tenant.id)
            db.add(db_acc)
        
        # 4. Create Admin User
        admin_user = user_service.create_user(
            db,
            user_in=schemas.user.UserCreate(email=org_in.admin_email, password=org_in.admin_password),
            role=UserRole.ADMIN,
            tenant_id=tenant.id
        )
        
        db.commit()
        db.refresh(admin_user)
        return admin_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register organization. Error: {e}"
        )

@router.post("/token", response_model=token_schema.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)
):
    user = user_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = security.create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=user_schema.User)
def read_current_user(current_user: UserModel = Depends(dependencies.get_current_user)):
    return current_user