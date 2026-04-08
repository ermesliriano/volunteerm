from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db

class UserRole:
    ADMIN = "admin"
    READER = "reader"
    ALL = (ADMIN, READER)

class User(db.Model, UserMixin):
    __tablename__ = "users"
    __table_args__ = (
        db.CheckConstraint(
            "role in ('admin','reader')",
            name="ck_users_role",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(255), unique=True, index=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=True)
    google_sub = db.Column(db.String(255), unique=True, index=True, nullable=True)

    role = db.Column(db.String(20), nullable=False, default=UserRole.READER)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def can_write(self) -> bool:
        return self.is_admin

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
