from app.models.tag_model import TagModel
from app.repositories.crud_repository import CrudRepository


class TagRepository(CrudRepository):
    model = TagModel
    order_by = (TagModel.name,)
    create_fields = ("name", "color")
    update_fields = create_fields
