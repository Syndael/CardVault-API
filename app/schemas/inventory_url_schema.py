from marshmallow import Schema, fields


class InventoryUrlSchema(Schema):
    id = fields.Int(dump_only=True)
    inventory_id = fields.Int(required=True, load_only=True)
    url = fields.Str(required=True)
    name = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
