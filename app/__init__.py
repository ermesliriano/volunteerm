import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config
from .extensions import db, login_manager, csrf
from .models import User

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Base config
    app.config.from_mapping(
        SECRET_KEY=Config.SECRET_KEY,
    )

    if test_config is not None:
        app.config.from_mapping(test_config)
    else:
        # Ensure instance folder exists (SQLite default file often lives there)
        os.makedirs(app.instance_path, exist_ok=True)

        # Apply config class defaults
        app.config.from_object(Config)
        Config.init_app_config(app)

        # If no SQLALCHEMY_DATABASE_URI set, default to SQLite in instance_path
        if not app.config.get("SQLALCHEMY_DATABASE_URI"):
            sqlite_path = os.path.join(app.instance_path, "volunteerm.sqlite3")
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path}"

    # Reverse proxy headers (Render)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    # Extensions
    db.init_app(app)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            uid = int(user_id)
        except ValueError:
            return None
        return User.query.get(uid)

    # Context for templates (Google Client ID)
    @app.context_processor
    def inject_globals():
        return {
            "google_client_id": app.config.get("GOOGLE_CLIENT_ID", ""),
            "environment": app.config.get("ENVIRONMENT", "development"),
        }

    # Blueprints
    from .auth.routes import auth_bp
    from .main.routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Create tables (MVP). For real migrations, use Alembic/Flask-Migrate.
    with app.app_context():
        db.create_all()

    return app
