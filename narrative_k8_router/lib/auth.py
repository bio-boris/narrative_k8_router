import traceback

import requests
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from lib.config import get_settings

KBASE_SESSION_COOKIE = "kbase_session"


# One day fastapi will support route based middleware
# See https://github.com/tiangolo/fastapi/issues/1174
# See https://github.com/tiangolo/fastapi/discussions/7691
unauthenticated_endpoints = ["/status", "/docs", "/openapi.json", "/redoc"]


async def authenticator_middleware(request: Request, call_next):
    settings = get_settings()
    try:
        if request.url.path not in unauthenticated_endpoints:
            valid_user(
                request,
                auth_url=settings.auth_url,
                admin_role=settings.admin_role,
            )
        response = await call_next(request)
        return response
    except HTTPException as e:
        return JSONResponse({"detail": e.detail}, status_code=e.status_code)
    except Exception as e:
        error_message = traceback.format_exc()

        return JSONResponse({"detail": str(e), "exception": error_message}, status_code=500)


def valid_user(request: Request, auth_url: str, admin_role: str):
    """
    # TODO - REUSE THE COOKIE and CACHE THE RESPONSE?
    :param request: Request to intercept and mutate
    :param auth_url: The auth url to use for authentication
    :param admin_role: The admin role to check for admin status
    :return:
    """
    token = request.cookies.get("kbase_session")

    # TODO May need to update this to do a redirect to the login page
    if not token:
        raise HTTPException(
            status_code=401,
            detail="kbase_session cookie is missing. unable to authenticate.",
        )

    response = requests.get(auth_url, headers={"Authorization": token})

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail=f"Invalid auth token or token has expired.")
    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail=f"Something is wrong auth service or url is not valid",
        )

    data = response.json()
    username = data.get("user")
    custom_roles = data.get("customroles", [])
    is_admin = admin_role in custom_roles

    # Save user attributes in request.state for later use
    request.state.username = username
    request.state.custom_roles = custom_roles
    request.state.is_admin = is_admin

    return request
