import os

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from old.main import app

app.authenticated = True


@pytest.fixture
def mock_valid_user():
    # Create a MagicMock object to mock the behavior of valid_user
    mock = MagicMock()
    mock.return_value = None  # Modify the behavior of the mock as needed
    return mock


@pytest.fixture(scope="module")
def client():
    # Define the default cookies
    default_cookies = {"kbase_session": "test-cookie-value"}

    # Create the TestClient with default cookies
    with TestClient(app) as test_client:
        test_client.cookies.update(default_cookies)
        yield test_client


def requests_mock_helper(rq,admin=False):
    auth_url = os.environ.get("AUTH_URL", "https://ci.kbase.us/services/auth/api/V2/me")
    user = {'user': 'test_user', 'custom_roles': []}
    if admin:
        user['custom_roles'] = ['KBASE_ADMIN']
    rq.get(auth_url, json=user)  # Update the json parameter



def test_whoami(requests_mock, client):
    requests_mock_helper(requests_mock, admin=True)

    response = client.get("/whoami/")
    assert response.status_code == 200
    assert response.json() == {'is_KBASE_ADMIN': False, 'username': 'test_user'}

    requests_mock_helper(requests_mock,admin=True)
    response = client.get("/whoami/")
    assert response.status_code == 200
    assert response.json() == {'is_KBASE_ADMIN': True, 'username': 'test_user'}



def test_status(client):
    response = client.get("/status")
    assert response.status_code == 200
    assert "timestamp" in response.json()
    assert "version" in response.json()
    assert "git_hash" in response.json()


def test_narrative_status(client):
    response = client.get("/narrative_status")
    assert response.status_code == 200
    # Add assertions for the expected response JSON


def test_start_container(client):
    container_req = {
        "container_name": "test-container",
        "container_image": "test-image",
        "container_command": "echo",
        "container_args": "Hello, World!"
    }
    response = client.post("/start_container", json=container_req)
    assert response.status_code == 200
    assert response.json() == {"message": "Container test-container started in namespace staging-narrative"}


def test_hello(client):
    narrative = "test-narrative"
    response = client.get(f"/narrative/{narrative}")
    assert response.status_code == 200
    # Add assertions for the expected response
