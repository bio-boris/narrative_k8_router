import logging
import random
from typing import Optional, Dict

from fastapi.responses import RedirectResponse, Response
from fastapi.requests import Request


from lib.config import get_settings
from lib.k8_helper import start_container


def error_response(auth_status: Dict[str, str], request: Request) -> Response:
    """
    Return an flask response that is appropriate for the message in the auth_status dict.
    """
    pass
    # resp = flask.Response(errors[auth_status["error"]])
    # if auth_status["error"] == "no_cookie":
    #     resp = flask.Response(errors["no_cookie"])
    #     resp.status_code = 401
    # elif auth_status["error"] == "auth_error":
    #     resp = flask.Response(errors["auth_error"] + auth_status["message"])
    #     resp.status_code = 403
    # elif auth_status["error"] == "request_error":
    #     resp = flask.Response(errors["request_error"] + auth_status["message"])
    #     resp.status_code = 403
    # else:
    #     resp = flask.Response(errors["other"] + auth_status["message"])
    #     resp.status_code = 400
    # client_ip = request.headers.get("X-Real-Ip", request.headers.get("X-Forwarded-For", None))
    # logger.info({"message": "auth_error", "client_ip": client_ip, "error": auth_status["error"], "detail": auth_status.get("message", "")})
    # return resp


def check_session(userid: str) -> str:
    """
    Check to see if we already have a container for this user by trying to pull the container object
    for the userid
    """
    # You cannot rename containers, so check labels for username instead, and get the session id from there




    # try:
    #     name = cfg["container_name"].format(userid)
    #     container = client.containers.get(name)
    #     session_id = container.labels["session_id"]
    # except docker.errors.NotFound:
    #     session_id = None
    # except docker.errors.APIErrors as err:
    #     msg = "Docker APIError thrown while searching for container name {} : {}".format(name, str(err))
    #     logger.error({"message": msg, "container_name": name, "exception": str(err)})
    #     session_id = None
    # return session_id


def redirect(request):
    """
    If no cookie is set, force the user to login!
    """
    settings = get_settings()
    next_request = '{{"path":"{}","external":true}}'.format(request.url.path)
    logging.info({"message": "Redirecting user for no_cookie", "nextrequest": request.url})


def get_container(request: Request, narrative_identifier: str, settings=get_settings()) -> Response:
    """
    Given the request object and the username from validating the token, either find or spin up
    the narrative container that should handle this user's narrative session. The narrative
    parameter is the path to the requested narrative from the original URL. Return a flask response
    object that contains the necessary cookie for traefik to use for routing, as well as a brief
    message that reloads the page so that traefik reroutes to the right place
    """
    # See if there is an existing session for this user, if so, reuse it
    logging.critical("77")
    userid = request.state.cleaned_username
    session = check_session(userid)
    client_ip = request.headers.get("X-Real-Ip", request.headers.get("X-Forwarded-For", None))
    load_narrative_redirect = RedirectResponse(f"/load-narrative.html?n={narrative_identifier}&check=true")


    if session is None:
        load_narrative_redirect, session = new_narrative_session(client_ip, load_narrative_redirect, request, userid)
        logging.critical("86")

    if session is not None:
        logging.critical("87")
        cookie = f"{settings.narrative_session_cookie}={session}"
        logging.debug({"message": "session_cookie", "userid": userid, "client_ip": client_ip, "cookie": cookie})
        load_narrative_redirect.set_cookie(key=settings.narrative_session_cookie, value=session)

    logging.critical(load_narrative_redirect)
    return load_narrative_redirect


def new_narrative_session(client_ip, load_narrative_redirect, request, userid):
    logging.debug({"message": "new_session", "userid": userid, "client_ip": client_ip})

    try:
        # Try to get a narrative session, the session value returned is the one that has been assigned to the
        # userid. The second value is whether or not the session is to a prespawned container, no wait is necessary
        session = start(userid, client_ip, prespawn=True)


    except Exception as err:
        logging.critical({"message": "start_container_exception", "userid": userid, "client_ip": client_ip, "exception": repr(err)})
        load_narrative_redirect = error_response({"error": "other", "message": repr(err)}, request)
        session = None
    return load_narrative_redirect, session


