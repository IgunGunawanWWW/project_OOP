from flask import Flask, session, request
from routes.auth import auth_bp

app = Flask(__name__)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(debug=True)