from flask import Flask, g, jsonify, request
from werkzeug.exceptions import BadRequest, NotFound

from app.config.config import Config
from app.models.user_model import UserModel
from app.models.user_role_model import UserRoleModel
from app.models.role_model import RoleModel
from app.controllers.collection_controller import collection_blueprint
from app.controllers.collection_tracking_controller import collection_tracking_blueprint
from app.controllers.collection_translation_controller import collection_translation_blueprint
from app.controllers.collection_alternative_code_controller import collection_alternative_code_blueprint
from app.controllers.entity_controller import entity_blueprint
from app.controllers.file_controller import file_blueprint
from app.controllers.inventory_controller import inventory_blueprint
from app.controllers.inventory_price_history_controller import inventory_price_history_blueprint
from app.controllers.inventory_price_history_archive_controller import inventory_price_history_archive_blueprint
from app.controllers.inventory_url_controller import inventory_url_blueprint
from app.controllers.inventory_tag_controller import inventory_tag_blueprint
from app.controllers.language_controller import language_blueprint
from app.controllers.notification_controller import notification_blueprint
from app.controllers.price_source_controller import price_source_blueprint
from app.controllers.proxy_controller import proxy_blueprint
from app.controllers.product_catalog_controller import product_catalog_blueprint
from app.controllers.product_condition_controller import product_condition_blueprint
from app.controllers.product_controller import product_blueprint
from app.controllers.product_price_tracking_controller import product_price_tracking_blueprint
from app.controllers.product_translation_controller import product_translation_blueprint
from app.controllers.purchase_controller import purchase_blueprint
from app.controllers.publication_schedule_controller import publication_schedule_blueprint
from app.controllers.purchase_item_controller import purchase_item_blueprint
from app.controllers.scheduled_task_controller import scheduled_task_blueprint
from app.controllers.setting_controller import setting_blueprint
from app.controllers.statistics_controller import statistics_blueprint
from app.controllers.tag_controller import tag_blueprint
from app.controllers.task_execution_controller import task_execution_blueprint
from app.controllers.type_controller import type_blueprint
from app.controllers.wishlist_controller import wishlist_blueprint
from app.controllers.ai_controller import ai_blueprint
from app.database.session import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.json.ensure_ascii = False

    @app.errorhandler(BadRequest)
    def bad_request(e):
        return jsonify({"error": str(e.description)}), 400

    @app.errorhandler(NotFound)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(400)
    def bad_request_generic(e):
        return jsonify({"error": str(e.description or "Bad request")}), 400

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            resp = app.make_default_options_response()
            resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PATCH,DELETE,OPTIONS"
            resp.headers["X-Content-Type-Options"] = "nosniff"
            return resp

    @app.after_request
    def add_cors_headers(response):
        allowed_origins = app.config["CORS_ALLOWED_ORIGINS"]
        request_origin = request.headers.get("Origin")

        if "*" in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"
        elif request_origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = request_origin
            response.headers["Vary"] = "Origin"

        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization"
        )
        response.headers["Access-Control-Allow-Methods"] = (
            "GET,POST,PATCH,DELETE,OPTIONS"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    db.init_app(app)

    from app.controllers.auth_controller import auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/api/auth")

    import app.auth as _auth

    def register_protected(blueprint, url_prefix):
        def _before_request():
            from flask import jsonify
            if request.method == "OPTIONS":
                return
            if request.path == "/api/product-catalog/suggest-urls":
                return
            user = _auth.get_user_from_request()
            if not user:
                return jsonify({"message": "Unauthorized"}), 401
            g.current_user = user

        blueprint.before_request(_before_request)
        app.register_blueprint(blueprint, url_prefix=url_prefix)

    register_protected(type_blueprint, "/api/types")
    register_protected(collection_translation_blueprint, "/api/collection-translations")
    register_protected(collection_alternative_code_blueprint, "/api/collection-alternative-codes")
    register_protected(language_blueprint, "/api/languages")
    register_protected(collection_blueprint, "/api/collections")
    register_protected(collection_tracking_blueprint, "/api/collection-tracking")
    register_protected(proxy_blueprint, "/api/proxy")
    register_protected(product_blueprint, "/api/products")
    register_protected(product_catalog_blueprint, "/api/product-catalog")
    register_protected(product_translation_blueprint, "/api/product-translations")
    register_protected(entity_blueprint, "/api/entities")
    register_protected(purchase_blueprint, "/api/purchases")
    register_protected(purchase_item_blueprint, "/api/purchase-items")
    register_protected(product_condition_blueprint, "/api/product-conditions")
    register_protected(inventory_blueprint, "/api/inventory")
    register_protected(inventory_tag_blueprint, "/api/inventory")
    register_protected(file_blueprint, "/api/files")
    register_protected(publication_schedule_blueprint, "/api/publications")
    register_protected(price_source_blueprint, "/api/price-sources")
    register_protected(product_price_tracking_blueprint, "/api/product-price-tracking")
    register_protected(inventory_price_history_blueprint, "/api/inventory-price-history")
    register_protected(inventory_price_history_archive_blueprint, "/api/inventory-price-history-archive")
    register_protected(inventory_url_blueprint, "/api/inventory-urls")
    register_protected(tag_blueprint, "/api/tags")
    register_protected(scheduled_task_blueprint, "/api/scheduled-tasks")
    register_protected(setting_blueprint, "/api/settings")
    register_protected(statistics_blueprint, "/api/statistics")
    register_protected(task_execution_blueprint, "/api/task-executions")
    register_protected(wishlist_blueprint, "/api/wishlist-items")
    register_protected(notification_blueprint, "/api/notifications")
    register_protected(ai_blueprint, "/api/ai")

    return app
