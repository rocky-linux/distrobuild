import asyncio
import datetime

import koji

from distrobuild.models import Build, BuildStatus, Package
from distrobuild.session import koji_session, mbs_client

from distrobuild_scheduler import logger


async def check_build_status():
    while True:
        logger.debug("[*] Running periodic task: check_build_status")
        builds = await Build.filter(status=BuildStatus.BUILDING).all()
        for build in builds:
            if build.koji_id:
                task_info = koji_session.getTaskInfo(build.koji_id, request=True)
                if task_info["state"] == koji.TASK_STATES["CLOSED"]:
                    build.status = BuildStatus.SUCCEEDED
                    await build.save()

                    package = await Package.filter(id=build.package_id).get()
                    package.last_build = datetime.datetime.now()
                    await package.save()
                elif task_info["state"] == koji.TASK_STATES["CANCELED"]:
                    build.status = BuildStatus.CANCELLED
                    await build.save()
                elif task_info["state"] == koji.TASK_STATES["FAILED"]:
                    try:
                        task_result = koji_session.getTaskResult(build.koji_id)
                        print(task_result)
                    except koji.BuildError:
                        build.status = BuildStatus.FAILED
                    except koji.GenericError:
                        build.status = BuildStatus.CANCELLED
                    finally:
                        await build.save()
            elif build.mbs_id:
                build_info = await mbs_client.get_build(build.mbs_id)
                state = build_info["state_name"]
                if state == "ready":
                    build.status = BuildStatus.SUCCEEDED
                    await build.save()

                    package = await Package.filter(id=build.package_id).get()
                    package.last_build = datetime.datetime.now()
                    await package.save()
                elif state == "failed":
                    build.status = BuildStatus.FAILED
                    await build.save()

        # run every 5 minutes
        await asyncio.sleep(60 * 5)
