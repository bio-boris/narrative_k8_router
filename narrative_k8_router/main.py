from fastapi import FastAPI

from lib.auth import authenticator_middleware
from narrative_k8_router.routes.narrative import router as narrative_router
from narrative_k8_router.routes.status import router as status_router

app = FastAPI()
app.include_router(narrative_router)
app.include_router(status_router)
app.middleware("http")(authenticator_middleware)

def create_app(auth=True) -> FastAPI:
    app = FastAPI()
    app.include_router(narrative_router)
    app.include_router(status_router)
    if auth:
        app.middleware("http")(authenticator_middleware)

    return app

