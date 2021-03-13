import datetime

from typing import List, Tuple

from tortoise.transactions import atomic

from distrobuild.models import ImportStatus, Package, Import, ImportCommit
from distrobuild.session import koji_session, gl
from distrobuild.settings import settings
from distrobuild import srpmproc


@atomic()
async def do(package: Package, package_import: Import):
    package_import.status = ImportStatus.IN_PROGRESS
    await package_import.save()

    if not package.is_module and not package.part_of_module:
        tag = f"dist-{settings.tag_prefix}{settings.version}"
        koji_session.packageListAdd(tag, package.name, "distrobuild")

    branch_commits = await srpmproc.import_project(package_import.id, package.name, package_import.module)
    for branch in branch_commits.keys():
        commit = branch_commits[branch]
        await ImportCommit.create(branch=branch, commit=commit, import__id=package_import.id)

    package.last_import = datetime.datetime.now()

    mode = "modules" if package_import.module else "rpms"
    project = gl.projects.get(f"{settings.repo_prefix.removeprefix('/')}/{mode}/{package.name}")
    project.visibility = "public"
    project.save()


# noinspection DuplicatedCode
async def task(package_id: int, import_id: int, dependents: List[Tuple[int, int]]):
    package = await Package.filter(id=package_id).get()
    package_import = await Import.filter(id=import_id).get()
    try:
        await do(package, package_import)
    except Exception as e:
        print(e)
        package_import.status = ImportStatus.FAILED
    else:
        package_import.status = ImportStatus.SUCCEEDED
    finally:
        await package_import.save()
        await package.save()

    if len(dependents) > 0:
        await task(dependents[0][0], dependents[0][1], dependents[1:])
