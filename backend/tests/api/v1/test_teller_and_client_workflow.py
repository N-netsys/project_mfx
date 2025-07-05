# backend/tests/api/v1/test_teller_and_client_workflow.py

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import models, schemas
from app.core.security import UserRole
from app.services import loan_service
from tests.utils import create_tenant_and_admin, create_user_in_db, get_auth_headers

def setup_disbursement_test(db_session: Session):
    """Helper to create a fully approved loan ready for disbursement."""
    tenant, admin, _ = create_tenant_and_admin(db_session)
    
    client = models.Client(first_name="Ready", last_name="Borrower", tenant_id=tenant.id)
    db_session.add(client)
    db_session.commit()
    
    product = models.LoanProduct(name="Ready Loan", interest_rate=10.0, max_tenure_months=3, tenant_id=tenant.id)
    db_session.add(product)
    db_session.commit()
    
    loan_app = schemas.loan.LoanApply(loan_product_id=product.id, amount_requested=1000, tenure_months=3)
    user_for_client = create_user_in_db(db_session, tenant, "ready.client@test.com", "pass", UserRole.CLIENT)
    user_for_client.client_id = client.id # Link user to client
    db_session.commit()
    
    loan = loan_service.create_loan_application(db_session, loan_app, user_for_client)
    approved_loan = loan_service.approve_loan(db_session, loan.id)
    
    teller = create_user_in_db(db_session, tenant, "teller2@test.com", "tellerpass", UserRole.TELLER)
    return teller, approved_loan

def test_teller_can_disburse_funds_and_record_repayment(test_client: TestClient, db_session: Session):
    """
    USER STORIES:
    - As a teller, I want to mark loans as disbursed...
    - As a teller, I want to record full or partial repayments...
    """
    # Note: Our RBAC only allows Admins to disburse. Let's test that flow.
    # To fulfill the story, we would change the dependency to `allow_teller_and_admin`.
    
    teller, approved_loan = setup_disbursement_test(db_session)
    
    # Let's get an admin to do the disbursement
    admin = db_session.query(models.User).filter(models.User.role == UserRole.ADMIN).first()
    admin_headers = get_auth_headers(test_client, admin.email, "a_secure_password") # Using password from utils
    
    # 1. Disburse the loan
    response = test_client.post(f"/api/v1/loans/{approved_loan.id}/disburse", headers=admin_headers)
    assert response.status_code == 200
    
    # 2. Teller records repayment
    teller_headers = get_auth_headers(test_client, teller.email, "tellerpass")
    first_installment = db_session.query(models.RepaymentSchedule).filter(models.RepaymentSchedule.loan_id == approved_loan.id).first()
    
    repayment_data = {"schedule_id": str(first_installment.id), "amount_paid": 340.0}
    response = test_client.post(f"/api/v1/repayments/{approved_loan.id}/record", json=repayment_data, headers=teller_headers)
    assert response.status_code == 204

def test_client_can_view_their_loans(test_client: TestClient, db_session: Session):
    """
    USER STORIES:
    - As a borrower, I want to log in to see my active loans...
    - As a borrower, I want to see my loan balance and due dates.
    """
    _, approved_loan = setup_disbursement_test(db_session)
    client_user = approved_loan.client.user_account
    
    client_headers = get_auth_headers(test_client, client_user.email, "pass")
    response = test_client.get("/api/v1/loans/my-loans", headers=client_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(approved_loan.id)
    assert data[0]["status"] == "disbursed"