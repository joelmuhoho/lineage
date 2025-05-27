from app.models.event import Event
from app.models.family import Family
from app.models.link import Link
from app.models.member import Member
from app.models.user import User
from datetime import date

def test_family_initialization():
    """
    Test the initialization of a Family instance.
    Verifies that attributes are correctly set.
    """
    family = Family(family_id=1, name="Smith Family", user_id=1)
    assert family.family_id == 1
    assert family.name == "Smith Family"
    assert family.user_id == 1


def test_family_relationships(session):
    """
    Test Family relationships with User, Event, Member, and Link models.
    Verifies relationships are established correctly.
    """
    user = User(name="John Doe", email="john.doe@example.com", password="test")
    family = Family(family_id=2, name="Doe Family", user_id=1)
    event = Event(event_date=date(2024, 5, 7), event_name="Family Reunion", family_id=2)
    member = Member(first_name="Jane", last_name="Doe", family_id=2)
    link = Link(link="https://joelmhoho.com", family_id=2)

    session.add_all([user, family, event, member, link])
    session.commit()

    assert family.users is not None
    assert len(family.events) == 1
    assert family.events[0].event_name == "Family Reunion"
    assert len(family.members) == 1
    assert family.members[0].first_name == "Jane"
    assert len(family.links) == 1
    assert family.links[0].link == "https://joelmhoho.com"


def test_family_name_length_constraint():
    """
    Test Family name length constraint.
    Ensures that the name doesn't exceed the allowed string length.
    """
    family = Family(name="w" * 49)
    assert len(family.name) <= Family.MAX_STRING_LENGTH


def test_family_cascade_delete_relationships(session):
    """
    Test cascading deletion for related entities.
    Ensures that deleting a Family instance deletes related Members, Events, and Links.
    """
    family = Family(family_id=3, name="Test Family", user_id=1)
    event = Event(event_date=date(2023, 11, 2), event_name="Birthday Party", family_id=3)
    member = Member(first_name="Test", last_name="Member", family_id=3)
    link = Link(link="https://joelmuhoho.com", family_id=3)

    session.add_all([family, event, member, link])
    session.commit()

    session.delete(family)
    session.commit()

    assert session.query(Event).filter_by(family_id=3).count() == 0
    assert session.query(Member).filter_by(family_id=3).count() == 0
    assert session.query(Link).filter_by(family_id=3).count() == 0