import os
from typing import Dict

from fastapi import FastAPI, HTTPException
from kubernetes.client import models
from kubernetes.client.rest import ApiException
from pydantic import BaseModel, Field

from k8_helper import k8s_client

app = FastAPI()


class ContainerRequest(BaseModel):
    container_image: str = Field(..., description="Image of the container to start")
    container_name: str = Field(..., description="Name of the container")
    container_command: str = Field(..., description="Command to run inside the container")
    container_args: str = Field(..., description="Arguments for the container command")


@app.post("/start_container", response_model=Dict[str, str], summary="Start a container")
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
        args=container_req.container_args.split()
    )

    # Create pod definition
    pod = models.V1Pod(
        metadata=models.V1ObjectMeta(name=container_req.container_name),
        spec=models.V1PodSpec(
            containers=[container]
        )
    )

    try:
        # Create pod in namespace on Kubernetes cluster
        k8s_client.create_namespaced_pod(body=pod, namespace=namespace)
        return {"message": f"Container {container_req.container_name} started in namespace {namespace}"}
    except ApiException as e:
        if e.status == 409:
            raise HTTPException(status_code=409, detail="Conflict: Container already exists")
        else:
            raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
