import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "ok" 

def test_fastapi():
    response = client.get("/does-not-exist")
    
    assert response.status_code == 404
    
def test_ready_endpoint_success():
    response = client.get("/ready")
    
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "Solver exists, is a file and is executable and DB is connectable."

def test_ready_endpoint_failure_solver(monkeypatch):
    monkeypatch.setattr("backend.app.api.health.check_solver", fake_check_solver)
    response = client.get("/ready")
    
    assert response.status_code == 503
    assert response.json()["detail"] == "Solver is missing."
    
def test_ready_endpoint_failure_db(monkeypatch):
    monkeypatch.setattr("backend.app.api.health.session.check_db_connectivity", fake_check_db)
    response = client.get("/ready")
    
    assert response.status_code == 503
    assert response.json()["detail"] == "DB is missing."
    
def fake_check_solver():
        raise RuntimeError("Solver is missing.")
def fake_check_db():
        raise RuntimeError("DB is missing.")
