from http import HTTPStatus
from app.models import User
from flask import url_for
from flask_login import login_user, logout_user
from app.auth.services import AuthService

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
    response = client.get(url_for("auth.register"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Register" in response.data

    # if the user is authenticated, redirect to the main page
    login_user(test_user_1)
    response = client.get(url_for("auth.register"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Family Tree App" in response.data

def test_register_post(app, client, session):
    """
    Test the registration process functionality for new users by simulating a POST request
    to the registration endpoint and validating the database state and response content.

    Args:
        app: Flask application instance used to run the test context.
        client: Flask test client used to simulate HTTP requests to the application.
        session: Database session used to query and verify the application state.

    Raises:
        AssertionError: If any assertion regarding user registration, response content, or database
                        state fails.

    """
    # given
    user_data = {"name":"New_user",
                 "email":"newuser@mail.com",
                 "password":"newPassword",
                 "confirm_password":"newPassword"}
    # when
    response = client.post(url_for("auth.register"), data=user_data, follow_redirects=True)

    # then
    assert response.status_code == HTTPStatus.OK
    assert b"Login" in response.data

    with app.app_context():
        user = session.query(User).filter_by(email=user_data["email"]).first()
        assert session.query(User).count() == 1
        assert user is not None
        assert user.name == user_data["name"]
        assert user.email == user_data["email"]
        assert user.check_password(user_data["password"]) == True

def test_login_get(client, test_user_1):
    """
    Tests the "GET" behavior of the login route to ensure proper functionality
    and appropriate response status codes. It checks the page loading for
    unauthenticated users and the redirection to the family page for authenticated
    users.

    Args:
        client: Flask test client used for simulating requests.
        test_user_1: Instance of a test user data object pre-populated
            for login simulation.
    """
    response = client.get(url_for("auth.login"))
    assert response.status_code == HTTPStatus.OK
    assert b"Login" in response.data

    # if the user is authenticated, redirect to the family page
    login_user(test_user_1)
    response = client.get(url_for("auth.login"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Create Family" in response.data

def test_login_post(client, test_user_1):
    """
    This function tests the login functionality of an application using a test client.
    It checks whether the login endpoint behaves correctly when provided with invalid
    credentials and when provided with valid credentials.

    Parameters:
    client: The test client is used to simulate requests to the application.
    test_user_1: A test user object containing valid credentials for testing.

    Raises:
    AssertionError: If the expected response code or data for the login process does
    not match the actual responses.
    """
    # test login with incorrect credentials.
    invalid_user_data = {"email": "invalid_user@mail.com", "password": "invalidPassword"}
    response = client.post(url_for("auth.login"), data=invalid_user_data, follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Invalid username or password" in response.data

    # test login with correct credentials.
    user_data = {"email":test_user_1.email, "password":"user1password"}
    response = client.post(url_for("auth.login"), data=user_data, follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Create Family" in response.data

def test_guest_no_guest_info(client, monkeypatch):
    """
    Tests the behavior of the guest endpoint when no guest information is
    available. This ensures that appropriate messages are displayed to
    the user in the absence of guest details and that the response status
    is correct.

    Args:
        client (FlaskClient): Test client used to simulate application
            requests.
        monkeypatch (pytest.MonkeyPatch): Utility used to mock or replace
            objects for testing purposes.
    """

    def mock_get_guest_info(*args):
        return None, None, None

    monkeypatch.setattr(AuthService, "get_guest_info", mock_get_guest_info)

    response = client.get(url_for("auth.guest"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Guest name, email and password are required. Contact admin" in response.data
    assert b"Login" in response.data

    monkeypatch.undo()

def test_guest(client, test_guest_user_1):
    """
    Tests the guest user functionality of the application.

    This function is designed to validate the behavior of the system when a
    guest user attempts to access the guest-related endpoints. It ensures
    that the appropriate response is received, including verifying the
    presence of specific elements in the response data.

    Parameters:
    client
        The test client used to simulate requests to the application.
    test_guest_user_1
        A fixture or mock object representing a guest user instance for
        testing.

    Raises:
    AssertionError
        If any of the assertions fail, indicating that the application’s
        behavior does not match the expected results.
    """
    response = client.get(url_for("auth.guest"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Create Family" in response.data

    # if the guest user is authenticated, redirect to the family page
    response = client.get(url_for("auth.guest"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Create Family" in response.data

def test_guest_incorrect_credentials(client, test_guest_user_1, monkeypatch):
    """
    Tests the behavior of the guest login functionality when incorrect credentials
    are provided. A mocked version of the `get_guest_info` method is used to simulate
    the retrieval of guest information with an invalid password. Ensures the response
    is appropriate and provides the expected error message.

    Args:
        client (FlaskClient): The test client is used to simulate application requests.
        test_guest_user_1 (GuestUser): A test guest user object with predefined
            credentials.
        monkeypatch (MonkeyPatch): The test utility for dynamically modifying the
            behavior of objects or functions.

    Raises:
        AssertionError: If the expected response status or content does not match
            the actual results.
    """
    def mock_get_guest_info(*args):
        return test_guest_user_1.name, test_guest_user_1.email, "InvalidPassword"

    monkeypatch.setattr(AuthService, "get_guest_info", mock_get_guest_info)

    response = client.get(url_for("auth.guest"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Invalid username or password" in response.data
    assert b"Login" in response.data

    monkeypatch.undo()