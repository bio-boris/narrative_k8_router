from fastapi import APIRouter, Depends, Request

from lib.k8_helper import get_active_narrative_containers
from lib.auth import authenticator_middleware

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
