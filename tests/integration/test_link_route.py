from flask import url_for
from tests.utils import login_test_user_1


def test_create_link(client, test_user_and_family):
    """
    Tests the functionality for creating a family link using the provided client and test data.

    This test ensures that a user can successfully create a link associated with their family
    after logging in. It verifies the HTTP response status code and checks for the expected
    success message in the response data.

    Parameters:
        client
            A test client instance used to simulate requests to the application server.
        test_user_and_family
            A tuple containing a test user object and their associated family object.
    """
    user, family = test_user_and_family
    login_test_user_1(client, user)
    response = client.post(url_for("link.create_link"), data={"family_id": family.family_id}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Link created successfully" in response.data

    # create a link a second time when a link already exists
    response = client.post(url_for("link.create_link"), data={"family_id": family.family_id}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Link already exists for this family" in response.data


def test_create_link_no_family_id(client, test_user_1):
    """
    Tests the creation of a link without providing a family id. Ensures proper handling
    of missing required data by the request handler and validates the returned
    response and error message to confirm expected application behavior.

    Args:
        client: Flask test client used to simulate and make requests to
            the application during testing.
        test_user_1: Predefined test user fixture provided for authentication
            purposes during tests.

    Raises:
        AssertionError: If the response status code is not 200, or the expected
            error message is not found in the response data.
    """
    login_test_user_1(client, test_user_1)
    response = client.post(url_for("link.create_link"), follow_redirects=True)
    assert response.status_code == 200
    assert b"Family id is required" in response.data

def test_create_link_non_existing_family(client, test_user_1):
    """
    Tests the creation of a link with a non-existing family ID to ensure that
    the server responds appropriately by indicating the family was not found.

    Args:
    client: The test client is used to mock HTTP requests.
    test_user_1: A test user object used for login authentication.

    Raises:
    AssertionError: If the HTTP status code is not 200 or if the response
    does not contain the expected message indicating the family was not found.
    """
    login_test_user_1(client, test_user_1)
    response = client.post(url_for("link.create_link"), data={"family_id": 100}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Family not found" in response.data

def test_create_link_for_family_not_belonging_to_user(client, test_user_and_family, test_family_2):
    """
    Tests the creation of a family link for a family not belonging to the user.
    Ensures that users cannot create links for unauthorized families.

    Args:
        client: Test client for making HTTP requests.
        test_user_and_family: Fixture providing a test user and associated family.
        test_family_2: Fixture providing a second test family not associated with the test user.

    Raises:
        AssertionError: If the response status code is not 200 or if the error message
        "You do not have permission to access this family" is not found in the response.
    """
    user, family = test_user_and_family
    login_test_user_1(client, user)
    response = client.post(url_for("link.create_link"), data={"family_id": test_family_2.family_id}, follow_redirects=True)
    assert response.status_code == 200
    assert b"You do not have permission to access this family" in response.data