from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.entity_schema import EntitySchema
from app.services.entity_service import EntityService


entity_blueprint = create_crud_blueprint(
    "entities",
    EntityService,
    EntitySchema,
    "entity_id"
)
