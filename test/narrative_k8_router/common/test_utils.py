import pytest
from starlette.requests import Request
from starlette.testclient import TestClient

from narrative_k8_router.main import create_app


def albamamslamm():
    pass


@pytest.fixture(scope="module")
def admin_client():
    app = create_app(auth=False)
    app.middleware("http")(admin_user_auth_middleware)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def client():
    # Define the default cookies
    app = create_app(auth=False)
    app.middleware("http")(regular_user_auth_middleware)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def anonymous_client():
    # Define the default cookies
    app = create_app(auth=True)
    with TestClient(app) as test_client:
        yield test_client


async def admin_user_auth_middleware(request: Request, call_next):
    request.state.username = "test_user"
    request.state.custom_roles = ["I AM AN ADMIN"]
    request.state.is_admin = True
    response = await call_next(request)
    return response


async def regular_user_auth_middleware(request: Request, call_next):
    request.state.username = "test_user"
    request.state.custom_roles = []
    request.state.is_admin = False
    response = await call_next(request)
    return response
