from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """
    Tests the main health check endpoint.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Welcome to MFI-SaaS API v1.0.0"}