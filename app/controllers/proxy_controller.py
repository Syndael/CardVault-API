import requests
from flask import Blueprint, request, jsonify, Response

proxy_blueprint = Blueprint("proxy", __name__)


@proxy_blueprint.route("/external", methods=["POST"])
def proxy_external():
    body = request.get_json()
    if not body or not body.get("url"):
        return jsonify({"message": "url field is required"}), 400
    url = body["url"]
    raw = body.get("raw", False)

    try:
        resp = requests.get(url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        if not resp.ok:
            try:
                error_body = resp.json()
            except ValueError:
                error_body = {"message": resp.text[:500]}
            return jsonify({"found": False, "requested_url": url, "status": resp.status_code, "error": error_body}), 200

        if raw:
            content_type = resp.headers.get("Content-Type", "")
            return Response(resp.text, mimetype=content_type)

        try:
            data = resp.json()
            if isinstance(data, dict):
                data["requested_url"] = url
            return jsonify(data), 200
        except ValueError:
            return jsonify({"found": False, "requested_url": url, "message": "Invalid JSON from external API", "status": resp.status_code}), 200
    except requests.RequestException as e:
        return jsonify({"found": False, "requested_url": url, "message": "Proxy error", "error": str(e)}), 200
