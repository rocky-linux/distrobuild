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

from tortoise import Model, fields
from distrobuild.models.build import Import, Build


class BatchImport(Model):
    id = fields.BigIntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_add=True, null=True)

    imports: fields.ManyToManyRelation[Import] = fields.ManyToManyField("distrobuild.Import",
                                                                        related_name="batch_imports",
                                                                        backward_key="batch_import_id",
                                                                        through="batch_import_packages")

    class Meta:
        table = "batch_imports"


class BatchBuild(Model):
    id = fields.BigIntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_add=True, null=True)

    builds: fields.ManyToManyRelation[Build] = fields.ManyToManyField("distrobuild.Build",
                                                                      related_name="batch_builds",
                                                                      backward_key="batch_build_id",
                                                                      through="batch_build_packages")

    class Meta:
        table = "batch_builds"


class BatchImportPackage(Model):
    id = fields.BigIntField(pk=True)
    import_id = fields.BigIntField()
    batch_import_id = fields.BigIntField()

    class Meta:
        table = "batch_import_packages"


class BatchBuildPackage(Model):
    id = fields.BigIntField(pk=True)
    build_id = fields.BigIntField()
    batch_build_id = fields.BigIntField()

    class Meta:
        table = "batch_build_packages"
