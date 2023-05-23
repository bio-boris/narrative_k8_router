#!/bin/bash

if [[ -n "$GITHUB_ACTIONS" ]]; then
  echo "Running in GHA"
fi

    
tests="test/narrative_k8_router/routes/*.py"
PYTHONPATH=.:narrative_k8_router:test/narrative_k8_router pytest --cov=narrative_k8_router --cov-report=xml $tests