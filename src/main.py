import logging
import os
import traceback
from datetime import datetime
from typing import Dict

from fastapi import FastAPI, Response, Depends
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from kubernetes.client import models
from kubernetes.client.rest import ApiException
from typing_extensions import Annotated

from lib.k8_helper import k8s_client, get_active_narrative_containers
from lib import config
from lib.auth import whoami_helper, valid_user
from lib.models import ContainerRequest
from lib.config import get_settings




logging.basicConfig()
app = FastAPI()
# app.add_middleware(KBaseAuth, some_attribute="some_attribute_here_if_needed")

# from fastapi.exception_handlers import (
#     http_exception_handler,
#     request_validation_exception_handler,
# )



unauthenticated_endpoints = ["/status", "/docs", "/openapi.json", "/redoc"]


@app.middleware("http")
async def authenticated(request: Request, call_next):
    settings = get_settings()

    try:
        if request.url.path not in unauthenticated_endpoints:
            valid_user(request, auth_url=settings.auth_url, admin_role=settings.admin_role)
        response = await call_next(request)
        return response
    except HTTPException as e:
        return JSONResponse({"detail": e.detail}, status_code=e.status_code)
    except Exception as e:
        error_message = traceback.format_exc()

        return JSONResponse({"detail": str(e), "exception": error_message}, status_code=500)

        # return JSONResponse({"detail": f"Authentication failed {dir(e)}", }, status_code=500)


@app.get("/whoami/")
def whoami(request: Request):
    return JSONResponse(whoami_helper(request), status_code=200)


@app.get("/status")
def status():
    # TODO Figure out how to populate this with the correct information
    # Maybe env vars
    response_data = {
        "timestamp": datetime.now().isoformat(),
        "version": "0.10.1",
        "git_hash": "a4e1243"
    }
    return JSONResponse(response_data, status_code=200)


@app.get("/narrative_status")
def narrative_status(request: Request, settings: Annotated[config.Settings, Depends(get_settings)]) :
    """
    Simple status endpoint to re-assure us that the service is alive. Unauthenticated access just returns
    a 200 code with the current time in JSON string. If a kbase auth cookie is found, and the username is in the
    list of ID's in cfg['status_users'] then a dump of the current narratives running and their last
    active time from narr_activity is returned in JSON form, easily sent to elasticsearch for ingest, roughly
    matching the old proxy_map output from original OpenRest lua code
    """
    return get_active_narrative_containers()

    # logger.info({"message": "Status query received"})

    # Get narr_activity from the database
    # not currently used but may use in the future
    # try:
    #    narr_activity = get_narr_activity_from_db()
    # except Exception as e:
    #    logger.critical({"message": "Could not get narr_activity data from database: {}".format(repr(e))})
    #    return

    # resp_doc = {"timestamp": datetime.now().isoformat(), "version": VERSION, "git_hash": cfg['COMMIT_SHA']}
    # request = flask.request
    # auth_status = valid_request(request)
    # logger.debug({"message": "Status query received", "auth_status": auth_status})
    # if 'userid' in auth_status:
    #     if cfg['status_role'] in auth_status['customroles']:
    #         resp_doc['narrative_services'] = narrative_services()
    #     else:
    #         logger.debug({"message": "{} roles does not contain {}".format(auth_status['userid'], cfg['status_role']),
    #                       "customroles": str(auth_status['customroles'])})
    # return (flask.Response(json.dumps(resp_doc), 200, mimetype='application/json'))


@app.post(
    "/start_container", response_model=Dict[str, str], summary="Start a container"
)
async def start_container(container_req: ContainerRequest):
    """
    Start a container in the Kubernetes cluster.

    Args:
        container_req: ContainerRequest model containing container details.

    Returns:
        A dictionary with a success message.

    Raises:
        HTTPException: If there is an error starting the container.
    """
    # Get namespace from environmental variable
    namespace = os.environ.get("KUBERNETES_NAMESPACE", "staging-narrative")

    # Create container definition
    container = models.V1Container(
        name=container_req.container_name,
        image=container_req.container_image,
        command=container_req.container_command.split(),
        args=container_req.container_args.split(),
    )

    # Create pod definition
    pod = models.V1Pod(
        metadata=models.V1ObjectMeta(name=container_req.container_name),
        spec=models.V1PodSpec(containers=[container]),
    )

    try:
        # Create pod in namespace on Kubernetes cluster
        k8s_client.create_namespaced_pod(body=pod, namespace=namespace)
        return {
            "message": f"Container {container_req.container_name} started in namespace {namespace}"
        }
    except ApiException as e:
        if e.status == 409:
            raise HTTPException(
                status_code=409, detail="Conflict: Container already exists"
            )
        else:
            raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/narrative/{narrative:path}")
async def hello(narrative: str) -> Response:
    """
    Main handler for the auth service. Validates the request, retrieves the container that it should be routed to,
    and returns a response that will result in Traefik routing to the right place for subsequent requests.
    Returns an error in the response if requirements are not met or if an error occurs.
    """
    request = Request
    auth_status = valid_request(request)

    if "userid" in auth_status:
        resp = get_container(
            auth_status["userid"], request, narrative
        )  # replace with appropriate function
    else:
        if auth_status["error"] == "no_cookie":
            next_request = '{{"path":"{}","external":true}}'.format(request.url.path)
            logging.debug(
                {
                    "message": "Redirecting user for no_cookie",
                    "nextrequest": request.url,
                }
            )
            return Response(
                status_code=302,
                headers={"Location": f"/#login?nextrequest={next_request}"},
            )
        else:
            raise HTTPException(
                status_code=401, detail="Valid KBase authentication token required"
            )

    return resp

