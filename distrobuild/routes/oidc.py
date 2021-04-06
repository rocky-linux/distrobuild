#  Copyright (c) 2021 The Distrobuild Authors
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

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
