from fastapi import FastAPI
import logging
from lib.auth import authenticator_middleware
from narrative_k8_router.routes.narrative import router as narrative_router
from narrative_k8_router.routes.status import router as status_router

logging.basicConfig()

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)