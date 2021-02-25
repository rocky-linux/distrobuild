from typing import List, Tuple, Optional

from pydantic import BaseModel, validator

from distrobuild.models import Import, Package, PackageModule, BuildStatus


class BuildRequest(BaseModel):
    package_id: Optional[int]
    package_name: Optional[str]

    @validator('package_name')
    def validate(cls, package_name, values):
        if (not values.get('package_id') and not package_name) or (values.get('package_id') and package_name):
            raise ValueError('either package_id or package_name is required')
        return package_name


class BatchBuildRequest(BaseModel):
    packages: List[BuildRequest]


def gen_body_filters(body_in) -> dict:
    body = BuildRequest(**body_in)
    if body.package_id:
        return {"id": body.package_id}
    if body.package_name:
        return {"name": body.package_name}


async def create_build_order(package: Package) -> List[Tuple[int, int]]:
    pkg_list = []

    if package.is_package:
        package_import = await Import.create(package_id=package.id, status=BuildStatus.QUEUED, version=8)
        pkg_list.append((package.id, package_import.id))

    if package.is_module:
        subpackages = await PackageModule.filter(module_parent_package_id=package.id).all()
        for subpackage in subpackages:
            imports = await Import.filter(package_id=subpackage.package_id).all()
            if not imports or len(imports) == 0:
                subpackage_package = await Package.filter(id=subpackage.package_id).get()
                pkg_list += await create_build_order(subpackage_package)

        package_module_import = await Import.create(package_id=package.id, status=BuildStatus.QUEUED, version=8,
                                                    module=True)
        pkg_list.append((package.id, package_module_import.id))

    return pkg_list
