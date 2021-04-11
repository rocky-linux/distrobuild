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

from typing import List

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi_pagination import Page, pagination_params
from fastapi_pagination.ext.tortoise import paginate
from pydantic import BaseModel
from tortoise.functions import Count

from distrobuild.common import batch_list_check
from distrobuild.models import BatchImport, BatchBuild, ImportStatus, BuildStatus
from distrobuild.routes.builds import BuildRequest, queue_build
from distrobuild.routes.imports import ImportRequest, import_package_route
from distrobuild.serialize import BatchImport_Pydantic, BatchBuild_Pydantic

router = APIRouter(prefix="/batches")


class BatchImportRequest(BaseModel):
    should_precheck: bool = True
    packages: List[ImportRequest]


class BatchBuildRequest(BaseModel):
    should_precheck: bool = True
    ignore_modules: bool = False
    packages: List[BuildRequest]


class NewBatchResponse(BaseModel):
    id: int


@router.get("/imports/", response_model=Page[BatchImport_Pydantic], dependencies=[Depends(pagination_params)])
async def list_batch_imports():
    return await paginate(
        BatchImport.all().prefetch_related("imports", "imports__package", "imports__commits").order_by("-created_at"))


@router.post("/imports/", response_model=NewBatchResponse)
async def batch_import_package(request: Request, body: BatchImportRequest):
    if body.should_precheck:
        await batch_list_check(body.packages)

    batch = await BatchImport.create()

    for build_request in body.packages:
        await import_package_route(request, dict(build_request), batch.id)

    return NewBatchResponse(id=batch.id)


@router.get("/imports/{batch_import_id}", response_model=BatchImport_Pydantic)
async def get_batch_import(batch_import_id: int):
    return await BatchImport_Pydantic.from_queryset_single(BatchImport.filter(id=batch_import_id).first())


@router.post("/imports/{batch_import_id}/cancel", status_code=202)
async def cancel_batch_import(batch_import_id: int):
    batch_import_obj = await BatchImport.filter(id=batch_import_id).prefetch_related("imports").get_or_none()
    if not batch_import_obj:
        raise HTTPException(404, detail="batch import does not exist")

    for import_ in batch_import_obj.imports:
        import_.status = ImportStatus.CANCELLED
        await import_.save()

    return {}


@router.post("/imports/{batch_import_id}/retry_failed", response_model=NewBatchResponse)
async def retry_failed_batch_imports(request: Request, batch_import_id: int):
    batch_import_obj = await BatchImport.filter(id=batch_import_id).prefetch_related("imports",
                                                                                     "imports__package").get_or_none()
    if not batch_import_obj:
        raise HTTPException(404, detail="batch import does not exist")

    packages = [{"package_id": b.package.id} for b in batch_import_obj.imports if
                b.status == ImportStatus.CANCELLED or b.status == ImportStatus.FAILED]

    return await batch_import_package(request, BatchImportRequest(packages=packages))


@router.get("/builds/", response_model=Page[BatchBuild_Pydantic], dependencies=[Depends(pagination_params)])
async def list_batch_builds():
    return await paginate(
        BatchBuild.all().prefetch_related("builds", "builds__package", "builds__import_commit").order_by("-created_at"))


@router.post("/builds/", response_model=NewBatchResponse)
async def batch_queue_build(request: Request, body: BatchBuildRequest):
    if body.should_precheck:
        await batch_list_check(body.packages)

    batch = await BatchBuild.create()

    for build_request in body.packages:
        await queue_build(request, dict(**dict(build_request), ignore_modules=body.ignore_modules), batch.id)

    return NewBatchResponse(id=batch.id)


@router.get("/builds/{batch_build_id}", response_model=BatchBuild_Pydantic)
async def get_batch_build(batch_build_id: int):
    return await BatchBuild_Pydantic.from_queryset_single(BatchBuild.filter(id=batch_build_id).first())


@router.post("/builds/{batch_build_id}/cancel", status_code=202)
async def cancel_batch_build(batch_build_id: int):
    batch_build_obj = await BatchBuild.filter(id=batch_build_id).prefetch_related("builds").get_or_none()
    if not batch_build_obj:
        raise HTTPException(404, detail="batch build does not exist")

    for build in batch_build_obj.builds:
        build.status = BuildStatus.CANCELLED
        await build.save()

    return {}


@router.post("/builds/{batch_build_id}/retry_failed", response_model=NewBatchResponse)
async def retry_failed_batch_builds(request: Request, batch_build_id: int):
    batch_build_obj = await BatchBuild.filter(id=batch_build_id).prefetch_related("builds",
                                                                                  "builds__package").get_or_none()
    if not batch_build_obj:
        raise HTTPException(404, detail="batch build does not exist")

    packages = [{"package_id": b.package.id} for b in batch_build_obj.builds if
                b.status == BuildStatus.CANCELLED or b.status == BuildStatus.FAILED]

    return await batch_queue_build(request, BatchBuildRequest(packages=packages))
