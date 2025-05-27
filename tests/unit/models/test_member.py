from datetime import date
from app.models.family import Family
from app.models.member import Member

def test_member_initialization():
    """
    Test the initialization of a Member instance.
    Verifies that attributes are correctly set.
    """
    family = Family(family_id=1, name="Smith Family", user_id=1)
    member = Member(
        member_id=1,
        first_name="John",
        last_name="Doe",
        birthdate=date(1980, 5, 20),
        deathdate=None,
        gender="Male",
        root=True,
        alive=True,
        mother=None,
        father=None,
        family_id=1,
        user_id=1,
        family=family,
        relationships1=[],
        relationships2=[]
    )

    assert member.member_id == 1
    assert member.first_name == "John"
    assert member.last_name == "Doe"
    assert member.birthdate == date(1980, 5, 20)
    assert member.deathdate is None
    assert member.gender == "Male"
    assert member.root is True
    assert member.alive is True
    assert member.mother is None
    assert member.father is None
    assert member.family_id == 1
    assert member.user_id == 1
    assert member.family == family
    assert member.relationships1 == []
    assert member.relationships2 == []


def test_member_to_dict():
    """
    Test the to_dict method of a Member instance.
    Verifies that the dictionary representation of the Member is accurate.
    """
    member = Member(
        member_id=1,
        first_name="Jane",
        last_name="Smith",
        birthdate=date(1990, 12, 15),
        deathdate=None,
        gender="Female",
        root=False,
        alive=True,
        mother=2,
        father=3,
        family_id=5,
        user_id=None,
        family=None,
        relationships1=[],
        relationships2=[]
    )

    member_dict = member.to_dict()

    assert member_dict["member_id"] == 1
    assert member_dict["first_name"] == "Jane"
    assert member_dict["last_name"] == "Smith"
    assert member_dict["birthdate"] == date(1990, 12, 15)
    assert member_dict["deathdate"] is None
    assert member_dict["gender"] == "Female"
    assert member_dict["root"] is False
    assert member_dict["alive"] is True
    assert member_dict["mother"] == 2
    assert member_dict["father"] == 3
    assert member_dict["family_id"] == 5
    assert member_dict["user_id"] is None
    assert "_internal_state" not in member_dict
