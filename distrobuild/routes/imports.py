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

from typing import Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_pagination import pagination_params, Page
from fastapi_pagination.ext.tortoise import paginate
from pydantic import BaseModel, validator
from starlette.responses import PlainTextResponse

from distrobuild.common import gen_body_filters, create_import_order, get_user
from distrobuild.models import Import, Package, Repo, ImportStatus
from distrobuild.serialize import Import_Pydantic, ImportGeneral_Pydantic
from distrobuild.settings import settings
from distrobuild_scheduler import import_package_task

router = APIRouter(prefix="/imports")


class ImportRequest(BaseModel):
    full_history: bool = False
    single_tag: Optional[str]
    package_id: Optional[int]
    package_name: Optional[str]

    @validator("package_name")
    def validate(cls, package_name, values):
        if (not values.get("package_id") and not package_name) or (values.get("package_id") and package_name):
            raise ValueError("either package_id or package_name is required")
        return package_name


@router.get("/", response_model=Page[ImportGeneral_Pydantic], dependencies=[Depends(pagination_params)])
async def list_imports():
    return await paginate(Import.all().order_by("-created_at").prefetch_related("package", "commits"))


@router.get("/{import_id}", response_model=Import_Pydantic)
async def get_import(import_id: int):
    return await Import_Pydantic.from_queryset_single(Import.filter(id=import_id).prefetch_related("package").first())


@router.get("/{import_id}/logs", response_class=PlainTextResponse)
async def get_import_logs(import_id: int):
    import_obj = await Import.filter(id=import_id).get_or_none()
    if not import_obj:
        raise HTTPException(404, detail="import does not exist")
    try:
        with open(f"{settings.import_logs_dir}/import-{import_obj.id}.log") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(412, detail="import not started or log has expired")


@router.post("/{import_id}/cancel", status_code=202)
async def cancel_import(import_id: int):
    user = get_user(request)

    import_obj = await Import.filter(id=import_id, cancelled=False).get_or_none()
    if not import_obj:
        raise HTTPException(404, detail="import does not exist or is already cancelled")

    import_obj.status = ImportStatus.CANCELLED
    await import_obj.save()

    return {}


@router.post("/", status_code=202)
async def import_package_route(request: Request, body: Dict[str, ImportRequest], batch_import_id: Optional[int] = None):
    user = get_user(request)

    filters = gen_body_filters(body)
    package = await Package.filter(**filters).get_or_none()
    if not package:
        raise HTTPException(404, detail="package does not exist")

    if package.repo == Repo.MODULAR_CANDIDATE:
        raise HTTPException(401, detail="modular subpackages cannot be imported")

    build_order = await create_import_order(package, user["preferred_username"], batch_import_id)
    await import_package_task(build_order[0][0], build_order[0][1], build_order[1:])

    return {}
