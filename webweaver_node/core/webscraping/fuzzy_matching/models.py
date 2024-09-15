from tortoise import Model, fields
from webweaver_node.common.enums import EntitiesEnum


class FuzzyMatch(Model):

    table           = fields.CharEnumField(EntitiesEnum)
    object_id       = fields.IntField()
    fuzzy_name      = fields.CharField(max_length=255)
    score           = fields.SmallIntField()
    date_created    = fields.DatetimeField(auto_now_add=True)


class FuzzyNearMatch(Model):

    table           = fields.CharEnumField(EntitiesEnum)
    object_one      = fields.IntField()
    obect_two       = fields.IntField()
    score           = fields.SmallIntField()
    date_created    = fields.DatetimeField(auto_now_add=True)

