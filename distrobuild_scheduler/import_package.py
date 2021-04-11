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

import datetime

from typing import List, Tuple

from tortoise.transactions import atomic

from distrobuild.models import ImportStatus, Package, Import, ImportCommit
from distrobuild.session import koji_session, gl
from distrobuild.settings import settings
from distrobuild import srpmproc

from distrobuild_scheduler.utils import gitlabify


@atomic()
async def do(package: Package, package_import: Import):
    tag = f"dist-{settings.tag_prefix}{settings.version}"
    koji_session.packageListAdd(tag, package.name, "distrobuild")

    branch_commits = await srpmproc.import_project(package_import.id, package.name, package_import.module)
    for branch in branch_commits.keys():
        commit = branch_commits[branch]
        await ImportCommit.create(branch=branch, commit=commit, import__id=package_import.id)

    package.last_import = datetime.datetime.now()

    mode = "modules" if package_import.module else "rpms"
    project = gl.projects.get(f"{settings.repo_prefix[1:]}/{mode}/{gitlabify(package.name)}")
    project.visibility = "public"
    project.save()


# noinspection DuplicatedCode
async def task(package_id: int, import_id: int, dependents: List[Tuple[int, int]]):
    package = await Package.filter(id=package_id).get()
    package_import = await Import.filter(id=import_id).get()

    if package_import.status != ImportStatus.CANCELLED:
        try:
            package_import.status = ImportStatus.IN_PROGRESS
            await package_import.save()

            await do(package, package_import)
        except Exception as e:
            print(e)
            package_import.status = ImportStatus.FAILED
            package.last_import = None
        else:
            package_import.status = ImportStatus.SUCCEEDED
        finally:
            await package_import.save()
            await package.save()

    if len(dependents) > 0:
        await task(dependents[0][0], dependents[0][1], dependents[1:])
