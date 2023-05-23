from datetime import datetime

from common.test_utils import client,admin_client



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