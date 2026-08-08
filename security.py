import hmac
import secrets

from flask import abort, jsonify, request, session


def csrf_token():
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def protect_csrf():
    if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return None

    submitted = request.headers.get("X-CSRFToken") or request.form.get("csrf_token")
    expected = session.get("_csrf_token")
    if not expected or not submitted or not hmac.compare_digest(submitted, expected):
        if request.is_json:
            return jsonify({"status": "error", "message": "CSRF token tidak valid"}), 400
        abort(400, description="CSRF token tidak valid")
    return None
