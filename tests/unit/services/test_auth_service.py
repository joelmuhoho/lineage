import pytest
from app.auth.services import AuthService
from app.models.user import User, Family
from flask_login import logout_user
from flask import session as flask_session

@pytest.fixture
def test_user(session):
    """
    This fixture creates and manages a temporary test user in a database session for testing
    purposes. The fixture ensures that the test user is added to the database at the start of
    the test and removed after the test completes, maintaining a clean testing environment.

    Args:
        session: The database session to use for adding and removing the test user.

    Yields:
        User: The temporary test user created for the purpose of the test.
    """
    user = User(
        name="test_user",
        email="testuser@example.com",
        password="secure_password"
    )
    session.add(user)
    session.commit()
    yield user
    session.delete(user)
    session.commit()

@pytest.fixture
def user_with_one_family(session):
    """
    Creates a pytest fixture that sets up a user with a single associated family
    in the database session. This fixture is intended for use in tests requiring
    a user with one family relation. After the test execution, the fixture ensures
    cleanup by deleting the created user and associated family from the database.

    Yields
    ------
    User
        The user object created for the test.
    """
    user = User(name="onefamily", email="one@ex.com", password="newPass")
    session.add(user)
    session.commit()

    family = Family(name="Solo Family", user_id=user.user_id)
    session.add(family)
    session.commit()

    yield user
    session.delete(family)
    session.delete(user)
    session.commit()

@pytest.fixture
def user_with_two_families(session):
    """
    This pytest fixture function creates and returns a user along with two associated families
    to be used in testing. It ensures appropriate setup and teardown by managing database
    entries within a session.

    Attributes:
        session: A pytest fixture that provides database session management.

    Yields:
        Tuple[User, List[Family]]: A tuple containing the created User object and a list
        of two associated Family objects.

    Raises:
        None
    """
    user = User(name="twofamily", email="two@ex.com", password="newPaas")
    session.add(user)
    session.commit()

    f1 = Family(name="Fam1", user_id=user.user_id)
    f2 = Family(name="Fam2", user_id=user.user_id)
    session.add_all([f1, f2])
    session.commit()

    yield user, [f1, f2]
    session.delete(f1)
    session.delete(f2)
    session.delete(user)
    session.commit()

def test_authenticate_valid_user(app, test_user):
    """
    Authenticate and validate a user within a test request context by simulating a
    login process. The function asserts the response received from the authentication
    service and ensures the returned data aligns with expected results.

    Parameters:
    app : Flask
        The Flask application instance used for testing purposes.
    test_user : User
        A mock or predefined user object that represents a valid test user.

    Raises:
    AssertionError
        If the status, message, category, or data in the response do not match
        the expected values.
    """
    with app.test_request_context():
        response = AuthService.authenticate("testuser@example.com", "secure_password")

        assert isinstance(response, tuple)
        data, status = response[0], response[1]
        assert status == 200
        assert data['message'] == "Login successful"
        assert data['category'] == "success"
        assert data['data'].email == test_user.email

def test_authenticate_invalid_password(app, test_user):
    """
    Test the behavior of the authentication service when provided with an invalid password for a valid user.

    This function checks if the authentication service correctly identifies and rejects an invalid
    password, returning the appropriate error message and HTTP status code.

    Args:
        app: The application object providing the test request context.
        test_user: A valid user object pre-registered in the test database.

    Raises:
        AssertionError: If the authentication service does not return the expected results.

    """
    with app.test_request_context():
        response = AuthService.authenticate(test_user.email, "wrongpassword")

        assert isinstance(response, tuple)
        data, status = response[0], response[1]
        assert status == 403
        assert data['message'] == "Invalid username or password"
        assert data['data'] is None

def test_authenticate_nonexistent_user(app):
    """
    Test the authentication process for a nonexistent user. This function verifies
    that the AuthService correctly handles a request to authenticate a user who
    does not exist in the system.

    Args:
        app: The Flask application instance used to create a test request context.

    Raises:
        AssertionError: If the AuthService does not return the expected response
        values, including the proper status code and error message format.
    """
    with app.test_request_context():
        response = AuthService.authenticate("nouser@example.com", "any")

        assert isinstance(response, tuple)
        data, status = response[0], response[1]
        assert status == 403
        assert data['message'] == "Invalid username or password"
        assert data['data'] is None

def test_set_current_family_id_one_family(app, user_with_one_family):
    """
    Tests the `set_current_family_id` functionality for a user with one associated
    family. This ensures that the `current_family_id` is correctly set in the user's
    session and matches the single family's ID.

    Args:
        app: A Flask application configured for testing.
        user_with_one_family: A user fixture representing a user with exactly one
            associated family.

    Raises:
        AssertionError: If `current_family_id` is not set in the session or does not
        match the expected family ID.
    """
    with app.test_request_context():
        AuthService.authenticate(email=user_with_one_family.email, password="newPass")
        AuthService.set_current_family_id()

        assert 'current_family_id' in flask_session
        assert flask_session['current_family_id'] == user_with_one_family.families[0].family_id
        logout_user()

def test_set_current_family_id_multiple_with_param(app, user_with_two_families):
    """
    Tests the ability to switch the current family context for a user with multiple families.

    This function verifies that the `set_current_family_id` method correctly updates the
    current family ID in the session for an authenticated user with two families. It ensures
    that the session reflects the updated family ID and validates the status after logout.

    Parameters:
        app (Flask): The Flask application context used for testing.
        user_with_two_families (Tuple[User, List[Family]]): A tuple containing a user object and
            a list of two family objects associated with the user.

    Raises:
        AssertionError: If the current family ID is not correctly set in the session or
            if session verification fails after the method call.
    """
    user, families = user_with_two_families
    with app.test_request_context():
        AuthService.authenticate(email=user.email, password="newPaas")
        AuthService.set_current_family_id(current_family_id=families[1].family_id)

        assert 'current_family_id' in flask_session
        assert flask_session['current_family_id'] == families[1].family_id
        logout_user()

def test_set_current_family_id_multiple_without_param(app, user_with_two_families):
    """
    Tests the behavior of the set_current_family_id method when called without any
    parameters, verifying that it does not set a current_family_id in the session
    and returns the flask_session unchanged. Additionally, validates the correct
    operation of user authentication and logout mechanisms.

    Args:
        app: Flask application instance used to create a test request context.
        user_with_two_families: A tuple containing a user instance with two
            associated families and additional related data, if any.

    Raises:
        AssertionError: If the current_family_id is present in flask_session or
            if the returned value of set_current_family_id does not match the
            actual flask_session.
    """
    user, _ = user_with_two_families
    with app.test_request_context():
        AuthService.authenticate(email=user.email, password="newPaas")
        result = AuthService.set_current_family_id()  # no param

        assert 'current_family_id' not in flask_session
        assert result == flask_session
        logout_user()