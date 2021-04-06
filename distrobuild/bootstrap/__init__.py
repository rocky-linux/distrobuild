import json

from distrobuild.models import Package, PackageModule, Repo
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
            existing_package = await Package.filter(name=package_name).get_or_none()
            if existing_package:
                existing_package.repo = repo
                existing_package.is_package = True
                await existing_package.save()
                continue
            await _internal_create_package(name=package_name,
                                           is_package=True,
                                           repo=repo,
                                           responsible_username=responsible_username)


async def process_module_dump(responsible_username: str) -> None:
    f = open("/tmp/modules.json")
    module_list = json.loads(f.read())
    f.close()

    for module in module_list.keys():
        package_name = module.strip()
        existing_package = await Package.filter(name=package_name).get_or_none()
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
            m_package_name = module_package.strip()
            m_package = await Package.filter(name=m_package_name).get_or_none()

            if m_package and m_package.repo != Repo.MODULAR_CANDIDATE:
                m_package.part_of_module = True

            if not m_package:
                m_package = await _internal_create_package(name=m_package_name,
                                                           repo=Repo.MODULAR_CANDIDATE,
                                                           responsible_username=responsible_username)

            await m_package.save()
            await PackageModule.create(package_id=m_package.id, module_parent_package_id=existing_package.id)
