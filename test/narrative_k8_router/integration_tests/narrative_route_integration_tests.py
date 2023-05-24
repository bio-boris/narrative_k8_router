from datetime import datetime
from unittest.mock import MagicMock, create_autospec

from common.test_utils import anonymous_client
from lib.config import get_settings
from kubernetes import client as k8s_client


def test_narrative_endpoint(anonymous_client, mocker):

    anonymous_client.cookies.set("kbase_session", "2RHNCJ754OWESIT5ONVVYHTE5XXJC66V")
    response = anonymous_client.get("/narrative/147008")
    assert response.json() == {}
