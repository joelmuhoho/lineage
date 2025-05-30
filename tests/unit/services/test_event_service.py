import pytest
from app.models import User, Family, Event
from app.event.services import EventService
from datetime import datetime, timedelta
from flask_login import login_user
from unittest.mock import Mock

@pytest.fixture
def test_user_and_family(session):
    """
    Fixture to create and provide a test user and family object for testing purposes.

    This fixture creates a user with a specific name, email, and password, along with a
    family associated with the user. It adds these objects to the database session
    and commits the changes to make them persistent. The fixture ensures that the
    user and associated family are cleaned up and deleted after the test execution
    completes.

    Yields:
        tuple: A tuple containing the created user and family objects.
    """
    user = User(name="test-user", email="test@example.com", password="pass")
    session.add(user)
    session.commit()

    family = Family(name="Test Family", user_id=user.user_id)
    session.add(family)
    session.commit()

    user.families.append(family)
    session.commit()
    yield user, family

    session.delete(user)
    session.delete(family)
    session.commit()

def test_create_event(test_user_and_family):
    """
    Tests the creation of an event using the EventService class and verifies
    the response and status code for successful execution.

    Args:
        test_user_and_family (tuple): A tuple containing a mock user and their
            associated family for the test.

    Raises:
        AssertionError: If the response does not indicate success or the event
            data does not match the input parameters.
    """
    user, family = test_user_and_family
    service = EventService()

    event_date = (datetime.now() + timedelta(days=5))
    response, status = service.create_event(
        event_date=event_date,
        event_name="Test Event",
        family_id=family.family_id,
        location="Test Location",
        description="Test Description"
    )

    assert status == 201
    assert response["message"] == "Event created successfully"
    assert response["data"].event_name == "Test Event"

def test_create_event_error(test_user_and_family):
    """
    Tests the behavior of the `create_event` method in the `EventService` class
    when invalid input parameters are provided. Specifically, it checks how the
    method handles an attempt to create an event with a `None` event date.

    Parameters
    ----------
    test_user_and_family : tuple
        A tuple containing a user and a corresponding family instance, with
        a valid family_id used to test the event creation.

    Raises
    ------
    AssertionError
        If the status code returned by `create_event` is not 500, or if the
        response does not match the expected output for the error case.

    """
    user, family = test_user_and_family
    service = EventService()

    response, status = service.create_event(
        event_date=None, # pass a None event_date to raise an Exception
        event_name="Test Event",
        family_id=family.family_id,
        location="Test Location",
        description="Test Description"
    )

    assert status == 500
    assert response["message"] == "Error creating event"
    assert response["category"] == "danger"
    assert response["data"] is None

def test_get_upcoming_events(test_user_and_family):
    """
    Tests the retrieval of upcoming events for a family using the EventService class.

    The function verifies the ability of the service to correctly retrieve events
    occurring soon for a given family. It ensures that the event creation
    and retrieval mechanisms are functioning as expected.

    Parameters:
    test_user_and_family: tuple
        A tuple containing a user instance and a family instance, used for setting
        up test conditions.

    Raises:
    AssertionError
        If the expected conditions (such as correct status code or event details)
        are not met.
    """
    user, family = test_user_and_family
    service = EventService()

    upcoming_date = (datetime.now() + timedelta(days=2))
    service.create_event(upcoming_date, "Future Event", family.family_id, None, None)

    response, status = service.get_upcoming_events(family.family_id)
    assert status == 200
    assert response["message"] == "Upcoming events retrieved successfully"
    assert any(event.event_name == "Future Event" for event in response["data"])

def test_get_upcoming_events_not_found(test_user_and_family):
    """
    Tests the behavior of get_upcoming_events when no events are found.
    Verifies that appropriate 404 status and warning message are returned.

    Parameters:
        test_user_and_family: tuple
        A tuple containing test user and family instances.

    Raises:
        AssertionError
        If the status code is not 404 or if the response message is incorrect.
    """
    user, family = test_user_and_family
    service = EventService()

    response, status = service.get_upcoming_events(family.family_id)
    assert status == 404
    assert response["message"] == "No upcoming events found"
    assert response["category"] == "warning"
    assert response["data"] is None

