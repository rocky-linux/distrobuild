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
