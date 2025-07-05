# backend/seed.py

import uuid
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import (
    Tenant, TenantSettings, ChartOfAccount, AccountType, DEFAULT_COA
)
from app.services import user_service
from app.schemas.user import UserCreate
from app.core.security import UserRole
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

print("--- MFI-SaaS Development Seeding Script ---")

# --- Configuration for a predictable local/dev environment ---
# This is the subdomain we will use for all local testing.
DEFAULT_TENANT_SUBDOMAIN = "apex"
DEFAULT_TENANT_NAME = "Apex Microfinance"
ADMIN_EMAIL = "admin@apex.com"
ADMIN_PASSWORD = "strongpassword123"

# Establish a database session
db: Session = SessionLocal()

try:
    # 1. Find or Create the Default Tenant
    tenant = db.query(Tenant).filter(Tenant.subdomain == DEFAULT_TENANT_SUBDOMAIN).first()
    
    if not tenant:
        print(f"Creating default tenant '{DEFAULT_TENANT_NAME}' with subdomain '{DEFAULT_TENANT_SUBDOMAIN}'...")
        
        # Create the tenant record with the required subdomain
        tenant = Tenant(
            name=DEFAULT_TENANT_NAME,
            subdomain=DEFAULT_TENANT_SUBDOMAIN
        )
        db.add(tenant)
        db.flush() # Use flush to get the tenant's generated ID for subsequent objects

        # Create default settings for the new tenant
        print("  -> Creating default settings...")
        settings = TenantSettings(
            tenant_id=tenant.id,
            currency="KES",
            configurations={"repayment_day_rule": "same_day", "penalty_rate_annual": 10.0}
        )
        db.add(settings)

        # Create the default Chart of Accounts for the new tenant
        print("  -> Seeding Chart of Accounts...")
        for acc_data in DEFAULT_COA:
            db_acc = ChartOfAccount(**acc_data, tenant_id=tenant.id)
            db.add(db_acc)
            print(f"    - Created account: {acc_data['name']} ({acc_data['account_code']})")

        db.commit()
        db.refresh(tenant)
        print(f"Tenant '{tenant.name}' created successfully.")
    else:
        print(f"Tenant '{tenant.name}' with subdomain '{tenant.subdomain}' already exists.")

    # 2. Find or Create the Admin User for this Tenant
    admin_user = user_service.get_user_by_email(db, email=ADMIN_EMAIL)
    if not admin_user:
        print(f"Creating admin user '{ADMIN_EMAIL}' for tenant '{tenant.name}'...")
        user_in = UserCreate(email=ADMIN_EMAIL, password=ADMIN_PASSWORD)
        user_service.create_user(db, user_in, UserRole.ADMIN, tenant.id)
        print("Admin user created successfully.")
    else:
        print(f"Admin user '{ADMIN_EMAIL}' already exists.")
    
    db.commit()
    print("\n--- Seeding Complete ---")
    print("Your local development environment is ready.")
    print("\nTo test API endpoints that require a tenant, use this header:")
    print(f"  X-Tenant-Subdomain: {DEFAULT_TENANT_SUBDOMAIN}")
    print("\nTo log in as the default admin, use these credentials:")
    print(f"  Username: {ADMIN_EMAIL}")
    print(f"  Password: {ADMIN_PASSWORD}")
    print("-------------------------\n")

finally:
    db.close()