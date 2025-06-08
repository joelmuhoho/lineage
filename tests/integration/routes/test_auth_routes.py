from http import HTTPStatus
from flask_login import login_user

def test_register_get(client, test_user_1):
    """
    Tests the behavior of the registration page in two scenarios:
    - When accessed by an unauthenticated user.
    - When accessed by an authenticated user, ensuring they are redirected to the main
    page.

    Attributes:
        client: A fixture that simulates a test client for making HTTP requests.
        test_user_1: A fixture representing a pre-existing test user.

    Args:
        client: Test client used to perform HTTP requests in the tests.
        test_user_1: Test user used to simulate authentication in the test.
    """
    response = client.get("/register")
    assert response.status_code == HTTPStatus.OK
    assert b"Register" in response.data

    # if the user is authenticated, redirect to the main page
    login_user(test_user_1)
    response = client.get("/register", follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Family Tree App" in response.data