import os
from datetime import datetime
from functools import lru_cache

from fastapi import HTTPException
from kubernetes import client, config
from kubernetes.client import models, V1SecurityContext, V1Capabilities, ApiException

from lib.config import get_settings
from lib.models import ActiveNarrativeContainers, NarrativeService, ContainerRequest


# Set up Kubernetes client


@lru_cache()
def get_k8s_client() -> client.CoreV1Api:
    config.load_kube_config()
    return client.CoreV1Api()


def get_container_security_context() -> V1SecurityContext:
    return V1SecurityContext(
        capabilities=V1Capabilities(
            add=[],
            drop=[
                "MKNOD",
                "NET_RAW",
                "SYS_CHROOT",
                "SETUID",
                "SETGID",
                "CHOWN",
                "SYS_ADMIN",
                "DAC_OVERRIDE",
                "FOWNER",
                "FSETID",
                "SETPCAP",
                "AUDIT_WRITE",
                "SETFCAP",
            ],
        )
    )


def start_container(username:str, client_ip: str, session_id: str, prespawn=False, settings=get_settings(), k8s_client=get_k8s_client()) -> dict:
    if not username:
        raise HTTPException(status_code=400, detail="Username is required to start a container")

    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required to start a container")

    namespace = settings.namespace

    #TODO Might not need to differentiate between these names anymore, or if prespawned, do we need to create a UUID?
    container_name = settings.container_name.format(username)
    if prespawn:
        container_name = settings.prespawn_container_name.format(username)



    # Create container definition

    container = models.V1Container(
        name=container_name,
        image="ghcr.io/kbase/narrative:latest",  # TODO: Make this configurable
        security_context=get_container_security_context(),
        image_pull_policy="Always",
        ports=[models.V1ContainerPort(container_port=8888)],
        tty=True,
        stdin=True,
    )

    # Create pod definition
    # Create pod definition
    spec = models.V1PodSpec(
        containers=[container],
        restart_policy="Always",
        dns_policy="ClusterFirst",
    )
    labels = {"app": "narrative", "session_id": session_id, "traefik.enable": "True"}
    annotations = {"client-ip": client_ip, "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")}
    metadata = models.V1ObjectMeta(name=container_name, namespace=namespace, labels=labels, annotations=annotations)
    pod = models.V1Pod(metadata=metadata, spec=spec)

    # # create a rule for list of hostnames that should match from cfg['hostname']
    # host_rules = " || ".join(['Host("{}")'.format(hostname) for hostname in cfg["hostname"]])
    # remaining_rule = ' && PathPrefix("{}") && HeadersRegexp("Cookie",`{}`)'
    # labels["traefik.http.routers." + userid + ".rule"] = host_rules + remaining_rule.format("/narrative/", cookie)
    # labels["traefik.http.routers." + userid + ".entrypoints"] = "web"
    # container_config["launchConfig"]["labels"] = labels
    # container_config["launchConfig"]["name"] = name
    # if cfg["image_tag"] is not None and cfg["image_tag"] != "":
    #     imageUuid = "{}:{}".format(cfg["image_name"], cfg["image_tag"])
    # else:
    #     # to do: fix calling latest_narr_version() so we don't need to call the `app` method like this
    #     imageUuid = "{}:{}".format(cfg["image_name"], app.latest_narr_version())
    # container_config["launchConfig"]["imageUuid"] = "docker:{}".format(imageUuid)
    # container_config["launchConfig"]["environment"].update(cfg["narrenv"])
    # container_config["name"] = name
    # container_config["stackId"] = cfg["rancher_stack_id"]
    #

    try:
        # Create pod in namespace on Kubernetes cluster
        k8s_client.create_namespaced_pod(body=pod, namespace=namespace)
        return {"message": f"Container {container_name} started in namespace {namespace}"}
    except ApiException as e:
        if e.status == 409:
            raise HTTPException(status_code=409, detail="Conflict: Container already exists")
        else:
            raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_active_narrative_containers(settings=get_settings()) -> ActiveNarrativeContainers:
    # TODO See what fields are being scraped from this endpoint, and if there is some custom logic
    # otherwise this seems to match up api response almost
    k8s_client = get_k8s_client()

    label_selector = "app=narrative"
    namespace = settings.namespace

    pod_list = k8s_client.list_namespaced_pod(timeout_seconds=1, label_selector=label_selector, namespace=namespace)

    narrative_services = []
    for pod in pod_list.items:
        publicEndpoints = "none"
        if pod.metadata.annotations:
            publicEndpoints = pod.metadata.annotations.get("publicEndpoints")

        narrative_service = NarrativeService(
            instance=pod.metadata.name,
            state=pod.status.phase,
            session_id=pod.metadata.labels.get("session_id", "NO_SESSION_ID"),
            last_seen=pod.status.start_time.isoformat(),
            session_key=pod.metadata.labels.get("session_key", "NO_SESSION_KEY"),
            image=pod.spec.containers[0].image,
            publicEndpoints=publicEndpoints,
            last_ip=pod.status.host_ip,
            created=pod.metadata.creation_timestamp.isoformat(),
        )

        narrative_services.append(narrative_service)

    settings = get_settings()
    active_narrative_containers = ActiveNarrativeContainers(
        timestamp=datetime.now().isoformat(),
        version=settings.version,
        git_hash=settings.gitcommit,
        narrative_services=narrative_services,
    )

    return active_narrative_containers


