docker build . -t narrative-k8-router:test
docker run -it -v ~/.kube/config:/root/.kube/config narrative-k8-router:test
