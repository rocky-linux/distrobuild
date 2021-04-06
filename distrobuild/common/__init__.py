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

from typing import List, Tuple

from fastapi import Request, HTTPException

from distrobuild.models import Import, ImportStatus, Package, PackageModule
from distrobuild.settings import settings


def gen_body_filters(body: dict) -> dict:
    if body.get("package_name"):
        return {"name": body["package_name"]}
    if body.get("package_id"):
        return {"id": body["package_id"]}


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
