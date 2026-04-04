from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(255), unique=True, index=True, nullable=False)

    # Email/password auth
    password_hash = db.Column(db.String(255), nullable=True)

    # Google auth: stable identifier is 'sub'
    google_sub = db.Column(db.String(255), unique=True, index=True, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def has_local_password(self) -> bool:
        return bool(self.password_hash)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
