from flask import Blueprint, request, jsonify, g

import app.auth as auth
from app.services.wishlist_item_service import WishlistItemService
from app.schemas.wishlist_schema import WishlistItemSchema, WishlistPriceSchema
from app.utils.pagination import get_pagination_params, paginated_response

wishlist_blueprint = Blueprint("wishlist", __name__)


def _get_current_user_id():
    user = getattr(g, "current_user", None)
    if not user:
        return None
    return user.id


def _owns_item(item):
    uid = _get_current_user_id()
    if not uid:
        return False
    return item.user_id == uid


def _can_manage_wishlist():
    user = getattr(g, "current_user", None)
    if not user:
        return False
    return any(ur.role.name in ("admin", "scheduled_task_read") for ur in getattr(user, "user_roles", []))


@wishlist_blueprint.route("", methods=["GET"], strict_slashes=False)
def list_items():
    uid = _get_current_user_id()
    if not uid and not auth.has_any_role("admin") and not _can_manage_wishlist():
        return jsonify({"message": "Unauthorized"}), 401

    page, per_page = get_pagination_params()
    can_see_all = auth.has_any_role("admin") or _can_manage_wishlist()

    if can_see_all and request.args.get("user_id"):
        data = WishlistItemService.get_paginated_by_user(int(request.args["user_id"]), page, per_page)
    elif can_see_all:
        data = WishlistItemService.get_paginated(page, per_page)
    else:
        data = WishlistItemService.get_paginated_by_user(uid, page, per_page)

    schema = WishlistItemSchema(many=True)
    return jsonify(paginated_response(data, schema))


@wishlist_blueprint.route("/<int:item_id>", methods=["GET"], strict_slashes=False)
def get_item(item_id):
    item = WishlistItemService.get_by_id(item_id)
    if not item:
        return jsonify({"message": "Not found"}), 404
    if not _owns_item(item) and not auth.has_any_role("admin") and not _can_manage_wishlist():
        return jsonify({"message": "Forbidden"}), 403

    schema = WishlistItemSchema()
    return jsonify(schema.dump(item))


@wishlist_blueprint.route("", methods=["POST"], strict_slashes=False)
def create_item():
    uid = _get_current_user_id()
    if not uid:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    data["user_id"] = uid

    item = WishlistItemService.create(data)
    schema = WishlistItemSchema()
    return jsonify(schema.dump(item)), 201


@wishlist_blueprint.route("/<int:item_id>", methods=["PATCH"], strict_slashes=False)
def update_item(item_id):
    item = WishlistItemService.get_by_id(item_id)
    if not item:
        return jsonify({"message": "Not found"}), 404
    if not _owns_item(item) and not auth.has_any_role("admin") and not _can_manage_wishlist():
        return jsonify({"message": "Forbidden"}), 403

    data = request.get_json(silent=True) or {}
    item = WishlistItemService.update(item_id, data)
    schema = WishlistItemSchema()
    return jsonify(schema.dump(item))


@wishlist_blueprint.route("/<int:item_id>", methods=["DELETE"], strict_slashes=False)
def delete_item(item_id):
    item = WishlistItemService.get_by_id(item_id)
    if not item:
        return jsonify({"message": "Not found"}), 404
    if not _owns_item(item) and not auth.has_any_role("admin") and not _can_manage_wishlist():
        return jsonify({"message": "Forbidden"}), 403

    WishlistItemService.delete(item_id)
    return jsonify({"success": True})


@wishlist_blueprint.route("/<int:item_id>/prices", methods=["GET"], strict_slashes=False)
def list_prices(item_id):
    item = WishlistItemService.get_by_id(item_id)
    if not item:
        return jsonify({"message": "Not found"}), 404
    if not _owns_item(item) and not auth.has_any_role("admin") and not _can_manage_wishlist():
        return jsonify({"message": "Forbidden"}), 403

    limit = request.args.get("limit", 20, type=int)
    prices = WishlistItemService.get_prices(item_id, limit=limit)
    schema = WishlistPriceSchema(many=True)
    return jsonify(schema.dump(prices))


@wishlist_blueprint.route("/<int:item_id>/prices", methods=["POST"], strict_slashes=False)
def record_price(item_id):
    item = WishlistItemService.get_by_id(item_id)
    if not item:
        return jsonify({"message": "Not found"}), 404
    if not _owns_item(item) and not auth.has_any_role("admin") and not _can_manage_wishlist():
        return jsonify({"message": "Forbidden"}), 403

    data = request.get_json(silent=True) or {}
    price = data.get("price")
    if price is None:
        return jsonify({"message": "price is required"}), 400

    record = WishlistItemService.record_price(
        item_id,
        price=price,
        source=data.get("source"),
    )
    schema = WishlistPriceSchema()
    return jsonify(schema.dump(record)), 201
