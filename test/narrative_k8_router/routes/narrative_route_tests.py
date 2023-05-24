from datetime import datetime
from unittest.mock import MagicMock, create_autospec

from common.test_utils import client, admin_client
from lib.config import get_settings
from kubernetes import client as k8s_client


def assertFixtures():
    assert client != admin_client


def test_narrative_status(client, admin_client, mocker):
    mock_client = create_autospec(k8s_client.CoreV1Api)
    mocker.patch(
        # api_call is from slow.py but imported to main.py
        "lib.k8_helper.get_k8s_client",
        return_value=mock_client,
    )

    # Set up any necessary return values or behaviors on the mock_client_instance

    response = client.get("/narrative_status/")
    settings = get_settings()
    expected_response = {
        "git_hash": settings.gitcommit,
        "narrative_services": [],
        "version": settings.version,
    }
    assert response.status_code == 200
    # assert len(response.json()) == len(expected_response) + 1  # Adding 1 to account for the "timestamp" key

    assert {k: v for k, v in response.json().items() if k != "timestamp"} == expected_response


def test_narrative_endpoint(client, admin_client, mocker):
    mock_client = create_autospec(k8s_client.CoreV1Api)
    mocker.patch(
        # api_call is from slow.py but imported to main.py
        "lib.k8_helper.get_k8s_client",
        return_value=mock_client,
    )

    response = client.get("/narrative/147008")
    assert response.json() == {}
