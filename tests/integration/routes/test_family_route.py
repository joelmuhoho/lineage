from tests.utils import login_test_user_1
from flask import url_for

def test_index(client, test_user_1):
    """
    Tests the 'index' view of the 'family' blueprint to ensure it renders
    correctly and contains expected content.

    Args:
    client: Flask test client used to simulate HTTP requests during testing.
    test_user_1: Fixture providing a test user object.

    Raises:
    AssertionError: If the response status code is not 200 or expected content
    is not found in the response data.
    """
    login_test_user_1(client, test_user_1)

    response = client.get(url_for("family.index"), follow_redirects=True)
    assert response.status_code == 200
    assert b"Create Family" in response.data

def test_index_with_family_id(client, test_user_and_family):
    """
    Executes a test case to verify that the 'index' page for a specific family ID renders
    successfully after authenticating the test user.

    Parameters:
    client : flask.testing.FlaskClient
        A test client object for simulating requests to the application.
    test_user_and_family : tuple
        A tuple containing a test user and their associated family.

    Raises:
    AssertionError
        If the response status code is not 200 or if the expected content is not in the
        response data.
    """
    user, family = test_user_and_family
    login_test_user_1(client, user)
    response = client.get(url_for("family.index", family_id=family.family_id), follow_redirects=True)
    assert response.status_code == 200
    assert b"Test Family 1" in response.data

def test_index_with_invalid_family_id(client, test_user_and_family, test_family_2):
    """
    Tests the accessibility of the family index page with an invalid family ID to
    ensure the system properly handles unauthorized access by redirecting the user
    and displaying an appropriate error message.

    Args:
        client: Flask test client used to simulate HTTP requests in testing.
        test_user_and_family: Tuple containing a user object and their associated
            family object.
        test_family_2: A second family object used for testing unauthorized access.

    Raises:
        AssertionError: If the response status code is not 200, or the error message
        does not appear in the response data.
    """
    user, family = test_user_and_family
    login_test_user_1(client, user)
    response = client.get(url_for("family.index", family_id=test_family_2.family_id), follow_redirects=True)
    assert response.status_code == 200
    assert b"You do not have permission to access this family" in response.data
