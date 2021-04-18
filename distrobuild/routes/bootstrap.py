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
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from tortoise.transactions import atomic

from distrobuild.bootstrap import process_repo_dump, process_module_dump
from distrobuild.common import get_user
from distrobuild.models import Repo, Package, Build, Import, ImportStatus, ImportCommit, BuildStatus
from distrobuild.session import koji_session
from distrobuild.settings import settings

router = APIRouter(prefix="/bootstrap")


@atomic()
async def import_build_from_koji(username: str, package: Package, koji_build):
    new_import = await Import.create(package_id=package.id, status=ImportStatus.SUCCEEDED,
                                     executor_username=username, version=settings.version)

    commit = koji_build["source"].split("#")[1]
    import_commit = await ImportCommit.create(branch=f"{settings.original_import_branch_prefix}{settings.version}",
                                              commit=commit, import__id=new_import.id)
    package.last_import = datetime.now()
    package.last_build = datetime.now()

    await Build.create(package_id=package.id, status=BuildStatus.SUCCEEDED,
                       executor_username=username,
                       point_release=f"{settings.version}_{settings.default_point_release}",
                       import_commit_id=import_commit.id, koji_id=koji_build["task_id"])

    await package.save()


@router.post("/modules")
async def bootstrap_modules(request: Request):
    user = get_user(request)
    await process_module_dump(user["preferred_username"])
    return JSONResponse(content={})


@router.post("/import_from_koji", status_code=202)
async def import_from_koji(request: Request):
    user = get_user(request)

    all_koji_builds = koji_session.listBuilds()

    packages_without_builds = await Package.filter(last_build__isnull=True).all()
    for package in packages_without_builds:
        for koji_build in all_koji_builds:
            if package.name == koji_build["name"] and not package.is_module and not package.part_of_module and \
                    koji_build["state"] == 1:
                await import_build_from_koji(user["preferred_username"], package, koji_build)

    return {}


@router.post("/{repo}")
async def bootstrap_repo(request: Request, repo: Repo):
    user = get_user(request)
    await process_repo_dump(repo, user["preferred_username"])
    return JSONResponse(content={})
