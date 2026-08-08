import os
import secrets

from flask import Flask
from flask import request, session
from routes.auth import auth_bp
from routes.admin import admin_bp
from security import csrf_token, protect_csrf

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("SESSION_COOKIE_SECURE") == "1"


@app.context_processor
def inject_security_context():
    return {"csrf_token": csrf_token()}


@app.before_request
def enforce_csrf():
    return protect_csrf()

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")