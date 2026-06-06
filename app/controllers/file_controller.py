import os
from urllib.parse import urlsplit

import requests
from flask import request, jsonify

import app.auth as auth
from app.controllers.crud_controller import create_crud_blueprint
from app.models.setting_model import SettingModel
from app.models.type_model import TypeModel
from app.repositories.file_repository import FileRepository, DEFAULT_IMG_DIR, API_ROOT
from app.schemas.file_schema import FileSchema
from app.services.file_service import FileService
from app.services.inventory_service import InventoryService
from app.services.product_service import ProductService
from app.services.purchase_service import PurchaseService

file_blueprint = create_crud_blueprint(
    "files",
    FileService,
    FileSchema,
    "file_id",
    read_roles=["product_read", "admin"],
    write_roles=["product_write", "admin"]
)


@file_blueprint.route('/download-manual', methods=['OPTIONS'])
@file_blueprint.route('/download-manual/', methods=['OPTIONS'])
def download_manual_options():
    # Respond to CORS preflight explicitly to avoid framework-level content-type issues
    from flask import make_response
    resp = make_response(('', 200))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    return resp


@file_blueprint.route('/download-manual', methods=['POST'])
@file_blueprint.route('/download-manual/', methods=['POST'])
@auth.require_role("product_write", "admin")
def download_manual_file():
    """Download an image URL and store it under the configured img.path

    Expected JSON body: { "product_id": <int>, "file_url": "https://..." }

    The saved path will use the pattern from sync.pokemon.products.img.path.pattern
    (default: {card_type}/{collection_code}) instead of a hardcoded /manual/ subdir.
    Returns the created file record.
    """
    # debug: log request body and headers to help diagnose 400 issues
    try:
        raw = request.get_data(as_text=True)
    except Exception:
        raw = None
    print("download_manual_request_headers:", dict(request.headers))
    print("download_manual_raw_body:", raw)

    try:
        body = request.get_json(silent=True) or {}
    except Exception as e:
        print("download_manual_parse_error:", e)
        body = {}
    product_id = body.get('product_id')
    file_url = body.get('file_url')
    language_id = body.get('language_id')
    try:
        if language_id is not None and language_id != "":
            language_id = int(language_id)
    except Exception:
        language_id = None

    if not product_id or not file_url:
        return jsonify({'message': 'product_id and file_url are required'}), 400

    product = ProductService.get_by_id(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    collection = getattr(product, 'collection', None)
    if not collection or not getattr(collection, 'code', None):
        return jsonify({'message': 'Product collection missing'}), 400

    # determine target directory from settings
    setting = SettingModel.query.filter_by(setting_key="sync.pokemon.products.img.path").first()
    img_dir = setting.setting_value if setting and setting.setting_value else DEFAULT_IMG_DIR
    if os.path.isabs(img_dir):
        target_base = img_dir
    else:
        target_base = os.path.join(API_ROOT, img_dir)

    # read and resolve path pattern (same as sync_pokemon_products.py uses)
    pattern_setting = SettingModel.query.filter_by(setting_key="sync.pokemon.products.img.path.pattern").first()
    pattern = pattern_setting.setting_value if pattern_setting and pattern_setting.setting_value else "{card_type}/{collection_code}"

    collection_code = collection.code
    product_number = product.product_number or ''
    card_type_obj = getattr(collection, 'card_type', None)
    card_type = getattr(card_type_obj, 'short_name', None) or getattr(card_type_obj, 'name', 'unknown')
    is_manual = "1" if getattr(product, 'is_manual', False) else "0"

    parsed = urlsplit(file_url)
    original_name = os.path.basename(parsed.path) or 'image'
    ext = os.path.splitext(original_name)[1] or '.jpg'

    stored_name = f"{collection_code}_{product_number}{ext}"
    sub_dir = _resolve_path_pattern(pattern,
        card_type=card_type,
        is_manual=is_manual,
        collection_code=collection_code
    )
    target_dir = os.path.join(target_base, sub_dir)
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, stored_name)

    # download
    try:
        response = requests.get(file_url, timeout=30)
        response.raise_for_status()
        with open(target_path, "wb") as file:
            file.write(response.content)
    except Exception as e:
        print("Error:", e)
        return jsonify({'message': 'Error downloading file', 'error': str(e)}), 400

    # create DB record
    payload = {
        'product_id': product_id,
        'language_id': language_id,
        'original_name': original_name,
        'stored_name': stored_name,
        'file_path': os.path.join(img_dir, sub_dir, stored_name),
        'file_type_id': None,
        'file_size': os.path.getsize(target_path)
    }

    try:
        created = FileRepository.create(payload)
    except Exception as e:
        return jsonify({'message': 'Error creating file record', 'error': str(e)}), 500

    schema = FileSchema()
    return jsonify(schema.dump(created)), 201


@file_blueprint.route('/by-inventory/<int:inventory_id>', methods=['GET'], strict_slashes=False)
def get_inventory_files(inventory_id):
    from app.models.file_model import FileModel
    files = FileModel.query.filter_by(inventory_id=inventory_id).all()
    schema = FileSchema(many=True)
    return jsonify(schema.dump(files))


@file_blueprint.route('/by-purchase/<int:purchase_id>', methods=['GET'], strict_slashes=False)
def get_purchase_files(purchase_id):
    from app.models.file_model import FileModel
    files = FileModel.query.filter_by(purchase_id=purchase_id).all()
    schema = FileSchema(many=True)
    return jsonify(schema.dump(files))


def _resolve_path_pattern(pattern, **variables):
    for key, value in variables.items():
        pattern = pattern.replace(f'{{{key}}}', str(value))
    return pattern


