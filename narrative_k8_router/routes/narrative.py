from fastapi import APIRouter, Depends, Request
from narrative_k8_router.lib.auth import authenticator_middleware

router = APIRouter()


@router.get("/narrative_status/", dependencies=[Depends(authenticator_middleware)])
def narrative_status(request: Request):
    pass
    # return JSONResponse(whoami_helper(request), status_code=200)
