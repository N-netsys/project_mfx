# backend/tests/utils.py

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import models, schemas
from app.core.security import UserRole
from app.services import user_service

def get_auth_headers(test_client: TestClient, email: str, password: str) -> dict:
    """Helper function to log in and get auth headers."""
    login_data = {"username": email, "password": password}
    response = test_client.post("/api/v1/auth/token", data=login_data)
    assert response.status_code == 200, f"Failed to log in user {email}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def create_user_in_db(db: Session, tenant: models.Tenant, email: str, password: str, role: UserRole) -> models.User:
    """Helper function to create a user directly in the database."""
    user_in = schemas.user.UserCreate(email=email, password=password)
    user = user_service.create_user(db, user_in, role, tenant.id)
    return user

def create_tenant_and_admin(db: Session) -> tuple[models.Tenant, models.User, str]:
    """Helper fixture to create a tenant and an admin user, returning them."""
    password = "a_secure_password"
    tenant = models.Tenant(name="Test Tenant Inc.")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    admin = create_user_in_db(db, tenant, "main.admin@test.com", password, UserRole.ADMIN)
    return tenant, admin, password