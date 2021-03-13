from typing import Optional, List
from pydantic import BaseSettings


class Settings(BaseSettings):
    bugs_api_key: str
    gitlab_api_key: str
    session_secret: str
    message_secret: str
    tag_prefix: str = "rocky"
    active_point_releases: List[str] = ["3", "4"]
    default_point_release: str = "4"

    # srpmproc
    gitlab_host: str
    repo_prefix: str = "/"
    storage_addr: str
    ssh_user: str = "git"
    ssh_port: int = 22
    ssh_key_location: Optional[str]
    version: int = 8
    no_storage_download: bool = False
    no_storage_upload: bool = False

    # mbs
    mbs_url: str

    # oidc
    oidc_issuer: str
    oidc_client_id: str
    oidc_client_secret: str
    oidc_scopes: str = "https://id.fedoraproject.org/scope/groups https://mbs.rockylinux.org/oidc/mbs-submit-build"
    oidc_required_group: Optional[str]

    # appearance
    distribution: str = "Rocky Linux"

    # scheduler options
    broker_url: str
    routing_key: str = "distrobuild"
    workers: int = 10

    class Config:
        env_file = "/etc/distrobuild/settings"


settings = Settings()
if settings.default_point_release not in settings.active_point_releases:
    raise Exception("Default point release not active.")

TORTOISE_ORM = {
    "connections": {"default": "postgres://postgres:postgres@localhost/dbuild"},
    "apps": {
        "distrobuild": {
            "models": [
                "aerich.models",
                "distrobuild.models",
            ],
            "default_connection": "default",
        },
    },
}