def _get_image_type_id():
    row = TypeModel.query.filter_by(type="file", name="image").first()
    return row.id if row else None


@file_blueprint.route('/upload-inventory', methods=['POST'])
@auth.require_role("inventory_manage", "admin")
def upload_inventory_file():
    inventory_id = request.form.get('inventory_id')
    uploaded_file = request.files.get('file')

    if not inventory_id or not uploaded_file:
        return jsonify({'message': 'inventory_id and file are required'}), 400

    try:
        inventory_id = int(inventory_id)
    except (ValueError, TypeError):
        return jsonify({'message': 'inventory_id must be an integer'}), 400

    inventory = InventoryService.get_by_id(inventory_id)
    if not inventory:
        return jsonify({'message': 'Inventory not found'}), 404

    product = getattr(inventory, 'product', None)
    collection = getattr(inventory, 'collection', None)
    if not product or not collection or not getattr(collection, 'code', None):
        return jsonify({'message': 'Inventory product or collection missing'}), 400

    card_type = getattr(collection, 'card_type', None)
    card_type_name = getattr(card_type, 'short_name', None) or getattr(card_type, 'name', 'unknown')
    collection_code = collection.code
    product_number = product.product_number or 'unknown'

    path_setting = SettingModel.query.filter_by(setting_key="app.inventory.files.path").first()
    base_dir = path_setting.setting_value if path_setting and path_setting.setting_value else "./../.files/inventory"
    target_base = base_dir if os.path.isabs(base_dir) else os.path.join(API_ROOT, base_dir)

    pattern_setting = SettingModel.query.filter_by(setting_key="app.inventory.files.path.pattern").first()
    pattern = pattern_setting.setting_value if pattern_setting and pattern_setting.setting_value else "{card_type}/{collection_code}/{product_number}/{inventory_id}"

    original_name = os.path.basename(uploaded_file.filename or 'image')
    if not os.path.splitext(original_name)[1]:
        original_name += '.jpg'

    stored_name = original_name
    sub_dir = _resolve_path_pattern(pattern,
        card_type=card_type_name,
        collection_code=collection_code,
        product_number=product_number,
        inventory_id=inventory_id
    )
    target_dir = os.path.join(target_base, sub_dir)
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, stored_name)

    try:
        uploaded_file.save(target_path)
    except Exception as e:
        return jsonify({'message': 'Error saving file', 'error': str(e)}), 500

    payload = {
        'inventory_id': inventory_id,
        'original_name': original_name,
        'stored_name': stored_name,
        'file_path': os.path.join(base_dir, sub_dir, stored_name),
        'file_type_id': _get_image_type_id(),
        'file_size': os.path.getsize(target_path)
    }

    try:
        created = FileRepository.create(payload)
    except Exception as e:
        return jsonify({'message': 'Error creating file record', 'error': str(e)}), 500

    schema = FileSchema()
    return jsonify(schema.dump(created)), 201


@file_blueprint.route('/upload-purchase', methods=['POST'])
@auth.require_role("inventory_manage", "admin")
def upload_purchase_file():
    purchase_id = request.form.get('purchase_id')
    uploaded_file = request.files.get('file')

    if not purchase_id or not uploaded_file:
        return jsonify({'message': 'purchase_id and file are required'}), 400

    try:
        purchase_id = int(purchase_id)
    except (ValueError, TypeError):
        return jsonify({'message': 'purchase_id must be an integer'}), 400

    purchase = PurchaseService.get_by_id(purchase_id)
    if not purchase:
        return jsonify({'message': 'Purchase not found'}), 404

    purchase_date = getattr(purchase, 'purchase_date', None)
    if purchase_date:
        year = str(purchase_date.year)
        month = f"{purchase_date.month:02d}"
    else:
        year = "unknown"
        month = "unknown"

    path_setting = SettingModel.query.filter_by(setting_key="app.purchase.files.path").first()
    base_dir = path_setting.setting_value if path_setting and path_setting.setting_value else "./../.files/purchases"
    target_base = base_dir if os.path.isabs(base_dir) else os.path.join(API_ROOT, base_dir)

    pattern_setting = SettingModel.query.filter_by(setting_key="app.purchase.files.path.pattern").first()
    pattern = pattern_setting.setting_value if pattern_setting and pattern_setting.setting_value else "{year}/{month}/{purchase_id}"

    original_name = os.path.basename(uploaded_file.filename or 'image')
    if not os.path.splitext(original_name)[1]:
        original_name += '.jpg'

    stored_name = original_name
    sub_dir = _resolve_path_pattern(pattern,
        year=year,
        month=month,
        purchase_id=purchase_id
    )
    target_dir = os.path.join(target_base, sub_dir)
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, stored_name)

    try:
        uploaded_file.save(target_path)
    except Exception as e:
        return jsonify({'message': 'Error saving file', 'error': str(e)}), 500

    file_type = request.form.get('file_type', 'image')
    type_row = TypeModel.query.filter_by(type="file", name=file_type).first()
    file_type_id = type_row.id if type_row else _get_image_type_id()

    payload = {
        'purchase_id': purchase_id,
        'original_name': original_name,
        'stored_name': stored_name,
        'file_path': os.path.join(base_dir, sub_dir, stored_name),
        'file_type_id': file_type_id,
        'file_size': os.path.getsize(target_path)
    }

    try:
        created = FileRepository.create(payload)
    except Exception as e:
        return jsonify({'message': 'Error creating file record', 'error': str(e)}), 500

    schema = FileSchema()
    return jsonify(schema.dump(created)), 201
