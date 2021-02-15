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
import distrobuild.session

app = FastAPI()
app.mount("/static/files", StaticFiles(directory="ui/dist/files"), name="static")
register_routes(app)

templates = Jinja2Templates(directory="ui/dist/templates")

@app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

register_tortoise(
     app,
     config=settings.TORTOISE_ORM
)
