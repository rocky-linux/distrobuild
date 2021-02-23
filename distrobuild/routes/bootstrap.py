from fastapi import APIRouter
from fastapi.responses import JSONResponse

from distrobuild.bootstrap import process_repo_dump, process_module_dump
from distrobuild.models import Repo

router = APIRouter(prefix="/bootstrap")


@router.post("/modules")
async def bootstrap_modules():
    await process_module_dump()
    return JSONResponse(content={})


@router.post("/{repo}")
async def bootstrap_repo(repo: Repo):
    await process_repo_dump(repo)
    return JSONResponse(content={})
