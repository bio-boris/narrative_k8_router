import pytest
from fastapi import Request, HTTPException

from lib.auth import valid_user
from lib.config import get_settings


def test_narrative_status():
    r = Request
    r.cookies = {"kbase_session": "test-cookie-value"}
    s = get_settings()

    with pytest.raises(HTTPException) as e:
        valid_user(r,s.auth_url,s.admin_role)

    assert e.value.status_code == 401
    assert e.value.detail == "Invalid auth token or token has expired."


    with pytest.raises(HTTPException) as e:
        valid_user(r,s.auth_url + "something fake",s.admin_role)

    assert e.value.status_code == 401
    assert e.value.detail == "Something is wrong auth service or url is not valid"
