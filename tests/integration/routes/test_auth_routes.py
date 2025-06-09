from http import HTTPStatus
from app.models import User
from flask import url_for
from flask_login import login_user, logout_user

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
    response = client.get(url_for("auth.register"))
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