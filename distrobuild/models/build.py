from tortoise import Model, fields
from distrobuild.models.enums import BuildStatus


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
