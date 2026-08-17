from datetime import datetime

from flask import jsonify, request

import app.auth as auth
from app.controllers.crud_controller import _roles_guard, create_crud_blueprint
from app.schemas.publication_schedule_schema import PublicationScheduleSchema, PublicationCreateSchema
from app.services.publication_schedule_service import PublicationScheduleService

publication_schedule_blueprint = create_crud_blueprint(
    "publication_schedule",
    PublicationScheduleService,
    PublicationScheduleSchema,
    "publication_id",
    read_roles=["inventory_manage", "admin"],
    write_roles=["inventory_manage", "admin"],
)

schema = PublicationScheduleSchema()
create_schema = PublicationCreateSchema()


def _item_day(item):
    dt = item.published_at or item.scheduled_at
    return dt.date().isoformat() if dt else None


def _item_summary(item):
    inv = item.inventories[0] if item.inventories else None
    product = inv.product if inv else None
    collection = inv.collection if inv else None
    return {
        "id": item.id,
        "title": item.title,
        "status": item.status,
        "scheduled_at": item.scheduled_at.isoformat() if item.scheduled_at else None,
        "published_at": item.published_at.isoformat() if item.published_at else None,
        "collection_code": collection.code if collection else None,
        "product_number": product.product_number if product else None,
    }


@publication_schedule_blueprint.route("/calendar", methods=["GET"], strict_slashes=False)
def calendar():
    if _roles_guard(["inventory_manage", "admin"], None, "GET"):
        return jsonify({"message": "Forbidden"}), 403
    try:
        start = datetime.fromisoformat(request.args.get("start", ""))
        end = datetime.fromisoformat(request.args.get("end", ""))
    except (TypeError, ValueError):
        return jsonify({"message": "start and end params required (ISO)"}), 400

    items = PublicationScheduleService.get_in_date_range(start, end)

    days = {}
    for item in items:
        day = _item_day(item)
        if not day:
            continue
        bucket = days.setdefault(day, {"scheduled": 0, "published": 0, "items": []})
        summary = _item_summary(item)
        bucket["items"].append(summary)
        if item.status == "published":
            bucket["published"] += 1
        else:
            bucket["scheduled"] += 1

    return jsonify({"days": days})


@publication_schedule_blueprint.route("/pending-publish", methods=["GET"], strict_slashes=False)
def get_pending_publish():
    if _roles_guard(["inventory_manage", "admin"], None, "GET"):
        return jsonify({"message": "Forbidden"}), 403
    pending = PublicationScheduleService.get_pending_publish()
    return jsonify(schema.dump(pending, many=True))


@publication_schedule_blueprint.route("/by-status/<status_name>", methods=["GET"], strict_slashes=False)
def get_by_status(status_name):
    if _roles_guard(["inventory_manage", "admin"], None, "GET"):
        return jsonify({"message": "Forbidden"}), 403
    items = PublicationScheduleService.get_by_status(status_name)
    return jsonify(schema.dump(items, many=True))


@publication_schedule_blueprint.route("/<int:publication_id>/approve", methods=["POST"], strict_slashes=False)
def approve_publication(publication_id):
    if _roles_guard(None, ["inventory_manage", "admin"], "POST"):
        return jsonify({"message": "Forbidden"}), 403
    entity = PublicationScheduleService.get_by_id(publication_id)
    if not entity:
        return jsonify({"message": "Not found"}), 404
    if entity.status != "pending_review":
        return jsonify({"message": f"Cannot approve publication with status '{entity.status}'"}), 400
    body = request.get_json() or {}
    scheduled_str = body.get("scheduled_at")
    if not scheduled_str:
        return jsonify({"message": "scheduled_at is required"}), 400
    try:
        entity.scheduled_at = datetime.fromisoformat(scheduled_str)
    except ValueError:
        return jsonify({"message": "Invalid scheduled_at format"}), 400
    entity.status = "pending_publish"
    from app.database.session import db
    db.session.commit()
    return jsonify(schema.dump(entity))


@publication_schedule_blueprint.route("/<int:publication_id>/cancel", methods=["POST"], strict_slashes=False)
def cancel_publication(publication_id):
    if _roles_guard(None, ["inventory_manage", "admin"], "POST"):
        return jsonify({"message": "Forbidden"}), 403
    entity = PublicationScheduleService.get_by_id(publication_id)
    if not entity:
        return jsonify({"message": "Not found"}), 404
    if entity.status not in ("pending_review", "pending_publish"):
        return jsonify({"message": f"Cannot cancel publication with status '{entity.status}'"}), 400
    entity.status = "cancelled"
    from app.database.session import db
    db.session.commit()
    return jsonify(schema.dump(entity))


