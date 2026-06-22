from flask import Flask
from routes.auth import auth_bp
from routes.admin import admin_bp

app = Flask(__name__)

app.secret_key = "secret123"

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)