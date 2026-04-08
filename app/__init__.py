import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config
from .extensions import csrf, db, login_manager

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Defaults
    app.config.from_mapping(
        SECRET_KEY=Config.SECRET_KEY,
    )

    if test_config:
        app.config.from_mapping(test_config)
    else:
        os.makedirs(app.instance_path, exist_ok=True)
        app.config.from_object(Config)
        Config.init_app_config(app)

        # Fallback SQLite si no hay DATABASE_URL
        if not app.config.get("SQLALCHEMY_DATABASE_URI"):
            sqlite_path = os.path.join(app.instance_path, "volunteerm.sqlite3")
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path}"

    # Proxy headers (Render)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    # Extensions
    db.init_app(app)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id: str):
        # Import lazy para evitar ciclos
        from .models import User
        try:
            uid = int(user_id)
        except ValueError:
            return None
        return User.query.get(uid)

    @app.context_processor
    def inject_globals():
        return {
            "google_client_id": app.config.get("GOOGLE_CLIENT_ID", ""),
            "environment": app.config.get("ENVIRONMENT", "development"),
        }

    # Blueprints
    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .volunteers.routes import volunteers_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(volunteers_bp)

    # Create tables (MVP): asegúrate de que los modelos están importados
    with app.app_context():
        from .models import User, Volunteer  # noqa: F401
        db.create_all()

    return app