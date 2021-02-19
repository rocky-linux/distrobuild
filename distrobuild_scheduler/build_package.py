from tortoise.transactions import atomic

from distrobuild.models import Build, BuildStatus, Package
from distrobuild.session import koji_session
from distrobuild.settings import settings


@atomic()
async def do(package: Package, build: Build):
    if build.mbs:
        pass
    else:
        target = "dist-rocky8"

        source = f"git+https://{settings.gitlab_host}{settings.repo_prefix}/rpms/{package.name}.git?#{build.commit}"
        task_id = koji_session.build(source, target)

        build.koji_id = task_id
        build.status = BuildStatus.BUILDING
        await build.save()


# noinspection DuplicatedCode
async def task(package_id: int, build_id):
    build = await Build.filter(id=build_id).get()
    package = await Package.filter(id=package_id).get()
    try:
        await do(package, build)
    except Exception as e:
        print(e)
        build.status = BuildStatus.FAILED
    finally:
        await build.save()
        await package.save()
