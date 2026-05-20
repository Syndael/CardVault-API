import os
from urllib.parse import urlsplit

import requests
from flask import request, jsonify

import app.auth as auth
from app.controllers.crud_controller import create_crud_blueprint
from app.models.setting_model import SettingModel
from app.repositories.file_repository import FileRepository, DEFAULT_IMG_DIR, API_ROOT
from app.schemas.file_schema import FileSchema
from app.services.file_service import FileService
from app.services.product_service import ProductService

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

    The saved path will be: <img_dir>/manual/{collection_code}/{collection_code}_{product_number}.{ext}
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

    collection_code = collection.code
    product_number = product.product_number or ''

    parsed = urlsplit(file_url)
    original_name = os.path.basename(parsed.path) or 'image'
    ext = os.path.splitext(original_name)[1] or '.jpg'

    stored_name = f"{collection_code}_{product_number}{ext}"
    manual_dir = os.path.join(target_base, 'manual', collection_code)
    os.makedirs(manual_dir, exist_ok=True)
    target_path = os.path.join(manual_dir, stored_name)

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
        'file_path': os.path.join(img_dir, 'manual', collection_code, stored_name),
        'file_type_id': None,
        'file_size': os.path.getsize(target_path)
    }

    try:
        created = FileRepository.create(payload)
    except Exception as e:
        return jsonify({'message': 'Error creating file record', 'error': str(e)}), 500

    schema = FileSchema()
    return jsonify(schema.dump(created)), 201
