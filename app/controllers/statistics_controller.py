from flask import Blueprint, jsonify, request

import app.auth as auth
from app.services.statistics_service import (
    avg_monthly_spending,
    best_investment_entities,
    collections_top,
    condition_distribution,
    inventory_value_by_type,
    inventory_value_detail,
    language_distribution,
    purchases_by_entity,
    purchases_by_month,
    summary,
    top_profit_items,
    top_valuable_items,
    untracked_items,
)

statistics_blueprint = Blueprint("statistics", __name__)


def admin_or_inventory():
    return auth.has_any_role("inventory_manage", "admin")


@statistics_blueprint.route("/", methods=["GET"], strict_slashes=False)
def stats_root():
    return jsonify({"endpoints": [
        "/api/statistics/summary",
        "/api/statistics/inventory-value-by-type",
        "/api/statistics/inventory-value-detail",
        "/api/statistics/collections-top",
        "/api/statistics/purchases-by-entity",
        "/api/statistics/purchases-by-month",
        "/api/statistics/language-distribution",
        "/api/statistics/condition-distribution",
        "/api/statistics/top-valuable-items",
        "/api/statistics/top-profit-items",
        "/api/statistics/untracked-items",
        "/api/statistics/avg-monthly-spending",
        "/api/statistics/best-investment-entities",
    ]})


@statistics_blueprint.route("/summary", methods=["GET"], strict_slashes=False)
def summary_ep():
    if not admin_or_inventory():
        return jsonify({"message": "Forbidden"}), 403
    return jsonify(summary())


@statistics_blueprint.route("/inventory-value-by-type", methods=["GET"], strict_slashes=False)
def inventory_value_by_type_ep():
    if not admin_or_inventory():
        return jsonify({"message": "Forbidden"}), 403
    return jsonify(inventory_value_by_type())


@statistics_blueprint.route("/inventory-value-detail", methods=["GET"], strict_slashes=False)
def inventory_value_detail_ep():
    if not admin_or_inventory():
        return jsonify({"message": "Forbidden"}), 403
    return jsonify(inventory_value_detail())


@statistics_blueprint.route("/collections-top", methods=["GET"], strict_slashes=False)
def collections_top_ep():
    if not admin_or_inventory():
        return jsonify({"message": "Forbidden"}), 403
    return jsonify(collections_top())


@statistics_blueprint.route("/purchases-by-entity", methods=["GET"], strict_slashes=False)
def purchases_by_entity_ep():
    if not admin_or_inventory():
        return jsonify({"message": "Forbidden"}), 403
    return jsonify(purchases_by_entity())


@statistics_blueprint.route("/purchases-by-month", methods=["GET"], strict_slashes=False)
def purchases_by_month_ep():
    if not admin_or_inventory():
        return jsonify({"message": "Forbidden"}), 403
    return jsonify(purchases_by_month())


@statistics_blueprint.route("/language-distribution", methods=["GET"], strict_slashes=False)
def language_distribution_ep():
    if not admin_or_inventory():
        return jsonify({"message": "Forbidden"}), 403
    return jsonify(language_distribution())


@statistics_blueprint.route("/condition-distribution", methods=["GET"], strict_slashes=False)
def condition_distribution_ep():
    if not admin_or_inventory():
        return jsonify({"message": "Forbidden"}), 403
    return jsonify(condition_distribution())


@statistics_blueprint.route("/top-valuable-items", methods=["GET"], strict_slashes=False)
def top_valuable_items_ep():
    if not admin_or_inventory():
        return jsonify({"message": "Forbidden"}), 403
    limit = request.args.get("limit", 10, type=int)
    return jsonify(top_valuable_items(limit=limit))


@statistics_blueprint.route("/top-profit-items", methods=["GET"], strict_slashes=False)
def top_profit_items_ep():
    if not admin_or_inventory():
        return jsonify({"message": "Forbidden"}), 403
    limit = request.args.get("limit", 10, type=int)
    return jsonify(top_profit_items(limit=limit))


@statistics_blueprint.route("/untracked-items", methods=["GET"], strict_slashes=False)
def untracked_items_ep():
    if not admin_or_inventory():
        return jsonify({"message": "Forbidden"}), 403
    return jsonify(untracked_items())


@statistics_blueprint.route("/avg-monthly-spending", methods=["GET"], strict_slashes=False)
def avg_monthly_spending_ep():
    if not admin_or_inventory():
        return jsonify({"message": "Forbidden"}), 403
    return jsonify(avg_monthly_spending())


@statistics_blueprint.route("/best-investment-entities", methods=["GET"], strict_slashes=False)
def best_investment_entities_ep():
    if not admin_or_inventory():
        return jsonify({"message": "Forbidden"}), 403
    limit = request.args.get("limit", 10, type=int)
    return jsonify(best_investment_entities(limit=limit))
