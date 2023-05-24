from unittest.mock import MagicMock

import pytest
from fastapi import Request, HTTPException

from lib.auth import valid_user
from lib.config import get_settings


def test_narrative_status(mocker):
    r = Request
    r.cookies = {"kbase_session": "test-cookie-value"}
    r.json = MagicMock(return_value={"user": "test_user", "custom_roles": []})

    s = get_settings()

    with pytest.raises(HTTPException) as e:
        valid_user(r, s.auth_url, s.admin_role)

    assert e.value.status_code == 401
    assert e.value.detail == "Invalid auth token or token has expired."

    with pytest.raises(HTTPException) as e:
        valid_user(r, s.auth_url + "something fake", s.admin_role)

    assert e.value.status_code == 401
    assert e.value.detail == "Something is wrong auth service or url is not valid"

    # # Create a mock Response object with status_code = 200
    # mock_response = Response()
    # mock_response.status_code = 200
    #
    # # Create a dictionary to be returned by the patched requests.get function
    # mock_data = {"user": "abc", "custom_roles": []}
    #
    # # Mock the requests.get function and set its return value as the mock_response with the mock_data
    # mocker.patch("lib.auth.requests.get", return_value=mock_response)
    # mocker.patch.object(mock_response, "json", return_value=mock_data)
    #
    # valid_user(r, s.auth_url + "something fake", s.admin_role)
