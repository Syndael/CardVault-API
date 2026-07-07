from marshmallow import Schema, fields


class PublicationScheduleSchema(Schema):
    id = fields.Int(dump_only=True)
    inventory_id = fields.Int(required=True)
    scheduled_at = fields.DateTime(required=True)
    published_at = fields.DateTime(dump_only=True, allow_none=True)
    status = fields.Str(allow_none=True)
    caption = fields.Str(allow_none=True)
    instagram_media_id = fields.Str(dump_only=True, allow_none=True)
    instagram_permalink = fields.Str(dump_only=True, allow_none=True)
    error_message = fields.Str(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    inventory = fields.Nested("app.schemas.inventory_schema.InventorySchema",
                              dump_only=True, allow_none=True,
                              exclude=("tags",))
