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

def test_get_family_by_id_nonexistent(test_family_1):
    """
    Test function for checking the behavior of the get_family_by_id method
    when a family with a nonexistent ID is requested. This test ensures that
    the function returns the correct status and error message for invalid
    input.

    Args:
        test_family_1: Mocked family data used for testing purposes.
    """
    service = FamilyService()
    response, status = service.get_family_by_id(999999999)
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