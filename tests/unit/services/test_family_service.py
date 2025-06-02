import pytest
from app.family.services import FamilyService

def test_get_family_by_id(test_family_1):
    """
    Tests the `get_family_by_id` method from the `FamilyService` class. Ensures
    that the method correctly retrieves a family record by its unique identifier
    and validates the returned response and status code.

    Parameters:
    test_family_1 : Family
        A test fixture or mocked object representing a family entity, which includes
        the family ID that will be used for querying.

    Raises:
    AssertionError
        If the status code does not match 200, or the response message and data values
        do not match the expected results.
    """
    service = FamilyService()
    response, status = service.get_family_by_id(test_family_1.family_id)
    assert status == 200
    assert response['message'] == "Family found"
    assert response['data'] == test_family_1

def test_get_family_by_id_nonexistent():
    """
    Test function for checking the behavior of the get_family_by_id method
    when a family with a nonexistent ID is requested. This test ensures that
    the function returns the correct status and error message for invalid
    input.
    """
    service = FamilyService()
    response, status = service.get_family_by_id(17)
    assert status == 404
    assert response['message'] == "Family not found"
    assert response['data'] is None

def test_get_family_by_id_error(test_family_1, monkeypatch):
    """
    Tests the behavior of the `get_family_by_id` method in `FamilyService` when a database error occurs.
    The database query method is mocked to raise an exception, simulating a database failure.

    Args:
        test_family_1: Fixture representing a mocked family object or test data
            used in testing.
        monkeypatch: Fixture provided by pytest, used to modify or override
            objects and functions during testing.
    """
    service = FamilyService()

    def mock_query(*args):
        raise Exception("Database error")
    monkeypatch.setattr(service.db, "query", mock_query)
    response, status = service.get_family_by_id(family_id=test_family_1.family_id)
    assert status == 500

def test_get_user_families(test_user_with_two_families):
    """
    Test the retrieval of user families using the FamilyService class.

    This function checks if the `get_user_families` method of the FamilyService
    class works as expected. It validates that the correct status code, message,
    and family data are returned when a user with two families is provided.

    Parameters
    ----------
    test_user_with_two_families : User
        a user that is associated with twp families
    """
    service = FamilyService()
    response, status = service.get_user_families(test_user_with_two_families.user_id)
    assert status == 200
    assert response['message'] == "Families found"
    assert len(response['data']) == 2

def test_get_user_families_no_families(test_user_1):
    """
    Tests the retrieval of user families when no families exist for the given user.

    This test ensures that the get_user_families method of FamilyService
    returns the correct response and status code when no families are found
    for the user ID provided.

    Args:
        test_user_1 (User): A test user object used to perform the test.

    Raises:
        AssertionError: If the response status code or message does not match
        the expected outcome.
    """
    service = FamilyService()
    response, status = service.get_user_families(test_user_1.user_id)
    assert status == 404
    assert response['message'] == "No families found"
    assert response['data'] is None

def test_get_user_families_error(test_user_with_two_families, monkeypatch):
    """
    Test function for handling errors in the `get_user_families` method of the
    `FamilyService` when a database query fails. It simulates a scenario where
    an exception is raised during a database operation and ensures that the
    method handles the error correctly.

    Parameters
    ----------
    test_user_with_two_families : User
        A fixture object representing a test user associated with
        two family records in the database.
    monkeypatch : pytest Fixture
        Utility for dynamically modifying or patching code during tests.

    Raises
    ------
    Exception
        Raised during the database query to simulate an error condition.
    """
    service = FamilyService()

    def mock_query(*args):
        raise Exception("Database error")
    # mock the database query method to raise an exception during the family retrieval
    monkeypatch.setattr(service.db, "query", mock_query)

    response, status = service.get_user_families(test_user_with_two_families.user_id)
    assert status == 500
    assert response['message'] == "Error retrieving families"
    assert response['data'] is None