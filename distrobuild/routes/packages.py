from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi_pagination import Page, pagination_params
from fastapi_pagination.ext.tortoise import paginate

from distrobuild.models import Package
from distrobuild.pydantic import Package_Pydantic

router = APIRouter(prefix="/packages")

@router.get("/", response_model=Page[Package_Pydantic], dependencies=[Depends(pagination_params)])
async def list_packages(name: Optional[str] = None, modules_only: bool = False, non_modules_only: bool = False):
    filters = {}
    if name:
        filters["name__icontains"] = name
    if modules_only:
        filters["is_module"] = True
    if non_modules_only:
        filters["is_module"] = False
        filters["part_of_module"] = False
    return await paginate(Package.all().order_by('updated_at', 'name').filter(**filters))
