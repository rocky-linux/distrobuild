from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from distrobuild.auth import oidc

router = APIRouter(prefix="/oidc")


@router.get('/start_flow')
async def start_flow(request: Request):
    redirect_uri = request.url_for('callback')
    return await oidc.authorize_redirect(request, redirect_uri)


@router.get('/callback')
async def callback(request: Request):
    token = await oidc.authorize_access_token(request)
    user = await oidc.parse_id_token(request, token)
    request.session['user'] = dict(user)
    return RedirectResponse(url="/")
