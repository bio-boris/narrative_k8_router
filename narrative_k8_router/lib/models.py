from pydantic import BaseModel, Field

from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from pydantic import BaseModel
from typing import List


class NarrativeService(BaseModel):
    instance: str = None
    state: str = None
    session_id: str = None
    last_seen: str = None
    session_key: str = None
    image: str = None
    publicEndpoints: str = None
    last_ip: str = None
    created: str = None


class ActiveNarrativeContainers(BaseModel):
    timestamp: str
    version: str
    git_hash: str
    narrative_services: List[NarrativeService]


class ContainerRequest(BaseModel):
    container_image: str = Field(..., description="Image of the container to start")
    container_name: str = Field(..., description="Name of the container")
    container_command: str = Field(
        ..., description="Command to run inside the container"
    )
    container_args: str = Field(..., description="Arguments for the container command")
