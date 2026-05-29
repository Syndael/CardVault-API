from flask import jsonify

from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.inventory_url_schema import InventoryUrlSchema
from app.services.inventory_url_service import InventoryUrlService


inventory_url_blueprint = create_crud_blueprint(
    "inventory_urls",
    InventoryUrlService,
    InventoryUrlSchema,
    "inventory_url_id",
    read_roles=["inventory_manage", "admin"],
    write_roles=["inventory_manage", "admin"]
)


@inventory_url_blueprint.route(
    "/by-inventory/<int:inventory_id>",
    methods=["GET"],
    strict_slashes=False
)
def get_by_inventory(inventory_id):
    from app.models.inventory_url_model import InventoryUrlModel
    urls = InventoryUrlModel.query.filter_by(inventory_id=inventory_id).all()
    schema = InventoryUrlSchema(many=True)
    return jsonify(schema.dump(urls))
