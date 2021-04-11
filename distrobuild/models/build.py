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
from distrobuild.models.enums import BuildStatus, ImportStatus


class Import(Model):
    id = fields.BigIntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_add=True, null=True)
    package = fields.ForeignKeyField("distrobuild.Package", on_delete="RESTRICT", related_name="imports")
    status = fields.CharEnumField(ImportStatus)
    module = fields.BooleanField(default=False)
    version = fields.IntField()
    executor_username = fields.CharField(max_length=255)

    commits: fields.ManyToManyRelation["ImportCommit"] = fields.ManyToManyField("distrobuild.ImportCommit",
                                                                                related_name="imports",
                                                                                forward_key="id",
                                                                                backward_key="import__id",
                                                                                through="import_commits")

    class Meta:
        table = "imports"
        ordering = ["-created_at"]

    class PydanticMeta:
        exclude = ("batch_imports",)


class ImportCommit(Model):
    id = fields.BigIntField(pk=True)
    commit = fields.CharField(max_length=255)
    branch = fields.CharField(max_length=255)
    import__id = fields.BigIntField()

    class Meta:
        table = "import_commits"

    class PydanticMeta:
        exclude = ("import_", "imports", "builds")


class Build(Model):
    id = fields.BigIntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_add=True, null=True)
    package = fields.ForeignKeyField("distrobuild.Package", on_delete="RESTRICT", related_name="builds")
    status = fields.CharEnumField(BuildStatus)
    mbs = fields.BooleanField(default=False)
    signed = fields.BooleanField(default=False)
    koji_id = fields.BigIntField(null=True)
    mbs_id = fields.BigIntField(null=True)
    import_commit = fields.ForeignKeyField("distrobuild.ImportCommit", on_delete="RESTRICT", related_name="builds")
    executor_username = fields.CharField(max_length=255)
    force_tag = fields.CharField(max_length=255, null=True)
    exclude_compose = fields.BooleanField(default=False)
    point_release = fields.CharField(max_length=255)

    class Meta:
        table = "builds"
        ordering = ["-created_at"]

    class PydanticMeta:
        exclude = ("batch_builds",)


class Logs(Model):
    id = fields.BigIntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    content = fields.TextField()

    class Meta:
        table = "logs"
