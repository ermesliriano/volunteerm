import os
from datetime import timedelta

class Config:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-not-secure")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()

    # Render Internal Database URL (postgresql://...)
    DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

    # CSV de emails con permisos CRUD: "a@x.com,b@y.com"
    _admin_emails_raw = os.getenv("ADMIN_EMAILS", "")
    ADMIN_EMAILS = {e.strip().lower() for e in _admin_emails_raw.split(",") if e.strip()}

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Manejo de desconexiones y "stale connections"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }

    # Cookies sesión
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Uploads: CSV import
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB

    # CSRF: tokens (incluye soporte header X-CSRFToken)
    WTF_CSRF_TIME_LIMIT = 60 * 60 * 2  # 2h

    @staticmethod
    def normalize_database_url(url: str) -> str:
        """
        Normaliza los esquemas para SQLAlchemy y fuerza driver explícito.
        - postgres://  -> postgresql://
        - postgresql:// -> postgresql+psycopg://
        """
        if not url:
            return ""

        url = url.strip()

        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]

        # Si es postgresql:// sin driver explícito, forzamos psycopg (v3)
        if url.startswith("postgresql://"):
            url = "postgresql+psycopg://" + url[len("postgresql://"):]

        return url

    @classmethod
    def init_app_config(cls, app):
        is_prod = cls.ENVIRONMENT == "production"
        app.config["SESSION_COOKIE_SECURE"] = bool(is_prod)

        db_url = cls.normalize_database_url(cls.DATABASE_URL)
        if db_url:
            app.config["SQLALCHEMY_DATABASE_URI"] = db_url
