from marshmallow import Schema, fields


class PublicationInventorySummarySchema(Schema):
    id = fields.Int(dump_only=True)
    product_name = fields.Method("_product_name", dump_only=True)
    collection_code = fields.Method("_collection_code", dump_only=True)
    product_number = fields.Method("_product_number", dump_only=True)

    def _product_name(self, obj):
        prod = getattr(obj, "product", None)
        if prod and prod.translations:
            return (prod.translations[0].name) if prod.translations else None
        return None

    def _collection_code(self, obj):
        col = getattr(obj, "collection", None)
        return col.code if col else None

    def _product_number(self, obj):
        prod = getattr(obj, "product", None)
        return prod.product_number if prod else None


class PublicationScheduleSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(allow_none=True)
    inventory_id = fields.Method("_first_inventory_id", dump_only=True)
    scheduled_at = fields.DateTime(required=False, allow_none=True)
    published_at = fields.DateTime(dump_only=True, allow_none=True)
    status = fields.Str(allow_none=True)
    caption = fields.Str(allow_none=True)
    instagram_media_id = fields.Str(dump_only=True, allow_none=True)
    instagram_permalink = fields.Str(dump_only=True, allow_none=True)
    error_message = fields.Str(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    inventory = fields.Nested(
        "app.schemas.inventory_schema.InventorySchema",
        dump_only=True, allow_none=True,
        exclude=("tags", "purchase", "purchase_item")
    )

    inventories = fields.List(
        fields.Nested(PublicationInventorySummarySchema),
        dump_only=True
    )

    purchases = fields.List(
        fields.Nested("app.schemas.purchase_schema.PurchaseListSchema"),
        dump_only=True
    )

    photo_count = fields.Method("get_photo_count", dump_only=True)
    first_photo_id = fields.Method("get_first_photo_id", dump_only=True)

    def _first_inventory_id(self, obj):
        invs = getattr(obj, "inventories", None)
        if invs:
            return invs[0].id
        return None

    def _all_files(self, obj):
        files = list(getattr(obj, "files", []) or [])
        for inv in (getattr(obj, "inventories", []) or []):
            for f in (getattr(inv, "files", []) or []):
                files.append(f)
        return files

    def get_photo_count(self, obj):
        files = self._all_files(obj)
        return sum(1 for f in files if f.instagram_sort_order is not None)

    def get_first_photo_id(self, obj):
        files = self._all_files(obj)
        ig_files = [f for f in files if f.instagram_sort_order is not None]
        if ig_files:
            ig_files.sort(key=lambda f: f.instagram_sort_order or 0)
            return ig_files[0].id
        return None


class PublicationCreateSchema(Schema):
    title = fields.Str(allow_none=True)
    scheduled_at = fields.DateTime(required=False, allow_none=True)
    status = fields.Str(load_default="pending_review")
    caption = fields.Str(allow_none=True)
    inventory_ids = fields.List(fields.Int(), load_default=[])
    purchase_ids = fields.List(fields.Int(), load_default=[])
