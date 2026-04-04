import os
from datetime import timedelta

class Config:
    # Base
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-not-secure")

    # Google Identity Services
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

    # DB
    DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # CSRF
    WTF_CSRF_TIME_LIMIT = 60 * 60 * 2  # 2h

    @staticmethod
    def normalize_database_url(url: str) -> str:
        """
        Normaliza DATABASE_URL para SQLAlchemy, especialmente si viene con
        esquemas legacy tipo 'postgres://'.
        """
        if not url:
            return ""
        if url.startswith("postgres://"):
            return "postgresql://" + url[len("postgres://"):]
        return url

    @classmethod
    def init_app_config(cls, app):
        # Detecta prod y aplica flags HTTPS
        is_prod = cls.ENVIRONMENT == "production"
        app.config["SESSION_COOKIE_SECURE"] = bool(is_prod)

        # DB URL final
        db_url = cls.normalize_database_url(cls.DATABASE_URL)
        if db_url:
            app.config["SQLALCHEMY_DATABASE_URI"] = db_url
