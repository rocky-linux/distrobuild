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

import asyncio

from tortoise import Tortoise

Tortoise.init_models(["distrobuild.models"], "distrobuild")

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from tortoise.contrib.fastapi import register_tortoise

from distrobuild.settings import TORTOISE_ORM, settings
from distrobuild.routes import register_routes
# init sessions
from distrobuild import session

from distrobuild_scheduler import init_channel

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret, max_age=3500)
app.mount("/static/files", StaticFiles(directory="ui/dist/files"), name="static")
register_routes(app)

templates = Jinja2Templates(directory="ui/dist/templates")
static_templates = Jinja2Templates(directory="distrobuild/templates")


@app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend(request: Request):
    not_authorized_message = request.session.get("not_authorized")
    if not_authorized_message:
        request.session.pop("not_authorized")
        return static_templates.TemplateResponse("not_authorized.html.j2", {
            "request": request,
            "message": not_authorized_message,
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "distribution": settings.distribution,
        "authenticated": "true" if request.session.get("user") else "false",
        "full_name": request.session.get("user").get("name") if request.session.get("user") else "",
        "koji_weburl": session.koji_config.get("weburl"),
        "gitlab_url": f"https://{settings.gitlab_host}",
        "repo_prefix": settings.repo_prefix
    })


@app.on_event("startup")
async def startup():
    await init_channel(asyncio.get_event_loop())


register_tortoise(
    app,
    config=TORTOISE_ORM
)
