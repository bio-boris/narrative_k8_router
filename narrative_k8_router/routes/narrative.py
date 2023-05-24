from fastapi import APIRouter, Request, Response, Path

from lib.k8_helper import get_active_narrative_containers
from lib.narrative_helper import get_container

router = APIRouter()


@router.get("/narrative_status/")
def narrative_status(request: Request):
    """
    Simple status endpoint to re-assure us that the service is alive. Unauthenticated access just returns
    a 200 code with the current time in JSON string. If a kbase auth cookie is found, and the username is in the
    list of ID's in cfg['status_users'] then a dump of the current narratives running and their last
    active time from narr_activity is returned in JSON form, easily sent to elasticsearch for ingest, roughly
    matching the old proxy_map output from original OpenRest lua code
    """
    return get_active_narrative_containers()


@router.get("/narrative/{narrative_identifier}")
def narrative(request: Request, narrative_identifier: str = Path(..., description="Narrative")):
    # Your code logic here
    # Access the `narrative_request` parameter in your code

    return get_container(request, narrative_identifier)
    #
    # """
    # Main handler for the auth service. Validate the request, get the container is should be routed
    # to and return a response that will result in traefik routing to the right place for subsequent
    # requests. Returns an error in the flask response if requirements are not met or if an error
    # occurs
    # """
    # return {}
    #
    # request = flask.request
    # auth_status = valid_request(request)
    # if 'userid' in auth_status:
    #     resp = get_container(auth_status['userid'], request, narrative)
    # else:
    #     if auth_status['error'] == "no_cookie":
    #         next_request = '{{"path":"{}","external":true}}'.format(request.full_path)
    #         logger.debug({"message": "Redirecting user for no_cookie", "nextrequest": request.url})
    #         resp = flask.redirect("/#login?nextrequest={}".format(quote_plus(next_request)))
    #     else:
    #         resp = error_response(auth_status, request)
    # return resp
