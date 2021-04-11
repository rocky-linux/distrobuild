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

from tortoise import Model, fields

from distrobuild.models.build import Build, Import
from distrobuild.models.enums import Repo


class Package(Model):
    id = fields.BigIntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_add=True, null=True)
    name = fields.CharField(max_length=255)
    responsible_username = fields.CharField(max_length=255)
    is_module = fields.BooleanField(default=False)
    is_package = fields.BooleanField(default=False)
    is_published = fields.BooleanField(default=False)
    part_of_module = fields.BooleanField(default=False)
    signed = fields.BooleanField(default=False)
    last_import = fields.DatetimeField(null=True)
    last_build = fields.DatetimeField(null=True)

    el8 = fields.BooleanField(default=False)
    el9 = fields.BooleanField(default=False)
    repo = fields.CharEnumField(Repo, null=True)

    builds: Optional[fields.ReverseRelation[Build]]
    imports: Optional[fields.ReverseRelation[Import]]

    class Meta:
        table = "packages"

    class PydanticMeta:
        exclude = ("m_module_parent_packages", "m_subpackages")


class PackageModule(Model):
    id = fields.BigIntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_add=True, null=True)
    package = fields.ForeignKeyField("distrobuild.Package", on_delete="RESTRICT", related_name="m_subpackages")
    module_parent_package = fields.ForeignKeyField("distrobuild.Package", on_delete="RESTRICT",
                                                   related_name="m_module_parent_packages")

    class Meta:
        table = "package_modules"

    class PydanticMeta:
        backward_relations = False