@publication_schedule_blueprint.route("/create-from-inventory", methods=["POST"], strict_slashes=False)
def create_from_inventory():
    if _roles_guard(None, ["inventory_manage", "admin"], "POST"):
        return jsonify({"message": "Forbidden"}), 403
    body = request.get_json() or {}
    inv_id = body.get("inventory_id")
    if not inv_id:
        return jsonify({"message": "inventory_id is required"}), 400

    from app.services.inventory_service import InventoryService
    inv = InventoryService.get_by_id(inv_id)
    if not inv:
        return jsonify({"message": "Inventory not found"}), 404

    inv_dict = {
        "product": {
            "name": getattr(getattr(inv, "product", None), "name", None),
            "product_number": getattr(getattr(inv, "product", None), "product_number", None)
        },
        "collection": {
            "code": getattr(getattr(inv, "collection", None), "code", None),
            "name": getattr(getattr(inv, "collection", None), "name", None),
            "card_type": {
                "name": getattr(getattr(getattr(inv, "collection", None), "card_type", None), "name", None)
            }
        },
        "language": {
            "name": getattr(getattr(inv, "language", None), "name", None)
        },
    }

    caption = PublicationScheduleService.generate_caption(inv_dict)
    entity = PublicationScheduleService.repository.create({
        "status": "pending_review",
        "caption": caption,
        "inventory_ids": [inv_id],
    })
    return jsonify(schema.dump(entity)), 201


@publication_schedule_blueprint.route("/<int:publication_id>/inventories", methods=["POST"], strict_slashes=False)
def add_inventory(publication_id):
    if _roles_guard(None, ["inventory_manage", "admin"], "POST"):
        return jsonify({"message": "Forbidden"}), 403
    entity = PublicationScheduleService.get_by_id(publication_id)
    if not entity:
        return jsonify({"message": "Not found"}), 404
    body = request.get_json() or {}
    inv_id = body.get("inventory_id")
    if not inv_id:
        return jsonify({"message": "inventory_id is required"}), 400
    from app.database.session import db
    from app.models.publication_inventory_model import PublicationInventoryModel
    existing = PublicationInventoryModel.query.filter_by(
        publication_id=publication_id, inventory_id=int(inv_id)
    ).first()
    if existing:
        return jsonify({"message": "Already associated"}), 200
    db.session.add(PublicationInventoryModel(publication_id=publication_id, inventory_id=int(inv_id)))
    db.session.commit()
    return jsonify(schema.dump(PublicationScheduleService.get_by_id(publication_id)))


@publication_schedule_blueprint.route("/<int:publication_id>/inventories/<int:inv_id>", methods=["DELETE"], strict_slashes=False)
def remove_inventory(publication_id, inv_id):
    if _roles_guard(None, ["inventory_manage", "admin"], "DELETE"):
        return jsonify({"message": "Forbidden"}), 403
    from app.models.publication_inventory_model import PublicationInventoryModel
    link = PublicationInventoryModel.query.filter_by(
        publication_id=publication_id, inventory_id=inv_id
    ).first()
    if not link:
        return jsonify({"message": "Not found"}), 404
    from app.database.session import db
    db.session.delete(link)
    db.session.commit()
    return jsonify({"deleted": True})


@publication_schedule_blueprint.route("/<int:publication_id>/purchases", methods=["POST"], strict_slashes=False)
def add_purchase(publication_id):
    if _roles_guard(None, ["inventory_manage", "admin"], "POST"):
        return jsonify({"message": "Forbidden"}), 403
    entity = PublicationScheduleService.get_by_id(publication_id)
    if not entity:
        return jsonify({"message": "Not found"}), 404
    body = request.get_json() or {}
    pur_id = body.get("purchase_id")
    if not pur_id:
        return jsonify({"message": "purchase_id is required"}), 400
    from app.database.session import db
    from app.models.publication_purchase_model import PublicationPurchaseModel
    existing = PublicationPurchaseModel.query.filter_by(
        publication_id=publication_id, purchase_id=int(pur_id)
    ).first()
    if existing:
        return jsonify({"message": "Already associated"}), 200
    db.session.add(PublicationPurchaseModel(publication_id=publication_id, purchase_id=int(pur_id)))
    db.session.commit()
    return jsonify(schema.dump(PublicationScheduleService.get_by_id(publication_id)))


@publication_schedule_blueprint.route("/<int:publication_id>/purchases/<int:pur_id>", methods=["DELETE"], strict_slashes=False)
def remove_purchase(publication_id, pur_id):
    if _roles_guard(None, ["inventory_manage", "admin"], "DELETE"):
        return jsonify({"message": "Forbidden"}), 403
    from app.models.publication_purchase_model import PublicationPurchaseModel
    link = PublicationPurchaseModel.query.filter_by(
        publication_id=publication_id, purchase_id=pur_id
    ).first()
    if not link:
        return jsonify({"message": "Not found"}), 404
    from app.database.session import db
    db.session.delete(link)
    db.session.commit()
    return jsonify({"deleted": True})


