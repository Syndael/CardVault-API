from marshmallow import Schema, fields


class WishlistPriceSchema(Schema):
    id = fields.Int(dump_only=True)
    wishlist_item_id = fields.Int(dump_only=True)
    price = fields.Decimal(as_string=True, places=2)
    min_price = fields.Decimal(as_string=True, places=2, allow_none=True)
    max_price = fields.Decimal(as_string=True, places=2, allow_none=True)
    min_price_recorded_at = fields.DateTime(allow_none=True)
    max_price_recorded_at = fields.DateTime(allow_none=True)
    source = fields.Str(allow_none=True)
    recorded_at = fields.DateTime(dump_only=True)


class WishlistItemSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True)
    target_price = fields.Decimal(as_string=True, places=2, allow_none=True)
    language_id = fields.Int(allow_none=True)
    condition_id = fields.Int(allow_none=True)
    w_state = fields.Str(dump_default="buscando")
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    prices = fields.Nested(WishlistPriceSchema, many=True, dump_only=True)
    last_price = fields.Method("get_last_price", dump_only=True)
    min_price = fields.Method("get_min_price", dump_only=True)
    max_price = fields.Method("get_max_price", dump_only=True)
    product_number = fields.Method("get_product_number", dump_only=True)
    collection_code = fields.Method("get_collection_code", dump_only=True)
    product_name = fields.Method("get_product_name", dump_only=True)
    language_name = fields.Method("get_language_name", dump_only=True)
    condition_name = fields.Method("get_condition_name", dump_only=True)
    user_email = fields.Method("get_user_email", dump_only=True)
    last_notified_at = fields.Method("get_last_notified_at", dump_only=True)
    product_image_url = fields.Method("get_product_image_url", dump_only=True)
    type_name = fields.Method("get_type_name", dump_only=True)
    type_short = fields.Method("get_type_short", dump_only=True)
    tracker_url = fields.Method("get_tracker_url", dump_only=True)

    def get_last_price(self, obj):
        prices = getattr(obj, "prices", []) or []
        if not prices:
            return None
        return str(prices[0].price) if prices[0].price is not None else None

    def get_min_price(self, obj):
        prices = getattr(obj, "prices", []) or []
        if not prices:
            return None
        return str(prices[0].min_price) if prices[0].min_price is not None else None

    def get_max_price(self, obj):
        prices = getattr(obj, "prices", []) or []
        if not prices:
            return None
        return str(prices[0].max_price) if prices[0].max_price is not None else None

    def get_product_number(self, obj):
        return obj.product.product_number if obj.product else None

    def get_collection_code(self, obj):
        return obj.product.collection.code if obj.product and obj.product.collection else None

    def get_product_name(self, obj):
        if not obj.product:
            return None
        translations = getattr(obj.product, "translations", [])
        if translations:
            return translations[0].name
        return None

    def get_language_name(self, obj):
        return obj.language.name if obj.language else None

    def get_condition_name(self, obj):
        return obj.condition.name if obj.condition else None

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None

    def get_last_notified_at(self, obj):
        notifications = getattr(obj, "notifications", []) or []
        if not notifications:
            return None
        latest = max(notifications, key=lambda n: n.notified_at)
        return latest.notified_at.isoformat() if latest.notified_at else None

    def get_product_image_url(self, obj):
        if not obj.product:
            return None
        files = getattr(obj.product, "files", []) or []
        if not files:
            return None
        if obj.language_id:
            matched = [f for f in files if f.language_id == obj.language_id]
            if matched:
                return f"/api/product-catalog/files/{matched[0].id}/content"
        return f"/api/product-catalog/files/{files[0].id}/content"

    def get_type_name(self, obj):
        return obj.product.product_type.name if obj.product and obj.product.product_type else None

    def get_type_short(self, obj):
        return obj.product.product_type.short_name if obj.product and obj.product.product_type else None

    def get_tracker_url(self, obj):
        if not obj.product:
            return None
        trackings = getattr(obj.product, "price_tracking", None)
        if not trackings:
            return None
        t = trackings[0]
        url = t.url
        if not url:
            return None
        ps = t.price_source
        lang = getattr(obj, "language", None)
        cond = getattr(obj, "condition", None)
        sep = '&' if '?' in url else '?'
        if ps and ps.language_param and lang and lang.cardmarket_code:
            url += sep + ps.language_param + '=' + str(lang.cardmarket_code)
            sep = '&'
        if ps and ps.condition_param and cond and cond.cardmarket_code:
            url += sep + ps.condition_param + '=' + str(cond.cardmarket_code)
        return url
