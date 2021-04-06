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

from typing import Optional, List, Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_pagination import Page, pagination_params
from fastapi_pagination.ext.tortoise import paginate
from pydantic import BaseModel, validator

from distrobuild.common import gen_body_filters, get_user, tags
from distrobuild.models import Build, Import, ImportCommit, Package, PackageModule, BuildStatus, Repo
from distrobuild.serialize import Build_Pydantic
from distrobuild.session import message_cipher
from distrobuild_scheduler import build_package_task

router = APIRouter(prefix="/builds")


class BuildRequest(BaseModel):
    scratch: bool = False
    testing: bool = False
    package_id: Optional[int]
    package_name: Optional[str]

    @validator("package_name")
    def validate(cls, package_name, values):
        if (not values.get("package_id") and not package_name) or (values.get("package_id") and package_name):
            raise ValueError("either package_id or package_name is required")
        return package_name


class BatchBuildRequest(BaseModel):
    packages: List[BuildRequest]


@router.get("/", response_model=Page[Build_Pydantic], dependencies=[Depends(pagination_params)])
async def list_builds():
    return await paginate(Build.all().order_by("-created_at").prefetch_related("package", "import_commit"))


@router.get("/{build_id}", response_model=Build_Pydantic)
async def get_build(build_id: int):
    return await Build_Pydantic.from_queryset_single(
        Build.filter(id=build_id).prefetch_related("package", "import_commit").first()
    )


@router.post("/", status_code=202)
async def queue_build(request: Request, body: Dict[str, BuildRequest]):
    user = get_user(request)

    filters = gen_body_filters(body)
    package = await Package.filter(**filters).get_or_none()
    if not package:
        raise HTTPException(404, detail="package does not exist")

    if package.repo == Repo.MODULAR_CANDIDATE:
        raise HTTPException(401, detail="modular subpackages cannot be built, build the main module")

    if package.part_of_module and not package.is_module:
        raise HTTPException(401, detail="this package is part of a module. build the main module")

    extras = {
        "mbs": package.is_module
    }
    token = None
    package_modules = await PackageModule.filter(package_id=package.id)
    if len(package_modules) > 0 or package.is_module:
        extras["mbs"] = True
        token = message_cipher.encrypt(request.session.get("token").encode()).decode()

    if body.get("testing") and not body.get("scratch"):
        extras["force_tag"] = tags.testing()

    if body.get("scratch"):
        extras["force_tag"] = tags.scratch()

    latest_import = await Import.filter(package_id=package.id).order_by("-created_at").first()
    import_commits = await ImportCommit.filter(import__id=latest_import.id).all()
    for import_commit in import_commits:
        if "-beta" not in import_commit.branch:
            build = await Build.create(package_id=package.id, status=BuildStatus.QUEUED,
                                       executor_username=user["preferred_username"], point_release="8_3",
                                       import_commit_id=import_commit.id, **extras)
            await build_package_task(package.id, build.id, token)

    return {}


@router.post("/batch", status_code=202)
async def batch_queue_build(request: Request, body: BatchBuildRequest):
    for build_request in body.packages:
        await queue_build(request, dict(build_request))

    return {}
