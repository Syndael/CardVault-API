from datetime import datetime

from app.repositories.publication_schedule_repository import PublicationScheduleRepository
from app.services.crud_service import CrudService


def _parse_scheduled_at(data):
    if "scheduled_at" in data and isinstance(data["scheduled_at"], str):
        try:
            data["scheduled_at"] = datetime.fromisoformat(data["scheduled_at"].replace("Z", "+00:00"))
        except ValueError:
            pass


class PublicationScheduleService(CrudService):
    repository = PublicationScheduleRepository

    @classmethod
    def create(cls, data):
        _parse_scheduled_at(data)
        return super().create(data)

    @classmethod
    def update(cls, entity_id, data):
        _parse_scheduled_at(data)
        return super().update(entity_id, data)

    @classmethod
    def get_pending_publish(cls):
        return cls.repository.get_pending_publish()

    @classmethod
    def get_by_status(cls, status_name):
        return cls.repository.get_by_status(status_name)

    @classmethod
    def generate_caption(cls, inventory):
        product = inventory.get("product") or {}
        collection = inventory.get("collection") or {}
        product_name = product.get("name") or product.get("product_number", "")
        product_number = product.get("product_number", "")
        collection_code = collection.get("code", "")
        card_type = collection.get("card_type") or {}

        lines = []
        header = f"{collection_code} {product_number}"
        if product_name:
            header += f" - {product_name}"
        lines.append(header.strip())

        if product_name and product_name != product_number:
            lines.append("")

        tags = ["#CardVault", "#TCG", "#Coleccionismo"]

        if card_type and card_type.get("name"):
            type_tag = card_type["name"].replace(" ", "")
            tags.append(f"#{type_tag}")

        if collection_code:
            tags.append(f"#{collection_code}")

        lang = inventory.get("language") or {}
        if lang and lang.get("name"):
            if lang["name"].lower() == "español":
                tags.append("#Español")

        lines.append(" ".join(tags))
        return "\n".join(lines)