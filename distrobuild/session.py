import os
import socket
import optparse

import gitlab
import koji
import requests
from cryptography.fernet import Fernet

from distrobuild.mbs import MBSClient
from distrobuild.settings import settings

gl = gitlab.Gitlab(f"https://{settings.gitlab_host}", private_token=settings.gitlab_api_key)


# from https://pagure.io/koji/blob/master/f/cli/koji_cli/lib.py
def ensure_connection(session):
    try:
        ret = session.getAPIVersion()
    except requests.exceptions.ConnectionError:
        raise Exception("Error: Unable to connect to server")
    if ret != koji.API_VERSION:
        print("WARNING: The server is at API version %d and "
              "the client is at %d" % (ret, koji.API_VERSION))


def activate_session(session, options):
    """Test and login the session is applicable"""
    if isinstance(options, dict):
        options = optparse.Values(options)
    noauth = options.authtype == "noauth" or getattr(options, "noauth", False)
    runas = getattr(options, "runas", None)
    if noauth:
        # skip authentication
        pass
    elif options.authtype == "ssl" or os.path.isfile(options.cert) and options.authtype is None:
        # authenticate using SSL client cert
        session.ssl_login(options.cert, None, options.serverca, proxyuser=runas)
    elif options.authtype == "password" \
        or getattr(options, "user", None) \
        and options.authtype is None:
        # authenticate using user/password
        session.login()
    elif options.authtype == "kerberos" or options.authtype is None:
        try:
            if getattr(options, "keytab", None) and getattr(options, "principal", None):
                session.gssapi_login(principal=options.principal, keytab=options.keytab,
                                     proxyuser=runas)
            else:
                session.gssapi_login(proxyuser=runas)
        except socket.error as e:
            print("Could not connect to Kerberos authentication service: %s" % e.args[1])
    if not noauth and not session.logged_in:
        raise Exception("Unable to log in, no authentication methods available")
    ensure_connection(session)
    if getattr(options, "debug", None):
        print("successfully connected to hub")


# end

koji_config = koji.read_config("koji")
koji_session = koji.ClientSession(koji_config["server"], koji_config)
activate_session(koji_session, koji_config)
mbs_client = MBSClient(settings.mbs_url)
message_cipher = Fernet(settings.message_secret)