def test_get_upcoming_events_error(test_user_and_family):
    """
    tests the behavior of the get_upcoming_events method when an error occurs while
    retrieving events for a given family.

    Parameters:
    user (User): A mock user object having relevant attributes.
    family (Family): A mock family object belonging to the user.

    Raises:
    Any exception occurring during a database query.

    Returns:
    None: Assertion methods are used to validate the function behavior.
    """
    user, family = test_user_and_family
    service = EventService()

    response, status = service.get_upcoming_events(family) # pass a family object instead of family_id to raise database Exception
    assert status == 500
    assert response["message"] == "Error retrieving upcoming events"
    assert response["category"] == "danger"
    assert response["data"] is None

def test_get_past_events(test_user_and_family):
    """
    This function tests whether the `get_past_events` method in `EventService` correctly
    retrieves events that occurred in the past for a specific family.

    Parameters:
    test_user_and_family (tuple): A test fixture containing a mock user and their
        associated family object.

    Raises:
    AssertionError: If the status code returned by `get_past_events` is not 200,
        if the success message in the response is incorrect, or if the event
        created with the name "Past Event" is not present in the returned event data.
    """
    user, family = test_user_and_family
    service = EventService()

    past_date = (datetime.now() - timedelta(days=2))
    service.create_event(past_date, "Past Event", family.family_id, None, None)

    response, status = service.get_past_events(family.family_id)
    assert status == 200
    assert response["message"] == "Past events retrieved successfully"
    assert any(event.event_name == "Past Event" for event in response["data"])

def test_get_past_events_not_found(test_user_and_family):
    """
    Tests the behavior of get_past_events when no events are found.
    Verifies that appropriate 404 status and warning message are returned.

    Parameters:
        test_user_and_family: tuple
        A tuple containing test user and family instances.

    Raises:
        AssertionError
        If the status code is not 404 or if the response message is incorrect.
    """
    user, family = test_user_and_family
    service = EventService()

    response, status = service.get_past_events(family.family_id)
    assert status == 404
    assert response["message"] == "No past events found"
    assert response["category"] == "warning"
    assert response["data"] is None

def test_get_past_events_error(test_user_and_family):
    """
    Tests the behavior of the `EventService.get_past_events` method when a database
    exception occurs. The test verifies that the appropriate error message, status,
    and response data are returned when the method fails.

    Args:
        test_user_and_family (tuple): A tuple containing a test user and their family
        object.
    """
    user, family = test_user_and_family
    service = EventService()

    response, status = service.get_past_events(family) # pass a family object instead of family_id to raise database Exception
    assert status == 500
    assert response["message"] == "Error retrieving past events"
    assert response["category"] == "danger"
    assert response["data"] is None

def test_event_belongs_to_current_user(session, test_user_and_family):
    """
    Tests whether an event is associated with a user's family.

    This function checks if the given event is linked to the family that
    belongs to a specific user. It creates a sample event, associates it
    with the test user's family, and verifies if the `event_belongs_to_current_user`
    method correctly identifies the event's association with the user.

    Parameters:
        session (Any): The database session used for adding and committing
        the test event.
        test_user_and_family (Tuple[User, Family]): A tuple containing the
        test user and their corresponding family.

    Raises:
        AssertionError: If the event does not belong to the current user's family
        as determined by the `event_belongs_to_current_user` method.
    """
    user, family = test_user_and_family
    event = Event(event_name="Sample", event_date=datetime.now(), family_id=family.family_id)
    session.add(event)
    session.commit()

    assert EventService.event_belongs_to_current_user(event, user)

def test_event_dont_belongs_to_current_user(session, test_user_and_family):
    """
    Tests whether the event does not belong to the current user.

    This function checks if a given event is not associated with the current user by
    verifying its family ID relation to the user's family.

    Parameters:
    session: Session
        The database session used to interact with the database.
    test_user_and_family: Tuple[User, Family]
        A tuple containing a user and their associated family to use in the test.

    Raises:
    AssertionError
        If the event is correctly associated with the current user.

    """
    user, _ = test_user_and_family
    event = Event(event_name="Sample", event_date=datetime.now(), family_id=7)
    session.add(event)
    session.commit()

    assert not EventService.event_belongs_to_current_user(event, user)

