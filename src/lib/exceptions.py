from pydantic import BaseModel, Field


class ContainerRequest(BaseModel):
    container_image: str = Field(..., description="Image of the container to start")
    container_name: str = Field(..., description="Name of the container")
    container_command: str = Field(
        ..., description="Command to run inside the container"
    )
    container_args: str = Field(..., description="Arguments for the container command")
