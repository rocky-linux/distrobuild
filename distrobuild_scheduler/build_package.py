import datetime

from typing import Optional

from tortoise.transactions import atomic

from distrobuild.common import tags
from distrobuild.mbs import MBSConflictException
from distrobuild.models import Build, BuildStatus, Package
from distrobuild.session import koji_session, mbs_client
from distrobuild.settings import settings


@atomic()
async def do(package: Package, build: Build, token: Optional[str]):
    try:
        if build.mbs:
            task_id = await mbs_client.build(token, package.name, build.import_commit.branch, build.import_commit.commit)

            build.mbs_id = task_id
            build.status = BuildStatus.BUILDING
            await build.save()
        else:
            target = tags.base() if not build.force_tag else build.force_tag

            host = f"git+https://{settings.gitlab_host}{settings.repo_prefix}"
            source = f"{host}/rpms/{package.name}.git?#{build.import_commit.commit}"
            task_id = koji_session.build(source, target)

            build.koji_id = task_id
            build.status = BuildStatus.BUILDING
            await build.save()
    except MBSConflictException:
        build.status = BuildStatus.CANCELLED
        await build.save()
    except Exception:
        raise
    else:
        package.last_import = datetime.datetime.now()
        await package.save()


# noinspection DuplicatedCode
async def task(package_id: int, build_id: int, token: Optional[str]):
    build = await Build.filter(id=build_id).prefetch_related("import_commit").get()
    package = await Package.filter(id=package_id).get()
    try:
        await do(package, build, token)
    except Exception as e:
        print(e)
        build.status = BuildStatus.FAILED
    finally:
        await build.save()
        await package.save()
