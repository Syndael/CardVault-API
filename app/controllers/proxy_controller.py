import requests
from flask import Blueprint, request, jsonify

proxy_blueprint = Blueprint("proxy", __name__)


@proxy_blueprint.route("/external", methods=["POST"])
def proxy_external():
    body = request.get_json()
    if not body or not body.get("url"):
        return jsonify({"message": "url field is required"}), 400
    url = body["url"]

    try:
        resp = requests.get(url, timeout=30, headers={
            "User-Agent": "CardVault-Proxy/1.0"
        })
        if not resp.ok:
            try:
                error_body = resp.json()
            except ValueError:
                error_body = {"message": resp.text[:500]}
            return jsonify({"found": False, "status": resp.status_code, "error": error_body}), 200
        try:
            return jsonify(resp.json()), 200
        except ValueError:
            return jsonify({"found": False, "message": "Invalid JSON from external API", "status": resp.status_code}), 200
    except requests.RequestException as e:
        return jsonify({"found": False, "message": "Proxy error", "error": str(e)}), 200
