from datetime import datetime
from ..extensions import db

class Volunteer(db.Model):
    __tablename__ = "volunteers"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(255), unique=True, index=True, nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(120), nullable=True)
    availability = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    created_by = db.relationship("User", foreign_keys=[created_by_id])

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Volunteer id={self.id} full_name={self.full_name}>"