@publication_schedule_blueprint.route("/<int:publication_id>/files", methods=["POST"], strict_slashes=False)
def upload_publication_file(publication_id):
    if _roles_guard(None, ["inventory_manage", "admin"], "POST"):
        return jsonify({"message": "Forbidden"}), 403
    entity = PublicationScheduleService.get_by_id(publication_id)
    if not entity:
        return jsonify({"message": "Not found"}), 404

    import os
    import uuid
    from app.database.session import db
    from app.models.file_model import FileModel
    from app.models.type_model import TypeModel
    from app.models.setting_model import SettingModel
    from app.repositories.file_repository import API_ROOT

    path_setting = SettingModel.query.filter_by(setting_key="app.publications.files.path").first()
    base_dir = path_setting.setting_value if path_setting and path_setting.setting_value else "./../.files/publications"
    target_base = base_dir if os.path.isabs(base_dir) else os.path.join(API_ROOT, base_dir)

    pattern_setting = SettingModel.query.filter_by(setting_key="app.publications.files.path.pattern").first()
    pattern = pattern_setting.setting_value if pattern_setting and pattern_setting.setting_value else "{year}/{month}/{publication_id}"
    now = datetime.now()
    sub_dir = pattern.replace("{year}", str(now.year)).replace("{month}", f"{now.month:02d}").replace("{publication_id}", str(publication_id))

    target_dir = os.path.join(target_base, sub_dir)
    os.makedirs(target_dir, exist_ok=True)

    added = []
    files = request.files.getlist("files")
    for f in files:
        if not f.filename:
            continue
        ext = os.path.splitext(f.filename)[1] or ".jpg"
        stored_name = f"{uuid.uuid4().hex}{ext}"
        full_path = os.path.join(target_dir, stored_name)
        f.save(full_path)

        file_size = os.path.getsize(full_path)

        mime = f.mimetype or ""
        file_type_name = "image" if mime.startswith("image/") else\
                         "video" if mime.startswith("video/") else "document"
        ft = TypeModel.query.filter_by(type="file_type", name=file_type_name).first()

        max_sort = db.session.query(db.func.max(FileModel.sort_order)).filter(
            FileModel.publication_id == publication_id
        ).scalar() or 0

        file_obj = FileModel(
            publication_id=publication_id,
            original_name=f.filename,
            stored_name=stored_name,
            file_path=os.path.join(base_dir, sub_dir, stored_name),
            file_type_id=ft.id if ft else None,
            file_size=file_size,
            sort_order=max_sort + 1,
        )
        db.session.add(file_obj)
        db.session.flush()
        added.append({"id": file_obj.id, "original_name": file_obj.original_name, "file_type": file_type_name})

    db.session.commit()
    return jsonify({"files": added}), 201


@publication_schedule_blueprint.route("/<int:publication_id>/files/reorder", methods=["PATCH"], strict_slashes=False)
def reorder_publication_files(publication_id):
    if _roles_guard(None, ["inventory_manage", "admin"], "PATCH"):
        return jsonify({"message": "Forbidden"}), 403
    body = request.get_json() or {}
    file_ids = body.get("file_ids") or []
    from app.database.session import db
    from app.models.file_model import FileModel
    from app.models.publication_inventory_model import PublicationInventoryModel
    from app.models.publication_purchase_model import PublicationPurchaseModel

    inv_links = PublicationInventoryModel.query.filter_by(publication_id=publication_id).all()
    pur_links = PublicationPurchaseModel.query.filter_by(publication_id=publication_id).all()
    inv_ids = [l.inventory_id for l in inv_links]
    pur_ids = [l.purchase_id for l in pur_links]

    for idx, fid in enumerate(file_ids):
        f = FileModel.query.get(int(fid))
        if not f:
            continue
        if f.publication_id == publication_id or f.inventory_id in inv_ids or f.purchase_id in pur_ids:
            f.instagram_sort_order = idx + 1

    for key, value in body.items():
        if key.startswith("ig_order_"):
            fid = int(key.replace("ig_order_", ""))
            f = FileModel.query.get(fid)
            if not f:
                continue
            if f.publication_id == publication_id or f.inventory_id in inv_ids or f.purchase_id in pur_ids:
                f.instagram_sort_order = int(value) if value is not None else None

    db.session.commit()
    return jsonify(schema.dump(PublicationScheduleService.get_by_id(publication_id)))
