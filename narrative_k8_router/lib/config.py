import os
from dataclasses import dataclass
from functools import lru_cache

from pydantic import BaseSettings


# Could just use the class instead
@lru_cache()
def get_settings():
    return Settings()


class ContainerSettings(BaseSettings):
    container_name: str = "narrative-{}"


# @dataclass(frozen=True)
class Settings(BaseSettings):
    auth_url: str = os.environ.get("AUTH_URL", "https://ci.kbase.us/services/auth/api/V2/me")
    login_url_prefix: str = os.environ.get("LOGIN_URL", "https://ci.kbase.us")
    admin_role: str = os.environ.get("ADMIN_ROLE", "KBASE_ADMIN")
    namespace: str = os.environ.get("KUBERNETES_NAMESPACE", "staging-narrative")
    kubeconfig: str = os.environ.get("KUBECONFIG", "~/.kube/config")
    version: str = os.environ.get("VERSION", "123")
    gitcommit: str = os.environ.get("gitcommit", "123")
    container_name: str = "narrative-{}"  # TODO Possiblye move
    prespawn_container_name: str = "narrative-pre-{}"  # TODO Possiblye move
    narrative_session_cookie: str = "narrative_session"
    kbase_session_cookie: str = "kbase_session"

    # Could load from .env file instead
    # class Config:
    #     env_file = ".env"
