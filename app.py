import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure CORS
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://localhost/flask_api")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "jwt-secret-change-in-production")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  # Tokens don't expire for simplicity

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models  # noqa: F401
    
    # Import and register API routes
    from api_routes import api_bp
    app.register_blueprint(api_bp)
    
    # Create all tables
    db.create_all()
    
    # Create default admin token if not exists
    from models import ApiToken
    from auth import generate_token
    
    admin_token = ApiToken.query.filter_by(name="admin").first()
    if not admin_token:
        token_value = generate_token({"user": "admin", "role": "admin"})
        admin_token = ApiToken(name="admin", token=token_value, is_active=True)
        db.session.add(admin_token)
        db.session.commit()
        app.logger.info(f"Created admin token: {token_value}")

@app.route('/')
def index():
    """Serve the API documentation page"""
    from flask import render_template
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
