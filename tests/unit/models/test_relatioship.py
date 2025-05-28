from app.models.member import Member
from app.models.relationship import Relationship

def test_relationship_initialization():
    """
    Test the initialization of a Relationship instance.
    Verifies that attributes are correctly set.
    """
    relationship = Relationship(
        relationship_id=1,
        relationship_type="Sibling",
        member_id_1=1,
        member_id_2=2,
    )
    assert relationship.relationship_id == 1
    assert relationship.relationship_type == "Sibling"
    assert relationship.member_id_1 == 1
    assert relationship.member_id_2 == 2


def test_relationship_with_members():
    """
    Test relationships between members.
    Ensure the Relationship instance links correctly to Member instances.
    """
    member1 = Member(
        member_id=1,
        first_name="John",
        last_name="Doe",
        family_id=1,
    )
    member2 = Member(
        member_id=2,
        first_name="Jane",
        last_name="Doe",
        family_id=1,
    )
    relationship = Relationship(
        relationship_id=1,
        relationship_type="Sibling",
        member1=member1,
        member2=member2,
    )
    assert relationship.member1.first_name == "John"
    assert relationship.member2.first_name == "Jane"
    assert relationship.relationship_type == "Sibling"