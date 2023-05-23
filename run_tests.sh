#!/bin/bash

if [[ -n "$GITHUB_ACTIONS" ]]; then
  echo "Running in GHA"
fi

    
TESTS="test/narrative_k8_router/routes/*.py test/narrative_k8_router/*.py"
PYTHONPATH=.:narrative_k8_router:test/narrative_k8_router pytest --cov=narrative_k8_router --cov-report=xml $TESTS