from . import db
from sqlalchemy.orm import Mapped

class Link(db.Model):
    """Class representing a link in the application."""
    __tablename__ = 'links'

    link_id:Mapped[int] = db.Column(db.Integer, primary_key=True)
    link:Mapped[str] = db.Column(db.String(500), nullable=True)

     # Foreign Key
    family_id:Mapped[int] = db.Column(db.Integer, db.ForeignKey('families.family_id'), nullable=False)

    # Relationships
    family:Mapped["Family"] = db.relationship('Family', back_populates='links')

