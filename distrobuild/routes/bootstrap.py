from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from distrobuild.bootstrap import process_repo_dump, process_module_dump
from distrobuild.common import get_user
from distrobuild.models import Repo

router = APIRouter(prefix="/bootstrap")


@router.post("/modules")
async def bootstrap_modules(request: Request):
    user = get_user(request)
    await process_module_dump(user["preferred_username"])
    return JSONResponse(content={})


@router.post("/{repo}")
async def bootstrap_repo(request: Request, repo: Repo):
    user = get_user(request)
    await process_repo_dump(repo, user["preferred_username"])
    return JSONResponse(content={})