#
# def valid_request(request: Request) -> Dict[str, str]:
#     """
#     Validate the request and return the authentication status
#     """
#     # Implementation of valid_request function
#
#
# def clean_userid(dirty_user: str) -> str:
#     """
#     Clean the user ID
#     """
#     # Implementation of clean_userid function
#
#
# def check_session(userid: str) -> str:
#     """
#     Check for an active session for the given user ID
#     """
#     # Implementation of check_session function
#
#
# def reap_narrative(name: str) -> None:
#     """
#     Delete the narrative service using the Rancher API
#     """
#     # Implementation of reap_narrative function
#
#
# def delete_from_narr_activity_db(narr_activity: str) -> None:
#     """
#     Delete the narrative from the narr_activity database
#     """
#     # Implementation of delete_from_narr_activity_db function
#
#
# def get_narr_activity_from_db() -> Dict[str, str]:
#     """
#     Get the narr_activity data from the database
#     """
#     # Implementation of get_narr_activity_from_db function
#
#
# def find_narratives() -> List[str]:
#     """
#     Find the list of narrative container descriptors
#     """
#     # Implementation of find_narratives function
#
#
# def find_service(name: str) -> Dict[str, str]:
#     """
#     Find the service details for the given name
#     """
#     # Implementation of find_service function
#
#
# def stack_suffix() -> str:
#     """
#     Get the stack suffix
#     """
#     # Implementation of stack_suffix function
#
#
# @app.delete("/narrative_shutdown/")
# @app.delete("/narrative_shutdown/{username:path}")
# async def narrative_shutdown(username: str = None) -> Response:
#     """
#     This handler takes a request, looks for an auth token, and if both are present,
#     it looks for sessions associated with that user ID and calls the Rancher API to delete those services.
#     Returns a 401 error if there isn't an auth token. If there is an auth token,
#     it tries to delete all the sessions associated with that user ID.
#     """
#     request = Request
#     auth_status = valid_request(request)
#     logging.info(
#         {"message": "narrative_shutdown called", "auth_status": str(auth_status)}
#     )
#
#     if "userid" in auth_status:
#         dirty_user = auth_status["userid"]
#         userid = clean_userid(dirty_user)
#         session_id = check_session(userid)
#         logging.debug({"message": "narrative_shutdown session {}".format(session_id)})
#
#         if session_id is None:
#             return Response("No sessions found for user", status_code=404)
#         else:
#             try:
#                 name = cfg["container_name"].format(userid)
#                 logging.debug(
#                     {"message": "narrative_shutdown reaping", "session_id": session_id}
#                 )
#                 reap_narrative(name)
#
#                 name_match = naming_regex.format(name)
#                 try:
#                     narr_activity = get_narr_activity_from_db()
#                 except Exception as e:
#                     logging.critical(
#                         {
#                             "message": "Could not get data from database: {}".format(
#                                 repr(e)
#                             )
#                         }
#                     )
#                     raise HTTPException(status_code=500, detail=str(e))
#
#                 for narr_name in narr_activity.keys():
#                     if re.match(name_match, narr_name):
#                         delete_from_narr_activity_db(narr_activity[narr_name])
#                         break
#
#                 return Response("Service {} deleted".format(name), status_code=200)
#             except Exception as e:
#                 logging.critical(
#                     {
#                         "message": "Error: Unhandled exception while trying to reap container {}: {}".format(
#                             name, repr(e)
#                         )
#                     }
#                 )
#                 return Response(
#                     "Error deleting service {}: {}".format(name, repr(e)),
#                     status_code=500,
#                 )
#     else:
#         return Response("Valid KBase authentication token required", status_code=401)
#
#
# @app.get("/narrative_status/")
# async def narrative_status() -> Response:
#     """
#     Simple status endpoint to reassure us that the service is alive.
#     Unauthenticated access just returns a 200 code with the current time in JSON string.
#     If a KBase auth cookie is found and the username is in the list of IDs in cfg['status_users'],
#     then a dump of the current narratives running and their last active time from narr_activity
#     is returned in JSON form, easily sent to Elasticsearch for ingest, roughly matching the old proxy_map output
#     from the original OpenRest Lua code.
#     """
#     logging.info({"message": "Status query received"})
#
#     resp_doc = {
#         "timestamp": datetime.now().isoformat(),
#         "version": VERSION,
#         "git_hash": cfg["COMMIT_SHA"],
#     }
#     request = Request
#     auth_status = valid_request(request)
#     logging.debug({"message": "Status query received", "auth_status": auth_status})
#
#     if "userid" in auth_status:
#         if cfg["status_role"] in auth_status["customroles"]:
#             resp_doc["narrative_services"] = narrative_services()
#         else:
#             logging.debug(
#                 {
#                     "message": "{} roles does not contain {}".format(
#                         auth_status["userid"], cfg["status_role"]
#                     ),
#                     "customroles": str(auth_status["customroles"]),
#                 }
#             )
#
#     return Response(content=json.dumps(resp_doc), media_type="application/json")
#
#
# @app.get("/reaper/")
# async def reaper_endpoint(request: Request) -> Response:
#     """
#     Endpoint that runs the reaper once and returns the status
#     """
#     logging.info(
#         {"message": "Reaper endpoint called from {}".format(request.client.host)}
#     )
#
#     if ipaddress.ip_address(request.client.host) in ipaddress.ip_network(
#         cfg["reaper_ipnetwork"]
#     ):
#         try:
#             num = reaper()
#             return Response("Reaper success: {} deleted".format(num))
#         except Exception as ex:
#             raise HTTPException(
#                 status_code=500, detail="Reaper error: {}".format(repr(ex))
#             )
#     else:
#         raise HTTPException(
#             status_code=403,
#             detail="Reaper error: access denied from IP {}".format(request.client.host),
#         )
#
#
#