sample_response_on_ci = {
    "timestamp": "2023-05-19T21:51:15.396394",
    "version": "0.10.1",
    "git_hash": "119fc07",
    "narrative_services": [
        {
            "instance": "narrative-gaprice-c33afa",
            "state": "active",
            "session_id": "gaprice-c33afa",
            "last_seen": "Fri May 19 21:51:00 2023",
            "session_key": "dafd0f733ce2f311d2201afed6c43f35",
            "image": "docker:ghcr.io/kbase/narrative-develop:latest",
            "publicEndpoints": "[{'type': 'publicEndpoint', 'hostId': '1h142', 'instanceId': '1i6637796', 'ipAddress': '10.58.1.105', 'port': 52661, 'serviceId': '1s438427'}]",
            "last_ip": "24.7.65.94",
            "created": "2023-05-19T20:06:51.501038Z",
        }
    ],
}

# logger.info({"message": "Status query received"})

# Get narr_activity from the database
# not currently used but may use in the future
# try:
#    narr_activity = get_narr_activity_from_db()
# except Exception as e:
#    logger.critical({"message": "Could not get narr_activity data from database: {}".format(repr(e))})
#    return


# resp_doc = {"timestamp": datetime.now().isoformat(), "version": VERSION, "git_hash": cfg['COMMIT_SHA']}
# request = flask.request
# auth_status = valid_request(request)
# logger.debug({"message": "Status query received", "auth_status": auth_status})
# if 'userid' in auth_status:
#     if cfg['status_role'] in auth_status['customroles']:
#         resp_doc['narrative_services'] = narrative_services()
#     else:
#         logger.debug({"message": "{} roles does not contain {}".format(auth_status['userid'], cfg['status_role']),
#                       "customroles": str(auth_status['customroles'])})
# return (flask.Response(json.dumps(resp_doc), 200, mimetype='application/json'))
# @app.post(
#     "/start_container", response_model=Dict[str, str], summary="Start a container"
# )
# async def start_container(container_req: ContainerRequest):
#     """
#     Start a container in the Kubernetes cluster.
#
#     Args:
#         container_req: ContainerRequest model containing container details.
#
#     Returns:
#         A dictionary with a success message.
#
#     Raises:
#         HTTPException: If there is an error starting the container.
#     """
#     # Get namespace from environmental variable
#     namespace = os.environ.get("KUBERNETES_NAMESPACE", "staging-narrative")
#
#     # Create container definition
#     container = models.V1Container(
#         name=container_req.container_name,
#         image=container_req.container_image,
#         command=container_req.container_command.split(),
#         args=container_req.container_args.split(),
#     )
#
#     # Create pod definition
#     pod = models.V1Pod(
#         metadata=models.V1ObjectMeta(name=container_req.container_name),
#         spec=models.V1PodSpec(containers=[container]),
#     )
#
#     try:
#         # Create pod in namespace on Kubernetes cluster
#         k8s_client.create_namespaced_pod(body=pod, namespace=namespace)
#         return {
#             "message": f"Container {container_req.container_name} started in namespace {namespace}"
#         }
#     except ApiException as e:
#         if e.status == 409:
#             raise HTTPException(
#                 status_code=409, detail="Conflict: Container already exists"
#             )
#         else:
#             raise HTTPException(status_code=e.status, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
