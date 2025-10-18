import pytest
# Importing as flask_app to avoid naming conflicts with other 'app' instances in tests
from resume_checker_ollama.app import app as flask_app

@pytest.fixture
def client():
    with flask_app.test_client() as client:
        yield client


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


def test_about(client):
    response = client.get("/about")
    assert response.status_code == 200
