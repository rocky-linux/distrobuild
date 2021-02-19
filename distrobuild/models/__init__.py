from enum import Enum

from tortoise import Model, fields


class Repo(str, Enum):
    BASEOS = "BASEOS"
    APPSTREAM = "APPSTREAM"
    POWERTOOLS = "POWERTOOLS"


class BuildStatus(str, Enum):
    QUEUED = "QUEUED"
    BUILDING = "BUILDING"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"
    CANCELLED = "CANCELLED"


class Package(Model):
    id = fields.BigIntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_add=True, null=True)
    name = fields.CharField(max_length=255)
    responsible_user_id = fields.CharField(max_length=255, null=True)
    is_module = fields.BooleanField(default=False)
    is_package = fields.BooleanField(default=False)
    part_of_module = fields.BooleanField(default=False)
    last_import = fields.DatetimeField(null=True)

    el8 = fields.BooleanField(default=False)
    repo = fields.CharEnumField(Repo, null=True)

    class Meta:
        table = "packages"

    class PydanticMeta:
        backward_relations = False


class PackageModule(Model):
    id = fields.BigIntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_add=True, null=True)
    package = fields.ForeignKeyField("distrobuild.Package", on_delete="RESTRICT", related_name="m_subpackages")
    module_parent_package = fields.ForeignKeyField("distrobuild.Package", on_delete="RESTRICT",
                                                   related_name="m_module_parent_pacakges")

    class PydanticMeta:
        backward_relations = False


class Build(Model):
    id = fields.BigIntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_add=True, null=True)
    package = fields.ForeignKeyField("distrobuild.Package", on_delete="CASCADE")
    status = fields.CharEnumField(BuildStatus)
    mbs = fields.BooleanField(default=False)
    koji_id = fields.BigIntField(null=True)
    mbs_id = fields.BigIntField(null=True)
    commit = fields.CharField(max_length=255)
    branch = fields.CharField(max_length=255)

    class Meta:
        table = "builds"


class Import(Model):
    id = fields.BigIntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_add=True, null=True)
    package = fields.ForeignKeyField("distrobuild.Package", on_delete="CASCADE")
    status = fields.CharEnumField(BuildStatus)
    version = fields.IntField()
    module = fields.BooleanField(default=False)

    commits: fields.ReverseRelation["ImportCommit"] = fields.ReverseRelation

    class Meta:
        table = "imports"

    class PydanticMeta:
        backward_relations = False


class ImportCommit(Model):
    id = fields.BigIntField(pk=True)
    commit = fields.CharField(max_length=255)
    branch = fields.CharField(max_length=255)
    import_ = fields.ForeignKeyField("distrobuild.Import", on_delete="CASCADE")

    class Meta:
        table = "import_commits"
