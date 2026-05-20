from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.product_condition_schema import ProductConditionSchema
from app.services.product_condition_service import ProductConditionService


product_condition_blueprint = create_crud_blueprint(
    "product_conditions",
    ProductConditionService,
    ProductConditionSchema,
    "condition_id"
)
