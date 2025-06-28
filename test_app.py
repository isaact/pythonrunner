import pytest
import json
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    with app.test_client() as client:
        yield client

def test_successful_execution(client, monkeypatch):
    """Test a successful script execution."""
    # Mock the subprocess call to simulate a successful nsjail run
    class MockCompletedProcess:
        stdout = json.dumps({"result": {"status": "ok"}, "stdout": "Hello from stdout!"})
        stderr = ""
    
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: MockCompletedProcess())

    response = client.post("/execute", json={"script": "def main(): return {'status': 'ok'}"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == {"status": "ok"}
    assert data["stdout"] == "Hello from stdout!"

def test_missing_main_function(client):
    """Test script validation for missing main() function."""
    response = client.post("/execute", json={"script": "def not_main(): pass"})
    assert response.status_code == 400
    data = response.get_json()
    assert "must contain a 'main' function" in data["error"]

def test_missing_script_field(client):
    """Test request validation for missing 'script' field."""
    response = client.post("/execute", json={"other_field": "some_value"})
    assert response.status_code == 400
    data = response.get_json()
    assert "Missing 'script' in request body" in data["error"]

def test_nsjail_execution_error(client, monkeypatch):
    """Test handling of a failed nsjail execution."""
    class MockCompletedProcess:
        stdout = ""
        stderr = "nsjail: execution failed"

    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: MockCompletedProcess())

    response = client.post("/execute", json={"script": "def main(): return {'status': 'ok'}"})
    assert response.status_code == 500
    data = response.get_json()
    assert "An unexpected error occurred" in data["error"]
    assert "nsjail: execution failed" in data["details"]

def test_invalid_json_from_runner(client, monkeypatch):
    """Test handling of invalid JSON output from the runner script."""
    class MockCompletedProcess:
        stdout = "this is not json"
        stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: MockCompletedProcess())

    response = client.post("/execute", json={"script": "def main(): return {'status': 'ok'}"})
    assert response.status_code == 500
    data = response.get_json()
    assert "Runner script produced invalid JSON" in data["error"]