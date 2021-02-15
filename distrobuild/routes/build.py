import datetime

from typing import Optional, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from fastapi_pagination import Page, pagination_params
from fastapi_pagination.ext.tortoise import paginate

from tortoise.transactions import atomic

from pydantic import BaseModel, validator

from distrobuild.models import Build, Import, Package, PackageModule, BuildStatus
from distrobuild.pydantic import Build_Pydantic, Import_Pydantic

from distrobuild.session import gl, koji_session
from distrobuild.settings import settings
from distrobuild import srpmproc

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

def gen_body_filters(body: BuildRequest) -> dict:
    if body.get("package_id"):
        return {"id": body["package_id"]}
    if body.get("package_name"):
        return {"name": body["package_name"]}

@atomic()
async def do_build_task(package: Package, build: Build):
    if build.mbs:
        pass
    else:
        scratch = False
        target = "dist-rocky8"

        latest_import = await Import.filter(package_id=package.id).order_by("-created_at").first()

        source = f"git+https://{settings.gitlab_host}{settings.repo_prefix}/rpms/{package.name}.git?#{latest_import.commit}"
        task_id = koji_session.build(source, target)

        build.koji_id = task_id
        build.status = BuildStatus.BUILDING
        await build.save()

async def build_task(package: Package, build: Build):
    try:
        await do_build_task(package, build)
    except Exception as e:
        print(e)
        build.status = BuildStatus.FAILED
        await build.save()

@atomic()
async def do_import_task(package: Package, import_obj: Import):
    koji_session.packageListAdd("dist-rocky8", package.name, "distrobuild")

    import_obj.status = BuildStatus.BUILDING
    await import_obj.save()

    await srpmproc.import_project(import_obj.id, package.name)

    package.last_import = datetime.datetime.now()
    await package.save()

    project = gl.projects.get(f"{settings.repo_prefix.removeprefix('/')}/rpms/{package.name}")
    project.visibility = "public"
    project.save()

    latest_commit = project.commits.list(ref_name=f"r{import_obj.version}")[0].id
    import_obj.status = BuildStatus.SUCCEEDED
    import_obj.commit = latest_commit
    await import_obj.save()

async def import_task(package: Package, import_obj: Import):
    try:
        await do_import_task(package, import_obj)
    except Exception as e:
        print(e)
        import_obj.status = BuildStatus.FAILED
        await import_obj.save()

@router.get("/", response_model=Page[Build_Pydantic], dependencies=[Depends(pagination_params)])
async def list_builds():
    return await paginate(Build.all().order_by('-created_at').prefetch_related("package"))

# response_model causes some weird errors with Import. why?
# TODO: find out (removing response_model for now)
@router.get("/imports/", dependencies=[Depends(pagination_params)])
async def list_imports():
    return await paginate(Import.all().order_by('-created_at').prefetch_related("package"))

@router.get("/imports/{id}/logs", response_class=PlainTextResponse)
async def get_import_logs(id: int):
    import_obj = await Import.filter(id=id).get()
    with open(f"/tmp/import-{import_obj.id}.log") as f:
        return f.read()

@router.post("/", status_code=202)
async def queue_build(body: BuildRequest, background_tasks: BackgroundTasks):
    filters = gen_body_filters(body)
    package = await Package.filter(**filters).get_or_none()
    if not package:
        raise HTTPException(404, detail="package does not exist")

    mbs = package.is_module
    package_modules = await PackageModule.filter(package_id=package.id)
    if len(package_modules) > 0:
        mbs = True

    build = await Build.create(package_id=package.id, status=BuildStatus.QUEUED, mbs=mbs)

    background_tasks.add_task(build_task, package, build)

    return {}

@router.post("/batch", status_code=202)
async def batch_queue_build(body: BatchBuildRequest, background_tasks: BackgroundTasks):
    for build_request in body.packages:
        await queue_build(build_request, background_tasks)

    return {}

@router.post("/imports/", status_code=202)
async def import_package(body: BuildRequest, background_tasks: BackgroundTasks):
    filters = gen_body_filters(body)
    package = await Package.filter(**filters).get_or_none()
    if not package:
        raise HTTPException(404, detail="package does not exist")

    import_obj = await Import.create(package_id=package.id, status=BuildStatus.QUEUED, version=8)

    background_tasks.add_task(import_task, package, import_obj)

    return {}

@router.post("/imports/batch", status_code=202)
async def batch_import_package(body: BatchBuildRequest, background_tasks: BackgroundTasks):
    for build_request in body.packages:
        await import_package(build_request, background_tasks)

    return {}
