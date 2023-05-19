import os
from datetime import datetime

from kubernetes import client, config

# Set up Kubernetes client
from src.models import ActiveNarrativeContainers, NarrativeService

config.load_kube_config()
k8s_client = client.CoreV1Api()


def get_active_narrative_containers() -> ActiveNarrativeContainers:
    #TODO See what fields are being scraped from this endpoint, and if there is some custom logic
    #otherwise this seems to match up api response almost

    label_selector = "app=narrative"
    namespace = os.environ.get("KUBERNETES_NAMESPACE", "staging-narrative")

    pod_list = k8s_client.list_namespaced_pod(label_selector=label_selector, namespace=namespace)

    narrative_services = []
    for pod in pod_list.items:

        publicEndpoints = "none"
        if pod.metadata.annotations:
            publicEndpoints = pod.metadata.annotations.get("publicEndpoints")

        narrative_service = NarrativeService(
            instance=pod.metadata.name,
            state=pod.status.phase,
            session_id=pod.metadata.labels.get("session_id", 'NO_SESSION_ID'),
            last_seen=pod.status.start_time.isoformat(),
            session_key=pod.metadata.labels.get("session_key", "NO_SESSION_KEY"),
            image=pod.spec.containers[0].image,
            publicEndpoints=publicEndpoints,
            last_ip=pod.status.host_ip,
            created=pod.metadata.creation_timestamp.isoformat()
        )

        narrative_services.append(narrative_service)

    active_narrative_containers = ActiveNarrativeContainers(
        timestamp=datetime.now().isoformat(),
        version="0.10.1",
        git_hash="119fc07",
        narrative_services=narrative_services
    )

    return active_narrative_containers


sample_response_on_ci ={
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
      "created": "2023-05-19T20:06:51.501038Z"
    }
  ]
}