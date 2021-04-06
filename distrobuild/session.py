import os
import socket
import optparse

import gitlab
import koji
import requests
from cryptography.fernet import Fernet
from koji_cli.lib import activate_session

from distrobuild.mbs import MBSClient
from distrobuild.settings import settings

gl = gitlab.Gitlab(f"https://{settings.gitlab_host}", private_token=settings.gitlab_api_key)

koji_config = koji.read_config("koji")
koji_session = koji.ClientSession(koji_config["server"], koji_config)
activate_session(koji_session, koji_config)
mbs_client = MBSClient(settings.mbs_url)
message_cipher = Fernet(settings.message_secret)
