from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.product_translation_schema import ProductTranslationSchema
from app.services.product_translation_service import ProductTranslationService


product_translation_blueprint = create_crud_blueprint(
    "product_translations",
    ProductTranslationService,
    ProductTranslationSchema,
    "translation_id",
    read_roles=["product_read", "admin"],
    write_roles=["product_write", "admin"]
)
