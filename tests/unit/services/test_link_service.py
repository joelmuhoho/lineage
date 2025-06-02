import pytest
from app.link.services import LinkService
from app.models import Link
from http import HTTPStatus


def test_check_existing_link(test_link_1):
    """
    Tests the `_check_existing_link` method of the `LinkService` class.

    This function verifies if the `_check_existing_link` method correctly checks for
    the existence of a link based on the provided family ID.

    Arguments:
        test_link_1 (Link): An instance of `Link` containing data to simulate
            a family link for testing.

    Raises:
        AssertionError: Raised if the `_check_existing_link` method does not behave
            as expected based on the `TestLink` input.
    """
    service = LinkService()
    assert service._check_existing_link(family_id=test_link_1.family_id)

def test_check_existing_link_no_link():
    """
    Tests the `_check_existing_link` method of the LinkService class
    to verify that it returns False when no link exists for the given
    family ID.
    """
    service = LinkService()
    assert not service._check_existing_link(family_id=17)

def test_create_link(test_family_1):
    """
    Tests the functionality of the create_link method in the LinkService class for
    creating a new link associated with a family.

    Args:
        test_family_1 (Family): A Family object to which the link is associated.

    Raises:
        AssertionError: If the creation of the link does not return the expected
        status code or response structure.

    """
    service = LinkService()
    response, status = service.create_link(test_family_1)
    assert status == HTTPStatus.CREATED
    assert response["message"] == "Link created successfully"
    assert response["category"] == "success"
    assert response["data"] in test_family_1.links

def test_create_link_for_family_with_existing_link(test_family_with_a_link):
    """
    Tests the behavior of the `create_link` method in `LinkService` when attempting
    to create a link for a family that already has an existing link. Ensures that
    the method returns the appropriate conflict status and message, along with
    no data.

    Parameters:
    test_family_with_a_link: object
        A test fixture representing a family instance that already has an
        associated link.

    Raises:
    AssertionError
        If the status returned by the `create_link` method is not equal to
        `HTTPStatus.CONFLICT`.
        If the response message is not "Link already exists for this family".
        If the response data is not `None`.
    """
    service = LinkService()
    response, status = service.create_link(test_family_with_a_link)
    assert status == HTTPStatus.CONFLICT
    assert response["message"] == "Link already exists for this family"
    assert response["data"] is None

def test_create_link_error(test_family_1, monkeypatch):
    """
    Simulates and tests the behavior of the LinkService when an error occurs during
    creation of a link due to a mocked database issue.

    Parameters:
    test_family_1: dict
        A dictionary representing test family data used to simulate the payload for
        creating a link.
    monkeypatch: pytest.MonkeyPatch
        A fixture for dynamically modifying and testing the behavior of objects,
        methods, or attributes.

    Raises:
    Exception
        An exception is raised during the mocked "add" operation in the database
        to simulate a database error.
    """
    service = LinkService()

    def mock_add(*args):
        raise Exception("Database error")

    # Mock the database add method to simulate an error during link creation
    monkeypatch.setattr(service.db, "add", mock_add)

    response, status = service.create_link(test_family_1)
    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["message"] == "Error creating link"
    assert response["data"] is None