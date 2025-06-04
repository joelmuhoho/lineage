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