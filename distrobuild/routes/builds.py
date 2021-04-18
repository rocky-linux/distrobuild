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
from fastapi_pagination import Page, pagination_params
from fastapi_pagination.ext.tortoise import paginate
from pydantic import BaseModel, validator

from distrobuild.common import gen_body_filters, get_user
from distrobuild.models import Build, Import, ImportCommit, Package, PackageModule, BuildStatus, Repo, BatchBuildPackage
from distrobuild.serialize import Build_Pydantic, BuildGeneral_Pydantic
from distrobuild.session import message_cipher
from distrobuild.settings import settings
from distrobuild_scheduler import build_package_task, merge_scratch_task

router = APIRouter(prefix="/builds")


class BuildRequest(BaseModel):
    scratch: bool = False
    ignore_modules: bool = False
    arch_override: Optional[str]
    force_tag: Optional[str]
    only_branch: Optional[str]
    package_id: Optional[int]
    package_name: Optional[str]

    @validator("package_name")
    def validate(cls, package_name, values):
        if (not values.get("package_id") and not package_name) or (values.get("package_id") and package_name):
            raise ValueError("either package_id or package_name is required")
        return package_name


@router.get("/", response_model=Page[BuildGeneral_Pydantic], dependencies=[Depends(pagination_params)])
async def list_builds():
    return await paginate(Build.all().order_by("-created_at").prefetch_related("package", "import_commit"))


@router.get("/{build_id}", response_model=Build_Pydantic)
async def get_build(build_id: int):
    return await Build_Pydantic.from_queryset_single(
        Build.filter(id=build_id).prefetch_related("package", "import_commit").first()
    )


@router.post("/{build_id}/cancel", status_code=202)
async def cancel_build(request: Request, build_id: int):
    get_user(request)

    build_obj = await Build.filter(id=build_id, cancelled=False).get_or_none()
    if not build_obj:
        raise HTTPException(404, detail="build does not exist or is already cancelled")

    build_obj.status = BuildStatus.CANCELLED
    await build_obj.save()

    return {}


@router.post("/{build_id}/merge_scratch", status_code=202)
async def merge_build(request: Request, build_id: int):
    get_user(request)

    build_obj = await Build.filter(id=build_id, scratch_merged=False, scratch=True).get_or_none()
    if not build_obj:
        raise HTTPException(404, detail="build does not exist, is already merged or not a scratch build")

    await merge_scratch_task(build_obj.id)

    return {}


@router.post("/", status_code=202)
async def queue_build(request: Request, body: Dict[str, BuildRequest], batch_build_id: Optional[int] = None):
    user = get_user(request)

    filters = gen_body_filters(body)
    package = await Package.filter(**filters).get_or_none()
    if not package:
        raise HTTPException(404, detail="package does not exist")

    if package.repo == Repo.MODULAR_CANDIDATE:
        raise HTTPException(400, detail="modular subpackages cannot be built, build the main module")

    extras = {}
    token = None

    if body.get("force_tag"):
        extras["force_tag"] = body.get("force_tag")

    if body.get("scratch"):
        extras["scratch"] = True

        latest_build = await Build.filter(package_id=package.id, status=BuildStatus.SUCCEEDED).prefetch_related(
            "import_commit").order_by(
            "-created_at").first()
        import_commits = [latest_build.import_commit]
    else:
        latest_import = await Import.filter(package_id=package.id).order_by("-created_at").first()
        import_commits = await ImportCommit.filter(import__id=latest_import.id).all()

    if body.get("arch_override"):
        extras["arch_override"] = body.get("arch_override")

    only_branch = body.get("only_branch")
    for import_commit in import_commits:
        if "-beta" not in import_commit.branch:
            if only_branch and import_commit.branch != only_branch:
                continue

            stream_branch_prefix = f"{settings.original_import_branch_prefix}{settings.version}-stream"
            if import_commit.branch.startswith(stream_branch_prefix):
                if body.get("ignore_modules"):
                    continue
                if package.part_of_module and not package.is_module:
                    continue
                extras["mbs"] = True
                if not token:
                    token = request.session.get("token")

            # temporarily skip containeronly streams
            containeronly_stream_prefix = f"{settings.original_import_branch_prefix}{settings.version}-containeronly-stream"
            if import_commit.branch.startswith(containeronly_stream_prefix):
                continue

            build = await Build.create(package_id=package.id, status=BuildStatus.QUEUED,
                                       executor_username=user["preferred_username"],
                                       point_release=f"{settings.version}_{settings.default_point_release}",
                                       import_commit_id=import_commit.id, **extras)
            if batch_build_id:
                await BatchBuildPackage.create(build_id=build.id, batch_build_id=batch_build_id)
            await build_package_task(package.id, build.id, token)

    return {}
