tests="test/narrative_k8_router/routes/*.py"
PYTHONPATH=.:narrative_k8_router:test/narrative_k8_router pytest --cov=src --cov-report=xml $tests