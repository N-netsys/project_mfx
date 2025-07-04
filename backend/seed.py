import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import tenant as tenant_model
from app.models import user as user_model
from app.services import user_service
from app.schemas.user import UserCreate
from app.core.config import settings
from dotenv import load_dotenv

# Load environment variables to ensure settings are available
load_dotenv()

print("Seeding initial data...")

# Create a new database session
db: Session = SessionLocal()

try:
    # --- Create Tenant ---
    # Check if the default tenant already exists
    tenant_name = "Default MFI"
    db_tenant = db.query(tenant_model.Tenant).filter(tenant_model.Tenant.name == tenant_name).first()
    
    if not db_tenant:
        print(f"Creating tenant: {tenant_name}")
        db_tenant = tenant_model.Tenant(name=tenant_name)
        db.add(db_tenant)
        db.commit()
        db.refresh(db_tenant)
        print("Tenant created successfully.")
    else:
        print(f"Tenant '{tenant_name}' already exists.")

    # --- Create Admin User ---
    # Check if the admin user already exists
    admin_email = "admin@example.com"
    db_user = user_service.get_user_by_email(db, email=admin_email)

    if not db_user:
        print(f"Creating admin user with email: {admin_email}")
        user_in = UserCreate( # CORRECT: Use UserCreate directly
            email=admin_email,
            password="adminpassword",
            role="admin",
            tenant_id=db_tenant.id
        )
        user_service.create_user(db, user=user_in)
        print("Admin user created successfully.")
        print("---")
        print("Login credentials:")
        print(f"  Email: {admin_email}")
        print(f"  Password: adminpassword")
        print("---")
    else:
        print(f"Admin user with email '{admin_email}' already exists.")
        
    print("Seeding complete.")

finally:
    db.close()