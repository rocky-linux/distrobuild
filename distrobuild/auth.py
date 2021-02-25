from authlib.integrations.starlette_client import OAuth

from distrobuild.settings import settings

oauth = OAuth()
oauth.register(
    name="oidc",
    client_id=settings.oidc_client_id,
    client_secret=settings.oidc_client_secret,
    server_metadata_url=f"{settings.oidc_issuer}/.well-known/openid-configuration",
    client_kwargs={
        "scope": f"openid profile {settings.oidc_scopes}"
    }
)

oidc = oauth.oidc
