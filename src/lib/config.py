import os
from functools import lru_cache

from pydantic import BaseSettings


# Could just use the class instead
@lru_cache()
def get_settings():
    return Settings()


class Settings(BaseSettings):
    auth_url: str = os.environ.get("AUTH_URL", "https://ci.kbase.us/services/auth/api/V2/me")
    admin_role: str = os.environ.get("ADMIN_ROLE", "KBASE_ADMIN")
    namespace: str = os.environ.get("KUBERNETES_NAMESPACE", "staging-narrative")
    kubeconfig: str = os.environ.get("KUBECONFIG", "~/.kube/config")

    # Could load from .env file instead
    # class Config:
    #     env_file = ".env"
