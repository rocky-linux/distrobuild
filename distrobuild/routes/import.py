from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import pagination_params
from fastapi_pagination.ext.tortoise import paginate
from starlette.responses import PlainTextResponse

from distrobuild.common import BuildRequest, gen_body_filters, BatchBuildRequest, create_build_order
from distrobuild.models import Import, Package
from distrobuild_scheduler import import_package_task

router = APIRouter(prefix="/imports")


# response_model causes some weird errors with Import. why?
# TODO: find out (removing response_model for now)
@router.get("/", dependencies=[Depends(pagination_params)])
async def list_imports():
    return await paginate(Import.all().order_by('-created_at').prefetch_related("package"))


@router.get("/{import_id}/logs", response_class=PlainTextResponse)
async def get_import_logs(import_id: int):
    import_obj = await Import.filter(id=import_id).get_or_none()
    if not import_obj:
        raise HTTPException(404, detail="import does not exist")
    try:
        with open(f"/tmp/import-{import_obj.id}.log") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(412, detail="import not started or log has expired")


@router.post("/", status_code=202)
async def import_package_route(body: BuildRequest):
    filters = gen_body_filters(body)
    package = await Package.filter(**filters).get_or_none()
    if not package:
        raise HTTPException(404, detail="package does not exist")

    build_order = await create_build_order(package)
    await import_package_task(build_order[0][0], build_order[0][1], build_order[1:])

    return {}


@router.post("/batch", status_code=202)
async def batch_import_package(body: BatchBuildRequest):
    for build_request in body.packages:
        await import_package_route(build_request)

    return {}
