from app.models.user import User

def test_user_initialization():
    """
    Test user initialization with name, email, and password.
    Verifies that user attributes are correctly set and the password is hashed.
    """
    user = User(name="John Doe", email="john.doe@example.com", password="my-secret")
    assert user.name == "John Doe"
    assert user.email == "john.doe@example.com"
    assert user.password != "my-secret"  # Ensure the password is hashed
    assert user.check_password("my-secret")


def test_set_password():
    """
    Test the set_password method for updating the user's password.
    """
    user = User(name="Jane Doe", email="jane.doe@example.com", password="initial-pass")
    old_password_hash = user.password
    user.set_password("newpassword")
    assert user.password != old_password_hash  # Password hash should change
    assert user.check_password("newpassword")


def test_check_password():
    """
    Test the check_password method to verify correct and incorrect passwords.
    """
    user = User(name="Alice", email="alice@example.com", password="secure-password")
    assert user.check_password("secure-password")  # Correct password
    assert not user.check_password("wrong-password")  # Incorrect password


def test_get_id():
    """
    Test the get_id method to fetch the user's ID.
    """
    user = User(name="Bob", email="bob@example.com", password="mypassword")
    user.user_id = 123  # Mock the user_id
    assert user.get_id() == 123


def test_get_reset_password_token():
    """
    Test the get_reset_password_token method to ensure a token is returned.
    """
    secret_key = "testsecret"
    user = User(name="Charlie", email="charlie@example.com", password="password123")
    user.user_id = 456  # Mock the user_id
    token = user.get_reset_password_token(secret_key)
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_reset_password_token_valid(session):
    """
    Test that verify_reset_password_token correctly decodes a valid token.
    """
    secret_key = "test-secret"
    user = User(name="Dana", email="dana@example.com", password="password")
    user.user_id = 789  # Mock the user_id
    session.add(user)
    session.commit()
    token = user.get_reset_password_token(secret_key)
    assert token is not None
    verified_user = User.verify_reset_password_token(secret_key, token)
    assert verified_user is not None
    assert verified_user.user_id == 789


def test_verify_reset_password_token_invalid():
    """
    Test that verify_reset_password_token handles an invalid token correctly.
    """
    secret_key = "testsecret"
    invalid_token = "invalidtoken"
    verified_user = User.verify_reset_password_token(secret_key, invalid_token)
    assert verified_user is None