
import os
from kubernetes import client, config


# Set up Kubernetes client
config.load_kube_config(config_file=os.environ.get("KUBECONFIG", "~/.kube/config"))
k8s_client = client.CoreV1Api()

