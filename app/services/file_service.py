from app.repositories.file_repository import FileRepository
from app.services.crud_service import CrudService


class FileService(CrudService):
    repository = FileRepository
