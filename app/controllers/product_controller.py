from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.product_schema import ProductSchema
from app.services.product_service import ProductService


product_blueprint = create_crud_blueprint(
    "products",
    ProductService,
    ProductSchema,
    "product_id",
    read_roles=["product_read", "admin"],
    write_roles=["product_write", "admin"]
)
