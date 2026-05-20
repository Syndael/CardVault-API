from app.models.entity_model import EntityModel
from app.repositories.crud_repository import CrudRepository


class EntityRepository(CrudRepository):
    model = EntityModel
    order_by = (EntityModel.id,)
    create_fields = (
        "name",
        "entity_type",
        "parent_id"
    )
    update_fields = create_fields
