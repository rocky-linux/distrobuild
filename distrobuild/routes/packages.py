from typing import Optional

from fastapi import APIRouter, Depends
from fastapi_pagination import Page, pagination_params
from fastapi_pagination.ext.tortoise import paginate

from distrobuild.models import Package, Repo
from distrobuild.serialize import Package_Pydantic

router = APIRouter(prefix="/packages")


@router.get("/", response_model=Page[Package_Pydantic], dependencies=[Depends(pagination_params)])
async def list_packages(name: Optional[str] = None, modules_only: bool = False, non_modules_only: bool = False,
                        exclude_modular_candidates: bool = False):
    filters = {}
    if name:
        filters["name__icontains"] = name
    if modules_only:
        filters["is_module"] = True
    if non_modules_only:
        filters["is_package"] = True
    if exclude_modular_candidates:
        filters["repo__not"] = Repo.MODULAR_CANDIDATE

    return await paginate(Package.all().order_by("updated_at", "name").filter(**filters))


@router.get("/{package_id}", response_model=Package_Pydantic)
async def get_package(package_id: int):
    return await Package_Pydantic.from_queryset_single(Package.filter(id=package_id).first())
