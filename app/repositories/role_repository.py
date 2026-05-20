from app.models.role_model import RoleModel
from app.repositories.crud_repository import CrudRepository


class RoleRepository(CrudRepository):
    model = RoleModel
    order_by = (RoleModel.name,)
    create_fields = (
        "name",
        "description"
    )
    update_fields = create_fields
