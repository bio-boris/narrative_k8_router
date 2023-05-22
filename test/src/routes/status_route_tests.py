import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from datetime import datetime
from narrative_k8_router.main import create_app

async def regular_user_auth_middleware(request: Request, call_next):
    request.state.username = "test_user"
    request.state.custom_roles = []
    request.state.is_admin = False
    response = await call_next(request)
    return response

async def admin_user_auth_middleware(request: Request, call_next):
    request.state.username = "test_user"
    request.state.custom_roles = ["I AM AN ADMIN"]
    request.state.is_admin = True
    response = await call_next(request)
    return response



@pytest.fixture(scope="module")
def client():
    # Define the default cookies
    app = create_app(auth=False)
    app.middleware("http")(regular_user_auth_middleware)
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="module")
def admin_client():
    app = create_app(auth=False)
    app.middleware("http")(admin_user_auth_middleware)
    with TestClient(app) as test_client:
        yield test_client




def test_whoami(client,admin_client ):
    response = client.get("/whoami/")
    assert response.status_code == 200
    assert response.json() == {
        "username": "test_user",
        "is_KBASE_ADMIN": False
    }

    response = admin_client.get("/whoami/")
    assert response.status_code == 200
    assert response.json() == {
        "username": "test_user",
        "is_KBASE_ADMIN": True
    }


def test_status(client):
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {
        "timestamp": datetime.now().isoformat(),
        "version": "your_version",
        "vcs-ref": "your_gitcommit",
        "auth_url": "your_auth_url",
        "admin_role": "your_admin_role",
        "k8-namespace": "your_namespace"
    }