def start(userid: str, client_ip: str, prespawn: bool = False) -> Dict[str, str]:
    """
    wrapper around the start_new function that checks to see if there are waiting narratives that
    can be assigned. Note that this method is subject to race conditions by competing workers, so we
    have 5 retries, and try to select a random waiting narrative before just spawning a new one. Someday maybe
    we can implement something to serialize selecting narratives for assignment, but that's a ToDo item.
    """
    session = random.getrandbits(128).to_bytes(16, "big").hex()

    if prespawn is True:
        start_new(session, userid, client_ip, True)
    # else:
    #     prespawned = find_prespawned()
    #     # The number of prespawned should be pretty stable around cfg['num_prespawn'], but during a
    #     # usage there might be spike that exhausts the pool of ready containers before replacements
    #     # are available.
    #     if len(prespawned) > 0:
    #         # if we're not already over the num)prespawn setting then
    #         # spawn a replacement and immediately rename an existing container to match the
    #         # userid. We are replicating the prespawn container name code here, maybe cause
    #         # issues later on if the naming scheme is changed!
    #         if len(prespawned) <= cfg['num_prespawn']:
    #             start_new(session, session[0:6], True)
    #         narr_name = cfg['container_name'].format(userid)
    #         offset = random.randint(0, len(prespawned)-1)
    #         session = None
    #         # Try max(5, # of prespawned) times to use an existing narrative, on success assign the session and break
    #         for attempt in range(max(5, len(prespawned))):
    #             candidate = prespawned[(offset+attempt) % len(prespawned)]
    #             try:
    #                 rename_narrative(candidate, narr_name)
    #                 container = find_service(narr_name)
    #                 session = container['launchConfig']['labels']['session_id']
    #                 logger.info({"message": "assigned_container", "userid": userid, "service_name": narr_name, "session_id": session,
    #                              "client_ip": "127.0.0.1", "attempt": attempt, "status": "success"})
    #                 break
    #             except Exception as ex:
    #                 logger.info({"message": "assigned_container_fail", "userid": userid, "service_name": narr_name, "session_id": session,
    #                              "client_ip": "127.0.0.1", "attempt": attempt, "status": "fail", "error": str(ex)})
    #         if session:
    #             return({"session": session, "prespawned": True})
    #         else:
    #             # Well, that was a bust, just spin up one explicitly for this user. Maybe we hit a race condition where all of the
    #             # cached containers have been assigned between when we queried and when we tried to rename it.
    #             # ToDo: need to write a pool watcher thread that wakes up periodically to make sure the number of prespawned
    #             # narratives are still at the desired level. Shouldn't be needed since there should be a 1:1 between assigning
    #             # and spawning replacements, but errors happen
    #             logger.debug({"message": "could not assign prespawned container, calling start_new", "userid": userid, "session_id": session})
    #             return({"session": start_new(session, userid, False)})
    #     else:
    #         return({"session": start_new(session, userid, False)})


def start_new(session: str, userid: str, client_ip: str, prespawn: Optional[bool] = False):
    """
    Attempts to start a new container using the rancher API. Signature is identical to the start_docker
    method, with the equivalent rancher exceptions.
    """
    # Crazy long config needed for rancher container startup. Based on observing the traffic from rancher
    # GUI to rancher REST APIs. Might be able to prune it down with some research

    start_container(username=userid, session_id=session, client_ip=client_ip, prespawn=prespawn)

    # # Attempt to bring up a container, if there is an unrecoverable error, clear the session variable to flag
    # # an error state, and overwrite the response with an error response
    # try:
    #     r = requests.post(cfg["rancher_env_url"] + "/service", json=container_config, auth=(cfg["rancher_user"], cfg["rancher_password"]))
    #     logger.info(
    #         {"message": "new_container", "image": imageUuid, "userid": userid, "service_name": name, "session_id": session, "client_ip": client_ip}
    #     )  # request.remote_addr)
    #     if not r.ok:
    #         msg = "Error - response code {} while creating new narrative rancher service: {}".format(r.status_code, r.text)
    #         logger.error({"message": msg})
    #         raise (Exception(msg))
    # except Exception as ex:
    #     raise (ex)
    # return session
