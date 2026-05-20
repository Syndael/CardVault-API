from app.repositories.tag_repository import TagRepository
from app.services.crud_service import CrudService


class TagService(CrudService):
    repository = TagRepository
