from app.models.family import Family
from app.models.link import Link


def test_link_initialization():
    """
    Test the initialization of a Link instance.
    Verifies that attributes are correctly set.
    """
    family = Family(family_id=1, name="Smith Family", user_id=1)
    link = Link(link_id=101, link="https://joelmuhoho.com", family=family, family_id=1)
    assert link.link_id == 101
    assert link.link == "https://joelmuhoho.com"
    assert link.family_id == 1
    assert link.family == family