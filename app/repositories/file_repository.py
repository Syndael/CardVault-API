import os
import urllib.request
from urllib.parse import urlsplit

from app.models.file_model import FileModel
from app.models.setting_model import SettingModel
from app.repositories.crud_repository import CrudRepository

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DEFAULT_IMG_DIR = "products_images"
API_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))


class FileRepository(CrudRepository):
    model = FileModel
    order_by = (FileModel.id,)
    create_fields = (
        "product_id",
        "inventory_id",
        "purchase_id",
        "language_id",
        "original_name",
        "stored_name",
        "file_path",
        "file_type_id",
        "file_size",
        "sort_order",
        "is_primary",
        "instagram_sort_order",
    )
    update_fields = create_fields

    @classmethod
    def _parse_stored_name(cls, fname):
        name_no_ext = fname.rsplit(".", 1)[0]
        parts = name_no_ext.split("_")
        if len(parts) >= 3:
            lang_code = parts[-1]
            code = parts[0]
            return code, lang_code
        return None, None

    @classmethod
    def _download_remote(cls, url, stored_name=None, sub_dir=None):
        """Download a remote file and store it under DEFAULT_IMG_DIR inside the repo.

        If sub_dir is not given, the stored_name pattern
        ``{code}_{number}_{lang}.jpg`` is parsed to derive
        ``{code}/{lang}/`` as subdirectory.

        Returns (rel_path, size, stored_name)
        """
        try:
            parsed = urlsplit(url)
            fname = stored_name or os.path.basename(parsed.path) or "file"

            # read setting for image path if present
            setting = SettingModel.query.filter_by(setting_key="sync.pokemon.products.img.path").first()
            img_dir = setting.setting_value if setting and setting.setting_value else DEFAULT_IMG_DIR
            # resolve relative paths
            if os.path.isabs(img_dir):
                target_dir = img_dir
            else:
                if img_dir.startswith('..'):
                    target_dir = os.path.join(API_ROOT, img_dir)
                else:
                    target_dir = os.path.join(REPO_ROOT, img_dir)

            if sub_dir is None:
                code, lang_code = cls._parse_stored_name(fname)
                if code and lang_code:
                    sub_dir = os.path.join(code, lang_code)

            if sub_dir:
                target_dir = os.path.join(target_dir, sub_dir)

            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, fname)

            # If file already exists, skip download
            if os.path.exists(target_path):
                return os.path.relpath(target_path, REPO_ROOT), os.path.getsize(target_path), fname

            req = urllib.request.Request(url, headers={"User-Agent": "card-collection/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            with open(target_path, "wb") as f:
                f.write(data)
            return os.path.relpath(target_path, REPO_ROOT), len(data), fname
        except Exception:
            return None, None, None

    @classmethod
    def create(cls, data):
        # If file_path is a remote URL, download it and adjust payload
        file_path = data.get("file_path")
        if file_path and isinstance(file_path, str) and file_path.lower().startswith(("http://", "https://")):
            stored_name = data.get("stored_name")
            rel_path, size, actual_name = cls._download_remote(file_path, stored_name=stored_name)
            if not rel_path:
                raise RuntimeError(f"Failed to download remote file: {file_path}")
            data["file_path"] = rel_path
            data["stored_name"] = actual_name
            data["file_size"] = size

        return super().create(data)
