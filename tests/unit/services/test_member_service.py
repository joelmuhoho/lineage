from app.member.services import MemberService
from http import HTTPStatus
from flask_login import login_user, logout_user

def test_get_member_unauthenticated(test_member_1):
    """
    Tests the behavior of the get_member method when the user is unauthenticated.

    This test ensures that the service correctly handles unauthenticated access and
    returns the appropriate HTTP status code and response when attempting to retrieve
    a member's information without being logged in.

    Attributes:
        test_member_1 (Member): A pre-created test instance of the Member model
            with a valid member_id used for testing.

    Parameters:
        test_member_1 (Member): The member instance to test retrieving member
            information when unauthenticated.

    Returns:
        None
    """
    logout_user()
    service = MemberService()
    response, status = service.get_member(test_member_1.member_id)
    assert status == HTTPStatus.UNAUTHORIZED
    assert response['data'] is None

def test_get_member_not_found(test_user_1):
    """
    Tests the retrieval of a member that does not exist in the system.

    The function simulates a situation where the user is logged in, and an attempt is made
    to retrieve a member with an ID that does not exist, ensuring the system correctly
    returns a NOT_FOUND status and no member data.

    Args:
        test_user_1: A test fixture representing a user.

    Raises:
        AssertionError: If the response does not match the expected outcome.
    """
    login_user(test_user_1)

    service = MemberService()
    response, status = service.get_member(9999)

    assert status == HTTPStatus.NOT_FOUND
    assert response['data'] is None

def test_get_member_forbidden(test_member_1, test_user_1):
    """
    Tests the behavior of the MemberService for users attempting to access
    restricted members' data without appropriate permissions.

    This test confirms that an authenticated user cannot access
    the data of a member they are unauthorized to view,
    and that the appropriate HTTP status and response are returned.

    Args:
        test_member_1: A test member object that the user attempts
                       to access.
        test_user_1: A test user object representing the user
                     performing the access.

    Raises:
        AssertionError: If the returned HTTP status code or response
                        data does not meet the expected conditions.
    """
    login_user(test_user_1)

    service = MemberService()
    response, status = service.get_member(test_member_1.member_id)
    assert status == HTTPStatus.FORBIDDEN
    assert response['data'] is None

def test_get_member_success(session, test_member_1, test_user_1):
    """
    Tests the successful retrieval of a member's information.

    This function verifies that a member's data can be successfully retrieved
    when the member is associated with a family, and the user has access to
    the respective family.

    Parameters:
    session : Session object
        The database session used for committing changes and verifying the test.
    test_member_1 : Member object
        The test member whose data is to be retrieved.
    test_user_1 : User object
        The test user attempting to access the member's data.

    Raises:
    AssertionError
        If the response status is not HTTPStatus.OK or if the retrieved data
        does not match the `test_member_1` information.
    """
    family = test_member_1.family
    test_user_1.families.append(family)
    session.commit()
    login_user(test_user_1)

    service = MemberService()
    response, status = service.get_member(test_member_1.member_id)

    assert status == HTTPStatus.OK
    assert response['data'] == test_member_1

def test_get_member_error(session, test_member_1, test_user_1, monkeypatch):
    """
    Simulates an error during the retrieval of a family member's details by mocking the query
    method in the service layer. Verifies that the application handles the error as expected
    and returns the appropriate HTTP status and response structure.

    Args:
        session: Database session configured for the test.
        test_member_1: Test fixture representing a sample member of a family.
        test_user_1: Test fixture representing a sample user.
        monkeypatch: Fixture used to dynamically replace the behavior of objects.

    Raises:
        Exception: Mocked query function raises an exception to simulate a database error.

    Returns:
        None
    """
    family = test_member_1.family
    test_user_1.families.append(family)
    session.commit()
    login_user(test_user_1)

    service = MemberService()

    def mock_query(*args):
        raise Exception("Database error")

    # mock the query method to simulate an error during member retrieval
    monkeypatch.setattr(service.db, "query", mock_query)

    response, status = service.get_member(test_member_1.member_id)

    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response['data'] is None

def test_is_member_accessible_by_user_true(test_member_1, test_user_1 ):
    """
    Checks if a specific member is accessible by a user through the member's
    associated family. The function ensures the user is logged in, associates
    the member's family with the user, and then verifies accessibility using
    the MemberService class.

    Args:
        test_member_1: The member whose accessibility will be checked by the user.
        test_user_1: The user for whom member accessibility is validated.

    Raises:
        AssertionError: If the member is not accessible by the user as expected.
    """
    login_user(test_user_1)

    # associate the member family with the user
    family = test_member_1.family
    test_user_1.families.append(family)

    service = MemberService()

    assert service.is_member_accessible_by_user(test_member_1)

def test_is_member_accessible_by_user_false(test_member_1, test_user_1 ):
    """
    Determines if a member is accessible by a specific user and asserts that it is not.

    Tests the `is_member_accessible_by_user` method provided by `MemberService` to
    ensure that the given member is not accessible to the provided user after logging
    into the system with the user.

    Parameters:
    test_member_1: The member object to test accessibility for.
    test_user_1: The user object to test access rights against.
    """
    login_user(test_user_1)

    service = MemberService()
    assert not service.is_member_accessible_by_user(test_member_1)

def test_create_member(app):
    """
    Tests the `create_member` functionality of the `MemberService` class to ensure
    a member is successfully created given valid input parameters. Verifies that
    the response includes the expected message, category, and data, and that the
    HTTP status code matches the expected value.

    Args:
        app: Flask application instance used for setting up the test environment.

    Raises:
        AssertionError: If the response message, category, data, or status code
        does not match the expected output.
    """
    service = MemberService()

    response, status = service.create_member(
        first_name="Allan",
        last_name="Kim",
        family_id=1,
    )

    assert status == HTTPStatus.CREATED
    assert response['message'] == "Member created successfully"
    assert response['category'] == "success"
    assert response['data'] is not None

