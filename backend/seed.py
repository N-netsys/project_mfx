import uuid
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import Tenant, TenantSettings, ChartOfAccount, AccountType
from app.services import user_service
from app.schemas.user import UserCreate
from app.core.security import UserRole
from dotenv import load_dotenv

load_dotenv()

print("--- MFI-SaaS Full-Fledged Seeding Script ---")

# --- Configuration ---
DEFAULT_TENANT_ID = uuid.UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")
DEFAULT_TENANT_NAME = "Apex Microfinance"
ADMIN_EMAIL = "admin@apex.com"
ADMIN_PASSWORD = "strongpassword123"

# Default Chart of Accounts
DEFAULT_COA = [
    {"name": "Cash on Hand", "account_code": "1010", "account_type": AccountType.ASSET},
    {"name": "Loans Receivable", "account_code": "1100", "account_type": AccountType.ASSET},
    {"name": "Interest Revenue", "account_code": "4010", "account_type": AccountType.REVENUE},
    {"name": "Client Savings", "account_code": "2010", "account_type": AccountType.LIABILITY},
]

db: Session = SessionLocal()

try:
    # 1. Create Tenant
    tenant = db.query(Tenant).filter(Tenant.id == DEFAULT_TENANT_ID).first()
    if not tenant:
        print(f"Creating tenant: '{DEFAULT_TENANT_NAME}'")
        tenant = Tenant(id=DEFAULT_TENANT_ID, name=DEFAULT_TENANT_NAME)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        print("Creating default settings for tenant...")
        settings = TenantSettings(
            tenant_id=tenant.id,
            currency="KES",
            configurations={"repayment_day_rule": "same_day"}
        )
        db.add(settings)
        db.commit()
    else:
        print(f"Tenant '{tenant.name}' already exists.")

    # 2. Create Chart of Accounts for the Tenant
    print("Seeding Chart of Accounts...")
    for acc_data in DEFAULT_COA:
        acc = db.query(ChartOfAccount).filter(
            ChartOfAccount.account_code == acc_data["account_code"],
            ChartOfAccount.tenant_id == tenant.id
        ).first()
        if not acc:
            db_acc = ChartOfAccount(**acc_data, tenant_id=tenant.id)
            db.add(db_acc)
            # This print statement is also now correct
            print(f"  - Created account: {acc_data['name']} ({acc_data['account_code']})")
    db.commit()

    # 3. Create Admin User
    user = user_service.get_user_by_email(db, email=ADMIN_EMAIL)
    if not user:
        print(f"Creating admin user: {ADMIN_EMAIL}")
        user_in = UserCreate(email=ADMIN_EMAIL, password=ADMIN_PASSWORD)
        user_service.create_user(db, user_in, UserRole.ADMIN, tenant.id)
    else:
        print(f"Admin user '{ADMIN_EMAIL}' already exists.")
    
    db.commit()
    print("\n--- Seeding Complete ---")
    print(f"Login with Username: {ADMIN_EMAIL} | Password: {ADMIN_PASSWORD}")
finally:
    db.close()