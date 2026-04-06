from app.extensions import db
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    READ = "read"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200))

    role = db.Column(db.Enum(UserRole), default=UserRole.READ)
