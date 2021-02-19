from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from fastapi_pagination import Page, pagination_params
from fastapi_pagination.ext.tortoise import paginate

from pydantic import BaseModel, validator

from distrobuild.models import Build, Import, ImportCommit, Package, PackageModule, BuildStatus
from distrobuild.serialize import Build_Pydantic

from distrobuild_scheduler import import_package_task, build_package_task

router = APIRouter(prefix="/build")


class BuildRequest(BaseModel):
    package_id: Optional[int]
    package_name: Optional[str]

    @validator('package_name')
    def validate(cls, package_name, values):
        if (not values.get('package_id') and not package_name) or (values.get('package_id') and package_name):
            raise ValueError('either package_id or package_name is required')
        return package_name


class BatchBuildRequest(BaseModel):
    packages: List[BuildRequest]


def gen_body_filters(body_in) -> dict:
    body = BuildRequest(**body_in)
    if body.package_id:
        return {"id": body.package_id}
    if body.package_name:
        return {"name": body.package_name}


@router.get("/", response_model=Page[Build_Pydantic], dependencies=[Depends(pagination_params)])
async def list_builds():
    return await paginate(Build.all().order_by('-created_at').prefetch_related("package"))


# response_model causes some weird errors with Import. why?
# TODO: find out (removing response_model for now)
@router.get("/imports/", dependencies=[Depends(pagination_params)])
async def list_imports():
    return await paginate(Import.all().order_by('-created_at').prefetch_related("package"))


@router.get("/imports/{import_id}/logs", response_class=PlainTextResponse)
async def get_import_logs(import_id: int):
    import_obj = await Import.filter(id=import_id).get()
    try:
        with open(f"/tmp/import-{import_obj.id}.log") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(404, detail="import not started")


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


@router.post("/imports/", status_code=202)
async def import_package_route(body: BuildRequest):
    filters = gen_body_filters(body)
    package = await Package.filter(**filters).get_or_none()
    if not package:
        raise HTTPException(404, detail="package does not exist")

    if package.is_package:
        package_import = await Import.create(package_id=package.id, status=BuildStatus.QUEUED, version=8)
        await import_package_task(package.id, package_import.id)

    if package.is_module:
        subpackages = await PackageModule.filter(module_parent_package_id=package.id).all()
        all_packages_imported = True
        for subpackage in subpackages:
            imports = await Import.filter(package_id=subpackage.package_id).all()
            if not imports or len(imports) == 0:
                all_packages_imported = False
                await import_package_route(BuildRequest(package_id=subpackage.package_id))

        if all_packages_imported:
            package_import = await Import.create(package_id=package.id, status=BuildStatus.QUEUED, version=8,
                                                 module=True)
            await import_package_task(package.id, package_import.id)

    return {}


@router.post("/imports/batch", status_code=202)
async def batch_import_package(body: BatchBuildRequest):
    for build_request in body.packages:
        await import_package_route(build_request)

    return {}
