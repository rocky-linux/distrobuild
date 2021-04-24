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

import asyncio
import datetime
import xmlrpc

import koji
from tortoise.transactions import atomic

from distrobuild.common import tags
from distrobuild.models import Build, BuildStatus, Package, PackageModule, Repo
from distrobuild.session import koji_session, mbs_client
from distrobuild.settings import settings

from distrobuild_scheduler import logger
from distrobuild_scheduler.sigul import sign_koji_package


async def sign_build_rpms(build_rpms):
    for build_rpm in build_rpms:
        rpm_sigs = koji_session.queryRPMSigs(build_rpm["id"])
        for rpm_sig in rpm_sigs:
            if rpm_sig["sigkey"] == settings.sigul_key_id:
                continue

        nvr_arch = "%s.%s" % (build_rpm["nvr"], build_rpm["arch"])
        await sign_koji_package(nvr_arch)
        koji_session.writeSignedRPM(nvr_arch, settings.sigul_key_id)


def tag_if_not_tagged(build_history, nvr, tag):
    if "tag_listing" in build_history:
        for t in build_history["tag_listing"]:
            if t["tag.name"] == tag:
                return

    koji_session.tagBuild(tag, nvr)


@atomic()
async def atomic_sign_unsigned_builds(build: Build):
    if build.koji_id:
        koji_session.packageListAdd(tags.compose(), build.package.name, "distrobuild")

        build_tasks = koji_session.listBuilds(taskID=build.koji_id)
        for build_task in build_tasks:
            build_history = koji_session.queryHistory(build=build_task["build_id"])
            tag_if_not_tagged(build_history, build_task["nvr"], tags.compose())

            build_rpms = koji_session.listBuildRPMs(build_task["build_id"])
            await sign_build_rpms(build_rpms)

        build.signed = True
        await build.save()
    elif build.mbs_id:
        mbs_build = await mbs_client.get_build(build.mbs_id)
        rpms = mbs_build["tasks"]["rpms"]
        for rpm_name in rpms.keys():
            if rpm_name == "module-build-macros":
                continue
            rpm = rpms[rpm_name]
            if rpm["state"] != 1:
                continue

            build_rpms = koji_session.listBuildRPMs(rpm["nvr"])
            if len(build_rpms) > 0:
                package_modules = await PackageModule.filter(
                    module_parent_package_id=build.package.id).prefetch_related(
                    "package").all()
                for package_module in package_modules:
                    package_module_package = await Package.filter(id=package_module.package.id).first()
                    package_module_package.last_build = datetime.datetime.now()
                    await package_module_package.save()

                    if package_module.package.repo != Repo.MODULAR_CANDIDATE:
                        continue
                    koji_session.packageListAdd(tags.module_compose(), package_module.package.name, "distrobuild")
                    koji_package = koji_session.getPackage(package_module.package.name)
                    koji_builds = koji_session.listBuilds(koji_package["id"])
                    for koji_build in koji_builds:
                        if koji_build["source"] == mbs_build["scmurl"]:
                            tag_if_not_tagged([], koji_build["nvr"], tags.module_compose())
                            break

                await sign_build_rpms(build_rpms)

        build.signed = True
        await build.save()


@atomic()
async def atomic_check_build_status(build: Build):
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
                logger.debug(task_result)
            except (koji.BuildError, xmlrpc.client.Fault):
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


async def check_build_status():
    while True:
        logger.debug("[*] Running periodic task: check_build_status")

        builds = await Build.filter(status=BuildStatus.BUILDING).all()
        for build in builds:
            try:
                await atomic_check_build_status(build)
            except Exception as e:
                logger.error(f"check_build_status: {e}")

        # run every 5 minutes
        await asyncio.sleep(60 * 5)


async def sign_unsigned_builds():
    if not settings.disable_sigul:
        while True:
            logger.debug("[*] Running periodic task: sign_unsigned_builds")

            builds = await Build.filter(signed=False, status=BuildStatus.SUCCEEDED).prefetch_related(
                "package").all()
            for build in builds:
                try:
                    await atomic_sign_unsigned_builds(build)
                except Exception as e:
                    logger.error(f"sign_unsigned_builds: {e}")

            # run every 5 minutes
            await asyncio.sleep(60 * 5)
