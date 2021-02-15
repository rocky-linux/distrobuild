from typing import Optional
from enum import Enum
from pydantic import BaseSettings

class Settings(BaseSettings):
    gitlab_host: str
    koji_hub_url: str
    repo_prefix: str
    storage_addr: str
    ssh_user: str = "git"
    ssh_port: int = 22
    ssh_key_location: Optional[str]
    version: int = 8
    bugs_api_key: str
    gitlab_api_key: str


    class Config:
        env_file = "/etc/distrobuild/settings"

settings = Settings()

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
