import json

from distrobuild.models import Package, PackageModule, Repo


async def process_repo_dump(repo: Repo) -> None:
    with open(f"/tmp/{repo}_ALL.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            package_name = line.strip()
            if await Package.filter(name=package_name).get_or_none():
                continue
            await Package.create(name=package_name, el8=True, is_package=True, repo=repo)


async def process_module_dump() -> None:
    f = open("/tmp/modules.json")
    module_list = json.loads(f.read())
    f.close()

    for module in module_list.keys():
        package_name = module.strip()
        existing_package = await Package.filter(name=package_name).get_or_none()
        if existing_package:
            if not existing_package.is_module:
                existing_package.is_module = True
                await existing_package.save()
        else:
            existing_package = await Package.create(name=package_name, el8=True, is_module=True)

        subpackages = [x.strip() for x in module_list[module].split(",")]
        for module_package in subpackages:
            m_package_name = module_package.strip()
            m_package = await Package.filter(name=m_package_name).get_or_none()
            if not m_package:
                continue

            m_package.part_of_module = True
            await m_package.save()
            await PackageModule.create(package_id=m_package.id, module_parent_package_id=existing_package.id)
