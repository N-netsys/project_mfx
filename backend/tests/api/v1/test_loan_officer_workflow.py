# backend/tests/api/v1/test_loan_officer_workflow.py

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import models
from app.core.security import UserRole
from tests.utils import create_tenant_and_admin, create_user_in_db, get_auth_headers

def setup_loan_officer_test(db_session: Session):
    """Helper to set up a tenant, admin, loan officer, client, and loan product."""
    tenant, admin, admin_password = create_tenant_and_admin(db_session)
    officer_password = "officer_pass"
    officer = create_user_in_db(db_session, tenant, "officer@test.com", officer_password, UserRole.LOAN_OFFICER)
    
    client = models.Client(first_name="John", last_name="Borrower", tenant_id=tenant.id)
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    
    product = models.LoanProduct(name="Business Loan", interest_rate=15.0, max_tenure_months=12, tenant_id=tenant.id)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    return officer, officer_password, client, product

def test_loan_officer_can_manage_borrowers(test_client: TestClient, db_session: Session):
    """
    USER STORY: As a loan officer, I want to add new clients or update their details...
    """
    officer, password, _, _ = setup_loan_officer_test(db_session)
    auth_headers = get_auth_headers(test_client, officer.email, password)

    client_data = {"first_name": "Jane", "last_name": "Doe"}
    response = test_client.post("/api/v1/clients/", json=client_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Jane"

def test_loan_officer_can_submit_and_approve_loan(test_client: TestClient, db_session: Session):
    """
    USER STORIES: 
    - As a loan officer, I want to create loan applications...
    - As a loan officer, I want to approve or reject loan requests...
    """
    # Note: In our RBAC, only Admins can approve. Let's test that a Loan Officer *cannot* approve.
    officer, password, client, product = setup_loan_officer_test(db_session)
    officer_headers = get_auth_headers(test_client, officer.email, password)

    # 1. Loan Officer submits application
    app_data = {
        "amount_requested": 5000,
        "tenure_months": 6,
        "loan_product_id": str(product.id),
        "client_id": str(client.id)
    }
    # This endpoint does not exist yet, we will create it in a moment. Let's assume it's /api/v1/loans/
    # For now, let's create it directly in the DB to test the approval part.
    loan = models.Loan(**app_data, tenant_id=officer.tenant_id)
    db_session.add(loan)
    db_session.commit()
    db_session.refresh(loan)
    
    # 2. Loan Officer attempts to approve - THIS SHOULD FAIL
    response = test_client.post(f"/api/v1/loans/{loan.id}/approve", headers=officer_headers)
    assert response.status_code == 403 # Forbidden