from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from distrobuild.auth import oidc
from distrobuild.settings import settings

router = APIRouter(prefix="/oidc")


@router.get("/start_flow")
async def start_flow(request: Request):
    redirect_uri = request.url_for("callback")
    return await oidc.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def callback(request: Request):
    token = await oidc.authorize_access_token(request)
    user = await oidc.parse_id_token(request, token)

    if settings.oidc_required_group:
        groups = user.get("groups")
        if not groups:
            request.session.update(not_authorized="No 'groups' attribute in ID token")
            return RedirectResponse(url="/")
        else:
            if settings.oidc_required_group not in groups:
                request.session.update(not_authorized=f"User not in '{settings.oidc_required_group}' group")
                return RedirectResponse(url="/")

    request.session.update(user=user, token=token["access_token"])
    return RedirectResponse(url="/")
