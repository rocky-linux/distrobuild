from tortoise import Model, fields
from distrobuild.models.enums import Repo


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
    last_build = fields.DatetimeField(null=True)

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
