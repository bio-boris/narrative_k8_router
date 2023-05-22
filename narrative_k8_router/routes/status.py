from datetime import datetime
from http.client import HTTPException
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from narrative_k8_router.lib.auth import authenticator_middleware
from narrative_k8_router.lib.config import get_settings

router = APIRouter()

# _authenticator = Annotated[Request, Depends(authenticator_middleware)]


@router.get("/whoami/")
def whoami(request: Request):
    return JSONResponse(
        {
            "username": request.state.username,
            "is_KBASE_ADMIN": request.state.is_admin,
        },
        status_code=200,
    )


@router.get("/status")
def status(return_image_name=None, settings=Depends(get_settings)):
    # TODO Figure out how to populate this with the correct information

    response_data = {
        "timestamp": datetime.now().isoformat(),
        "version": settings.version,
        "vcs-ref": settings.gitcommit,
        "auth_url": settings.auth_url,
        "admin_role": settings.admin_role,
        "k8-namespace": settings.namespace,
    }

    # Maybe env vars
    if return_image_name:
        response_data["image_name"] = "Not Yet Implemented"

    return JSONResponse(response_data, status_code=200)
