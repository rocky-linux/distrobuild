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

import json

from distrobuild.common import tags
from distrobuild.models import Package, PackageModule, Repo
from distrobuild.session import koji_session
from distrobuild.settings import settings


async def _internal_create_package(**kwargs) -> Package:
    return await Package.create(
        el8=True if settings.version == 8 else False,
        el9=True if settings.version == 9 else False,
        **kwargs,
    )


async def process_repo_dump(repo: Repo, responsible_username: str) -> None:
    with open(f"/tmp/{repo}_ALL.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            package_name = line.strip()
            existing_package = await Package.filter(name=package_name, repo__not=Repo.MODULAR_CANDIDATE).get_or_none()
            if existing_package and repo != Repo.MODULAR_CANDIDATE:
                existing_package.repo = repo
                existing_package.is_package = True
                await existing_package.save()
                continue

            is_package = True
            if repo == Repo.MODULAR_CANDIDATE:
                koji_session.packageListAdd(tags.modular_updates_candidate(), package_name, "distrobuild")
                is_package = False

            await _internal_create_package(name=package_name,
                                           is_package=is_package,
                                           repo=repo,
                                           responsible_username=responsible_username)


async def process_module_dump(responsible_username: str) -> None:
    f = open("/tmp/modules.json")
    module_list = json.loads(f.read())
    f.close()

    for module in module_list.keys():
        package_name = module.strip()
        existing_package = await Package.filter(name=package_name, repo__not=Repo.MODULAR_CANDIDATE).get_or_none()
        if existing_package:
            if not existing_package.is_module and existing_package.repo != Repo.MODULAR_CANDIDATE:
                existing_package.is_module = True
                await existing_package.save()
        else:
            existing_package = await _internal_create_package(name=package_name,
                                                              is_module=True,
                                                              responsible_username=responsible_username)

        subpackages = [x.strip() for x in module_list[module].split(",")]
        for module_package in subpackages:
            if len(module_package.strip()) == 0:
                continue
            m_package_name = module_package.strip()
            m_packages = await Package.filter(name=m_package_name, is_module=False).all()

            for m_package in m_packages:
                if m_package and m_package.repo != Repo.MODULAR_CANDIDATE:
                    m_package.part_of_module = True

                # Either this is safe to skip, or it will cause build failure later
                # This is not a bug though as all package records should be up to
                # date before bootstrapping the module list
                if not m_package:
                    continue

                await m_package.save()

                existing_pm_count = await PackageModule.filter(package_id=m_package.id).count()
                if existing_pm_count == 0:
                    await PackageModule.create(package_id=m_package.id, module_parent_package_id=existing_package.id)
