import os
from datetime import timedelta

class Config:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-not-secure").strip()
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()

    DATABASE_URL = os.getenv("DATABASE_URL", "").strip().strip('"').strip("'")

    # ADMIN_EMAILS puede venir con comillas desde .env en Windows, lo limpiamos
    _admin_raw = os.getenv("ADMIN_EMAILS", "").strip().strip('"').strip("'")
    ADMIN_EMAILS = {e.strip().lower() for e in _admin_raw.split(",") if e.strip()}

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB
    WTF_CSRF_TIME_LIMIT = 60 * 60 * 2  # 2h

    @staticmethod
    def normalize_database_url(url: str) -> str:
        if not url:
            return ""

        url = url.strip()

        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]

        # Si ya trae driver explícito, no tocar
        if url.startswith("postgresql+"):
            return url

        # SQLAlchemy 2.1 usa psycopg por defecto para postgresql://,
        # pero lo dejamos explícito para evitar ambigüedades.
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