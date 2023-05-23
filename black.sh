black -q --config pyproject.toml -v test/ 2>&1 | grep -v "wasn't modified on disk since last run." | grep -v ".gitignore"
black -q --config pyproject.toml -v narrative_k8_router/ 2>&1 | grep -v "wasn't modified on disk since last run." | grep -v ".gitignore"

