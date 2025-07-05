# backend/tests/api/v1/test_team_and_settings.py

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.security import UserRole
from tests.utils import create_tenant_and_admin, get_auth_headers

def test_admin_can_add_team_members(test_client: TestClient, db_session: Session):
    """
    USER STORY: As an MFI admin, I want to invite and assign roles to my team.
    """
    _, admin, password = create_tenant_and_admin(db_session)
    auth_headers = get_auth_headers(test_client, admin.email, password)

    # Add a loan officer
    loan_officer_data = {
        "email": "loanofficer@test.com", "password": "password123", "role": "loan_officer"
    }
    response = test_client.post("/api/v1/team/members", json=loan_officer_data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["role"] == UserRole.LOAN_OFFICER.value

    # Add a teller
    teller_data = {
        "email": "teller@test.com", "password": "password123", "role": "teller"
    }
    response = test_client.post("/api/v1/team/members", json=teller_data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["role"] == UserRole.TELLER.value

def test_admin_can_update_settings(test_client: TestClient, db_session: Session):
    """
    USER STORY: As an MFI admin, I want to configure loan rules...
    """
    _, admin, password = create_tenant_and_admin(db_session)
    auth_headers = get_auth_headers(test_client, admin.email, password)

    settings_data = { "currency": "UGX", "configurations": {"late_fee_grace_days": 5} }
    response = test_client.put("/api/v1/settings/", json=settings_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "UGX"
    assert data["configurations"]["late_fee_grace_days"] == 5

def test_admin_can_view_dashboard(test_client: TestClient, db_session: Session):
    """
    USER STORY: As an MFI admin, I want to see overall performance stats.
    """
    _, admin, password = create_tenant_and_admin(db_session)
    auth_headers = get_auth_headers(test_client, admin.email, password)
    
    response = test_client.get("/api/v1/reports/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_clients" in data
    assert "active_loans" in data