from datetime import datetime

from common.test_utils import client, admin_client, anonymous_client
from lib.config import get_settings


def assertFixtures():
    assert client != admin_client != anonymous_client


def test_whoami(client, admin_client, anonymous_client):
    tests = [
        (client, {"status_code": 200, "json": {"username": "test_user", "is_KBASE_ADMIN": False}}),
        (admin_client, {"status_code": 200, "json": {"username": "test_user", "is_KBASE_ADMIN": True}}),
        (anonymous_client, {"status_code": 401, "json": {"detail": "kbase_session cookie is missing. unable to authenticate."}}),
    ]

    for client, expected_response in tests:
        response = client.get("/whoami/")
        assert response.status_code == expected_response["status_code"]
        assert response.json() == expected_response["json"]


def test_status(client, admin_client, anonymous_client):
    for c in [client, admin_client, anonymous_client]:
        response = c.get("/status")
        settings = get_settings()

        assert response.status_code == 200

        expected_response = {
            "version": settings.version,
            "vcs-ref": settings.gitcommit,
            "auth_url": settings.auth_url,
            "admin_role": settings.admin_role,
            "k8-namespace": settings.namespace,
        }
        assert response.status_code == 200
        assert len(response.json()) == len(expected_response) + 1  # Adding 1 to account for the "timestamp" key

        assert {k: v for k, v in response.json().items() if k != "timestamp"} == expected_response
