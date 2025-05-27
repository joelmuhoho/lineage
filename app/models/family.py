from . import db
from .user import User
from .member import Member
from .event import  Event
from .link import  Link
from typing import List
from sqlalchemy.orm import Mapped

class Family(db.Model):
    """
    Represents a family entity in the application.

    This class models a family in the database, including its relationships to users,
    events, members, and links. It defines the family structure and facilitates interactions
    with other entities in the system. Each family has a unique ID, a name, and optionally
    associates with a user. The class supports cascading delete operations for related entities.

    Attributes:
        family_id: The unique identifier for the family.
        name: The name of the family.
        user_id: An optional foreign key referencing the user associated with the family.
        users: The relationship to the User model, representing users associated with the family.
        events: The relationship to the Event model, allowing cascading delete for family-related events.
        members: The relationship to the Member model, enabling cascading delete orphans for members of the family.
        links: The relationship to the Link model, enabling cascading delete orphans for links associated with the family.
    """
    MAX_STRING_LENGTH = 50
    __tablename__ = 'families'

    family_id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(MAX_STRING_LENGTH), nullable=False)

    # Foreign key
    user_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    # Relationships
    users: Mapped[List[User]] = db.relationship('User', back_populates='families')
    events: Mapped[List[Event]] = db.relationship('Event', cascade="all,delete", back_populates='family')
    members: Mapped[List[Member]] = db.relationship('Member', cascade="all,delete-orphan", back_populates='family')
    links: Mapped[List[Link]] = db.relationship('Link', cascade="all,delete-orphan", back_populates='family')
