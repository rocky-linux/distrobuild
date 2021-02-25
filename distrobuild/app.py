import asyncio

from tortoise import Tortoise

Tortoise.init_models(["distrobuild.models"], "distrobuild")

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

from distrobuild import settings
from distrobuild.routes import register_routes
# init sessions
from distrobuild import session

from distrobuild_scheduler import init_channel

app = FastAPI()
app.mount("/static/files", StaticFiles(directory="ui/dist/files"), name="static")
register_routes(app)

templates = Jinja2Templates(directory="ui/dist/templates")


@app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "distribution": settings.settings.distribution,
        "koji_weburl": session.koji_config.get("weburl"),
        "gitlab_url": f"https://{settings.settings.gitlab_host}{settings.settings.repo_prefix}"
    })


@app.on_event("startup")
async def startup():
    await init_channel(asyncio.get_event_loop())


register_tortoise(
    app,
    config=settings.TORTOISE_ORM
)
