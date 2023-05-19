import requests
from fastapi import HTTPException
from fastapi import Request

KBASE_SESSION_COOKIE = "kbase_session"


def whoami_helper(request: Request):
    return {"username": request.state.username, "is_KBASE_ADMIN": request.state.is_admin}


def valid_user(request: Request, auth_url: str, admin_role: str):
    token = request.cookies.get("kbase_session")

    if not token:
        raise HTTPException(status_code=401, detail="kbase_session cookie is missing. unable to authenticate.")

    response = requests.get(auth_url, headers={'Authorization': token})

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail=f"Invalid auth token or token has expired.")
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail=f"Something is wrong auth service or url is not valid")

    data = response.json()
    username = data.get("user")
    custom_roles = data.get("customroles", [])
    is_admin = admin_role in custom_roles

    # Save user attributes in request.state for later use
    request.state.username = username
    request.state.custom_roles = custom_roles
    request.state.is_admin = is_admin


def get_auth_status(request, auth_url, admin_role):
    auth_status = dict()
    if KBASE_SESSION_COOKIE not in request.cookies:
        auth_status['error'] = 'no_cookie'
    else:
        token = request.cookies[KBASE_SESSION_COOKIE]
        try:
            r = requests.get(auth_url, headers={'Authorization': token})
            authresponse = r.json()
            if r.status_code == 200:
                auth_status['userid'] = authresponse['user']
                auth_status['customroles'] = authresponse['customroles']
            else:
                auth_status['error'] = 'auth_error'
                auth_status['message'] = authresponse['error']['message']
        except Exception as err:
            auth_status['error'] = "request_error"
            auth_status['message'] = repr(err)


def valid_request(request: Request) -> str:
    """
    Validate request has a legit auth token and return a dictionary that has a userid field if
    it is legit, otherwise return the error type in the error field
    """

    return (auth_status)
