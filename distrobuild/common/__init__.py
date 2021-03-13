from typing import List, Tuple

from fastapi import Request, HTTPException

from distrobuild.models import Import, ImportStatus, Package, PackageModule
from distrobuild.settings import settings


def gen_body_filters(body: dict) -> dict:
    if body["package_id"]:
        return {"id": body["package_id"]}
    if body["package_name"]:
        return {"name": body["package_name"]}


async def create_import_order(package: Package, username: str) -> List[Tuple[int, int]]:
    pkg_list = []

    if package.is_package:
        package_import = await Import.create(package_id=package.id, status=ImportStatus.QUEUED,
                                             executor_username=username, version=settings.version)
        pkg_list.append((package.id, package_import.id))

    if package.is_module:
        subpackages = await PackageModule.filter(module_parent_package_id=package.id).all()
        for subpackage in subpackages:
            imports = await Import.filter(package_id=subpackage.package_id).all()
            if not imports or len(imports) == 0:
                subpackage_package = await Package.filter(id=subpackage.package_id).get()
                pkg_list += await create_import_order(subpackage_package, username)

        package_module_import = await Import.create(package_id=package.id, status=ImportStatus.QUEUED,
                                                    module=True, executor_username=username, version=settings.version)
        pkg_list.append((package.id, package_module_import.id))

    return pkg_list


def get_user(request: Request) -> dict:
    user = request.session.get("user")
    token = request.session.get("token")
    if not user or not token:
        if request.session.get("token"):
            request.session.pop("token")
        if request.session.get("user"):
            request.session.pop("user")
        raise HTTPException(401, "not authenticated")

    return user
