from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.tag_schema import TagSchema
from app.services.tag_service import TagService


tag_blueprint = create_crud_blueprint(
    "tags",
    TagService,
    TagSchema,
    "tag_id"
)
