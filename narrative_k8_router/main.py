from fastapi import FastAPI

from auth import authenticator_middleware
from routes.narrative import router as narrative_router
from routes.status import router as status_router

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

