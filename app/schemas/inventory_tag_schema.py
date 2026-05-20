from marshmallow import Schema, fields

from app.schemas.tag_schema import TagSchema


class InventoryTagSchema(Schema):
    inventory_id = fields.Int(required=True)
    tag_id       = fields.Int(required=True)
    created_at   = fields.DateTime(dump_only=True)
    tag          = fields.Nested(TagSchema, dump_only=True)
