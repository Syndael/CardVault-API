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
    photo_count = fields.Method("get_photo_count", dump_only=True)
    first_photo_id = fields.Method("get_first_photo_id", dump_only=True)

    def get_photo_count(self, obj):
        if obj.inventory and obj.inventory.files:
            return sum(1 for f in obj.inventory.files if f.instagram_sort_order is not None)
        return 0

    def get_first_photo_id(self, obj):
        if obj.inventory and obj.inventory.files:
            ig_files = [f for f in obj.inventory.files if f.instagram_sort_order is not None]
            if ig_files:
                ig_files.sort(key=lambda f: f.instagram_sort_order or 0)
                return ig_files[0].id
        return None