def test_create_member_error(app, monkeypatch):
    """
    Tests the behavior of the `create_member` method within the `MemberService` class
    when an exception is raised during the database `add` operation.

    This function mocks the `db.add` method to simulate a database error, invokes the
    `create_member` method, and asserts that the correct response and status code
    are returned when a failure occurs during member creation.

    Parameters
    ----------
    app : Any
        The application instance to be passed into the test context, if used.
    monkeypatch : MonkeyPatch
        A pytest fixture used to modify or simulate functionality during testing.

    Raises
    ------
    Exception
        When the mocked `db.add` method is called to simulate a database error.

    Returns
    -------
    None
    """
    service = MemberService()

    def mock_add(*args):
        raise Exception("Database error")

    # mock the database add method to simulate an error during member creation
    monkeypatch.setattr(service.db, "add", mock_add)

    response, status = service.create_member(
        first_name="Allan",
        last_name="Kim",
        family_id=1,
    )

    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response['message'] == "Error creating member"
    assert response['data'] is None

def test_get_member_siblings_not_found(session, test_user_1, test_member_1):
    """
    Tests that the `get_member_siblings` method of the `MemberService` returns the
    correct response when no siblings are found for the given member.

    Parameters:
    test_user_1: User
        The mock user object representing the current logged-in user in the test.
    test_member_1: Member
        The mock member object representing the member whose siblings are being
        requested.

    Raises:
    AssertionError
        If the returned status is not HTTPStatus.NOT_FOUND, or if the sibling's
        data in the response is not None.
    """
    # set current_user (test_user_1) to be in the same family as our member
    test_member_1.family.user_id = test_user_1.user_id
    session.commit()

    login_user(test_user_1)

    service = MemberService()
    response, status = service.get_member_siblings(test_member_1.member_id)
    siblings = response["data"]
    assert status == HTTPStatus.NOT_FOUND
    assert response["message"] == "No siblings found"
    assert siblings is None

def test_get_member_siblings(session, test_user_1, test_member_1, test_member_2, test_member_3):
    """
    Tests retrieval of siblings for a given member within the same family. This function verifies that members
    sharing the same father and mother are correctly identified and retrieved as siblings by the service.

    Arguments:
        session: Database session instance used for testing.
        test_user_1: User instance to represent the current logged-in user in the test.
        test_member_1: Member instance for which siblings will be retrieved.
        test_member_2: Member instance representing the first sibling.
        test_member_3: Member instance representing the second sibling.

    Raises:
        AssertionError: If the test conditions for verifying sibling's retrieval are not met.
    """
    # set current_user (test_user_1) to be in the same family as our members
    test_member_1.family.user_id = test_user_1.user_id

    login_user(test_user_1)
    # associate the members with same father(Member) and mother(Member) id to be siblings
    father_id, mother_id = 20, 30
    test_member_1.father, test_member_1.mother = father_id, mother_id
    test_member_2.father, test_member_2.mother = father_id, mother_id
    test_member_3.father, test_member_3.mother = father_id, mother_id
    session.commit()

    service = MemberService()
    response, status = service.get_member_siblings(test_member_1.member_id)
    siblings = response["data"]
    assert status == HTTPStatus.OK
    assert len(siblings) == 2
    assert test_member_2 in siblings
    assert test_member_3 in siblings

def test_get_member_siblings_error(session, test_user_1, test_member_1, test_member_2, test_member_3, monkeypatch):
    """
    Tests the behavior of the `get_member_siblings` method of the `MemberService` class
    when the database query for retrieving siblings raises an exception. This test ensures
    that the service properly handles errors during sibling retrieval and returns the
    appropriate response and status code.

    Args:
        session: The database session object used to manage changes and commits during
            testing.
        test_user_1: A predefined test user object that serves as the current logged-in
            user for the duration of the test.
        test_member_1: A predefined test member object whose siblings are to be retrieved
            in the test.
        test_member_2: A predefined test member object representing a sibling of
            `test_member_1`.
        test_member_3: A predefined test member object representing another sibling of
            `test_member_1`.
        monkeypatch: A pytest fixture that allows dynamic modification of attribute
            behavior to mock external dependencies.

    Raises:
        Exception: Simulates a database error during the siblings retrieval process.
    """
    # set current_user (test_user_1) to be in the same family as our members
    test_member_1.family.user_id = test_user_1.user_id

    login_user(test_user_1)
    # associate the members with same father(Member) and mother(Member) id to be siblings
    father_id, mother_id = 20, 30
    test_member_1.father, test_member_1.mother = father_id, mother_id
    test_member_2.father, test_member_2.mother = father_id, mother_id
    test_member_3.father, test_member_3.mother = father_id, mother_id
    session.commit()

    service = MemberService()

    def mock_get_member(*args):
        """simulates the get_member method of the MemberService class"""
        status = 200
        data = test_member_1
        return data, status

    # mock the get_member method to simulate a successful retrieval of a member (test_member_1)
    monkeypatch.setattr(service, "get_member", mock_get_member)

    def mock_query(*args):
        raise Exception("Database error")

    # mock the query method to simulate an error during siblings retrieval from the database
    monkeypatch.setattr(service.db, "query", mock_query)

    response, status = service.get_member_siblings(test_member_1.member_id)
    siblings = response["data"]
    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["message"] == "Error retrieving siblings"
    assert siblings is None
