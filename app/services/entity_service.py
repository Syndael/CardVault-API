from app.repositories.entity_repository import EntityRepository
from app.services.crud_service import CrudService


class EntityService(CrudService):
    repository = EntityRepository
