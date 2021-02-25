from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, pagination_params
from fastapi_pagination.ext.tortoise import paginate

from distrobuild.common import BuildRequest, gen_body_filters, BatchBuildRequest
from distrobuild.models import Build, Import, ImportCommit, Package, PackageModule, BuildStatus
from distrobuild.serialize import Build_Pydantic
from distrobuild_scheduler import build_package_task

router = APIRouter(prefix="/builds")


@router.get("/", response_model=Page[Build_Pydantic], dependencies=[Depends(pagination_params)])
async def list_builds():
    return await paginate(Build.all().order_by('-created_at').prefetch_related("package"))


@router.post("/", status_code=202)
async def queue_build(body: BuildRequest):
    filters = gen_body_filters(body)
    package = await Package.filter(**filters).get_or_none()
    if not package:
        raise HTTPException(404, detail="package does not exist")

    mbs = package.is_module
    package_modules = await PackageModule.filter(package_id=package.id)
    if len(package_modules) > 0:
        mbs = True

    latest_import = await Import.filter(package_id=package.id).order_by("-created_at").first()
    import_commits = await ImportCommit.filter(import__id=latest_import.id).all()
    for import_commit in import_commits:
        if "-beta" not in import_commit.branch:
            build = await Build.create(package_id=package.id, status=BuildStatus.QUEUED, mbs=mbs,
                                       commit=import_commit.commit, branch=import_commit.branch)
            await build_package_task(package.id, build.id)

    return {}


@router.post("/batch", status_code=202)
async def batch_queue_build(body: BatchBuildRequest):
    for build_request in body.packages:
        await queue_build(build_request)

    return {}
