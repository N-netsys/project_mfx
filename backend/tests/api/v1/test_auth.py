# backend/tests/api/v1/test_auth.py

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import models
from app.core.security import UserRole

def test_register_organization(test_client: TestClient, db_session: Session):
    """
    USER STORY: As an MFI admin, I want to register my SACCO/organization.
    """
    org_data = {
        "organization_name": "Test MFI",
        "admin_email": "testadmin@testmfi.com",
        "admin_password": "a_very_secure_password"
    }
    response = test_client.post("/api/v1/auth/register-organization", json=org_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == org_data["admin_email"]
    assert data["role"] == UserRole.ADMIN.value
    
    # Verify in DB
    user_in_db = db_session.query(models.User).filter(models.User.email == org_data["admin_email"]).first()
    assert user_in_db is not None
    assert user_in_db.tenant is not None
    assert user_in_db.tenant.name == org_data["organization_name"]

def test_login_for_access_token(test_client: TestClient, db_session: Session):
    """Tests the /token endpoint for all user roles."""
    from tests.utils import create_tenant_and_admin
    
    tenant, _, password = create_tenant_and_admin(db_session)
    
    login_data = {"username": "main.admin@test.com", "password": password}
    response = test_client.post("/api/v1/auth/token", data=login_data)
    assert response.status_code == 200
    token = response.json()
    assert "access_token" in token
    assert token["token_type"] == "bearer"

def test_read_current_user(test_client: TestClient, db_session: Session):
    """Tests the /me endpoint to verify token authentication."""
    from tests.utils import create_tenant_and_admin, get_auth_headers

    _, admin, password = create_tenant_and_admin(db_session)
    auth_headers = get_auth_headers(test_client, admin.email, password)
    
    response = test_client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == admin.email
    assert data["id"] == str(admin.id)