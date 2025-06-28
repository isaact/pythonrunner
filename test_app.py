import pytest
import json
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    with app.test_client() as client:
        yield client

def test_successful_execution(client):
    """Test a successful script execution with a simple return value."""
    script = "def main(): return {'status': 'ok'}"
    response = client.post("/execute", json={"script": script})
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == {"status": "ok"}
    assert data["stdout"] == ""

def test_execution_with_stdout(client):
    """Test a script that prints to stdout and returns a value."""
    script = "def main():\n  print('Hello from stdout!')\n  return {'data': 123}"
    response = client.post("/execute", json={"script": script})
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == {"data": 123}
    assert "Hello from stdout!" in data["stdout"]

def test_execution_with_pandas(client):
    """Test a script that uses an installed library (pandas)."""
    script = (
        "import pandas as pd\n"
        "def main():\n"
        "  df = pd.DataFrame([{'a': 1, 'b': 2}])\n"
        "  return df.to_dict()"
    )
    response = client.post("/execute", json={"script": script})
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == {"a": {"0": 1}, "b": {"0": 2}}

def test_script_with_error(client):
    """Test a script that raises an exception during execution."""
    script = "def main():\n  return 1 / 0"
    response = client.post("/execute", json={"script": script})
    assert response.status_code == 400
    data = response.get_json()
    assert "Failed to execute script" in data["error"]
    assert "ZeroDivisionError: division by zero" in data["details"]

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