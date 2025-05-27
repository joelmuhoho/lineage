from . import db
from sqlalchemy.orm import Mapped
from typing import Optional, List
from datetime import date

class Member(db.Model):
    """
    represents a Member entity in the database.

    this class is an SQLAlchemy model that maps to the 'members' table in the database.
    it is used to represent individuals within a family tree structure by storing their
    personal information, relationships, and familial connections.

    Attributes:
        member_id (int): The unique identifier for the member, acting as the primary key.
        first_name (str): The first name of the member.
        last_name (str): The last name of the member.
        birthdate (date): The date of birth of the member.
        deathdate (date): The death date of the member.
        gender (str): The gender of the member.
        root (bool): Indicates if the member is a root member of the family tree.
        alive (bool): Indicates if the member is currently alive.
        mother (Optional[int]): The member ID of the mother, if known.
        father (Optional[int]): The member ID of the father, if known.
        family_id (int): The foreign key linking the member to a family.
        user_id (Optional[int]): The foreign key linking the member to a user, if applicable.
        family (Family): Reference to the associated Family object.
        relationships1 (List[Relationship]): List of relationships where this member is the first individual.
        relationships2 (List[Relationship]): List of relationships where this member is the second individual.

    Methods:
        to_dict():
            Converts the Member object and its attributes into a dictionary representation.
    """
    __tablename__ = 'members'

    member_id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    first_name:Mapped[str] = db.Column(db.String(50), nullable=False)
    last_name:Mapped[str] = db.Column(db.String(50), nullable=False)
    birthdate:Mapped[date] = db.Column(db.Date)
    deathdate:Mapped[date] = db.Column(db.Date)
    gender:Mapped[str] = db.Column(db.String(10))
    root:Mapped[bool] = db.Column(db.Boolean, default=False)
    alive:Mapped[bool] = db.Column(db.Boolean)

    # Member Parents
    mother:Mapped[Optional[int]] = db.Column(db.Integer, nullable=True)
    father:Mapped[Optional[int]] = db.Column(db.Integer, nullable=True)

    # Foreign Keys
    family_id:Mapped[int] = db.Column(db.Integer, db.ForeignKey('families.family_id'), nullable=False)
    user_id:Mapped[Optional[int]] = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    # Relationships
    family:Mapped["Family"] = db.relationship('Family', back_populates='members')
    relationships1:Mapped[List["Relationship"]] = db.relationship('Relationship', foreign_keys="[Relationship.member_id_1]", cascade="all, delete-orphan", back_populates='member1')
    relationships2:Mapped[List["Relationship"]] = db.relationship('Relationship', foreign_keys="[Relationship.member_id_2]", cascade="all, delete-orphan", back_populates='member2')

    def to_dict(self)-> dict:
        """
        Converts the current object instance into a dictionary representation.

        The method provides a dictionary that includes attributes of the object.
        It also ensures that any internal SQLAlchemy state is excluded from the
        resulting dictionary to prevent unintended exposure of implementation details.

        Returns:
            dict: A dictionary representation of the current
            object instance.
        """
        dictionary = {}
        dictionary.update(self.__dict__)
        if '_sa_instance_state' in dictionary:
            del dictionary['_sa_instance_state']
        return dictionary