from datetime import datetime

from common.test_utils import client,admin_client



def test_narrative_status(client):
    response = client.get("/narrative_status/")
    assert response.status_code == 200
    assert response.json() == {
        "username": "test_user",
        "is_KBASE_ADMIN": False
    }