def test_update_event(test_user_and_family):
    """
    Tests the functionality of the EventService class, specifically the update_event method,
    to ensure it properly updates the details of an existing event created by a
    user belonging to a family. This involves validating that the response contains the
    updated field values and the appropriate success message.

    Parameters
    ----------
    test_user_and_family : tuple
        A tuple containing the test user and family object.

    Raises
    ------
    AssertionError
        If the HTTP status code is not 200, the response message is incorrect,
        or the updated event data does not match the expected values.
    """
    user, family = test_user_and_family
    service = EventService()

    response, status = service.create_event(
        event_date=datetime(2025, 6, 1),
        event_name="Original Name",
        location="Original Location",
        description="Original Description",
        family_id=family.family_id)
    event = response["data"]

    response, status = service.update_event(
        event,
        event_date=datetime(25,7, 1),
        event_name="Updated Name",
        location="Updated Location",
        description="Updated Description"
    )

    assert status == 200
    assert response["message"] == "Event updated successfully"
    assert response["data"].event_name == "Updated Name"
    assert response["data"].location == "Updated Location"
    assert response["data"].description == "Updated Description"
    assert response["data"].event_date == datetime(25, 7, 1)

def test_delete_event(app, test_user_and_family):
    """
    Tests the event deletion functionality provided by the EventService class.
    It ensures that an event can be created and subsequently deleted successfully.
    The test uses a logged-in user and verifies the response message and status.

    Parameters:
        app: Flask application for request context.
        test_user_and_family: Tuple containing test user and associated family.

    Raises:
        AssertionError: If the event deletion response does not meet the expected
                        success message or status.
    """
    user, family = test_user_and_family
    service = EventService()
    event_date = datetime.now()
    response = service.create_event(event_date, "Delete Me", family.family_id, None, None)
    event = response[0]["data"]

    with app.test_request_context():
        login_user(user)
        response, status = service.delete_an_event(event.event_id)
        assert status == 200
        assert response["message"] == "Event deleted successfully"

def test_delete_event_not_belong_to_user(app, test_user_and_family):
    """
    Test the deletion of an event that does not belong to the current user's family.

    This test ensures that a user cannot delete an event associated with a family
    that they are not a member of. It validates the proper handling of authorization
    by the `EventService` when an attempt is made to delete such an event.

    Parameters:
        app
            The Flask application instance.
        test_user_and_family
            A fixture providing a test user and their associated family.

    Raises:
        AssertionError: If the expected HTTP status or response message is not
        returned when attempting to delete an unauthorized event.
    """
    user, _ = test_user_and_family
    service = EventService()
    event_date = datetime.now()

    response = service.create_event(
        event_date=event_date,
        event_name="Delete Me",
        family_id=88,  # use family_id that does not belong to the current_user family
        description=None,
        location=None)
    event = response[0]["data"]

    with app.test_request_context():
        login_user(user)
        response, status = service.delete_an_event(event.event_id)
        assert status == 403
        assert response["message"] == "You are not authorized to delete this event"

def test_delete_event_error(app, test_user_and_family, monkeypatch):
    """
    Tests the behavior of the delete_event method in the EventService class when
    a database error occurs during the event deletion process. Ensures that the
    appropriate error handling mechanisms, such as rolling back the database and
    returning a meaningful error message, are executed as expected.

    Args:
        app (Flask): The Flask application instance used to create the request
            context.
        test_user_and_family (tuple): A tuple containing a test user and their
            associated family for use in the test. The first element is the user,
            and the second element is the family.
        monkeypatch (MonkeyPatch): A pytest fixture to dynamically modify or
            replace parts of the code during testing.

    Raises:
        Exception: Simulates a database deletion error in the test by
            triggering an exception in the mocked database object.
    """
    user, family = test_user_and_family
    service = EventService()

    response = service.create_event(
        event_date=datetime.now(),
        event_name="Delete Me",
        family_id=family.family_id,
        description=None,
        location=None
    )
    event = response[0]["data"]

    # a mock DB that raises an exception on delete
    mock_db = Mock()
    mock_db.delete.side_effect = Exception("Database error")
    mock_db.get.return_value = event  # Return the real event for the get_event call
    mock_db.rollback = Mock()  # Adding mock rollback method

    with app.test_request_context():
        login_user(user)
        # here we are replacing the entire db object with our mock
        monkeypatch.setattr(service, "db", mock_db)

        response, status = service.delete_an_event(event.event_id)

        assert status == 500
        assert response["message"] == "Error deleting event"
        assert response["category"] == "danger"
        assert response["data"] is None
        assert mock_db.rollback.called  # verifying the rollback was called
