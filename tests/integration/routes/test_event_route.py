from datetime import datetime
from http import HTTPStatus
from app.models.event import Event
from app.event.services import EventService
from app.services.service_base import service_response
from flask import url_for

def login_test_user_1(client, test_user_1):
    """
    Logs a test user into the application using the provided client and credentials.

    Parameters:
    client : Any
        The test client used to simulate HTTP requests to the application.
    test_user_1 : Any
        An object representing the first test user with an email attribute.

    Returns:
    Any
        The HTTP response object resulting from the login POST request.
    """
    return client.post(url_for("auth.login"), data={"email": test_user_1.email, "password": "user1password"})

def test_add_event_get_user_no_family(client, test_user_1):
    """
    Tests adding an event when the user does not belong to any family.

    This test ensures that a user who attempts to access the event
    creation page without being part of a family is properly redirected
    and notified that at least one family is required to add an event.
    Additionally, it verifies that the response includes a prompt
    to create a family.

    Parameters:
    client :
        A test client instance for simulating HTTP requests to the
        application.
    test_user_1 :
        The test user for this scenario, which logs in before
        attempting to view the event page.
    """
    login_test_user_1(client, test_user_1)
    response = client.get(url_for("event.add_event"), follow_redirects=True)

    assert response.status_code == 200
    assert b"At least one family is required to add an event" in response.data
    assert b"Create Family" in response.data

def test_add_event_get(client, test_user_and_family):
    """
    Tests the 'add_event' functionality by verifying that the 'Add Event'
    page is accessible for a logged-in user and returns the expected
    response content.

    Arguments:
        client: A test client instance used for making requests in a controlled
        testing environment.
        test_user_and_family: A fixture that returns a tuple containing a test
        user and their associated family.

    Raises:
        AssertionError: If the status code of the response is not 200 or if the
        response data does not include the expected text "Add Event".
    """
    user, family = test_user_and_family
    family.user_id = user.user_id
    login_test_user_1(client, user)

    response = client.get(url_for("event.add_event"), follow_redirects=True)

    assert response.status_code == 200
    assert b"Add Event" in response.data

def test_add_event_post(client, app, session, test_user_and_family):
    """
    Tests the creation of an event through a POST request to the event endpoint.

    The function simulates the process of creating a new event in a web application,
    ensuring that the event creation functionality works as expected and that the
    database updates correctly with the new event data.

    Parameters:
    client : flask.testing.FlaskClient
        The Flask test client used to simulate HTTP requests to the application.
    app : flask.Flask
        The Flask application instance used for testing.
    session : sqlalchemy.orm.session.Session
        The SQLAlchemy session object used to interact with the database during tests.
    test_user_and_family : Tuple[User, Family]
        A tuple containing a test user instance and associated family instance for testing.

    Raises:
    AssertionError
        If the response status code does not match the expected value, or the required content
        is not present in the response data, or the event is not properly persisted in the database.
    """
    user, family = test_user_and_family
    family.user_id = user.user_id
    login_test_user_1(client, user)

    event_data = {
        "name": "Test Event",
        "date": datetime(2025, 12, 25),
        "family": family.family_id,
        "description": "Test Description",
        "location": "Test Location"
    }
    response = client.post(url_for("event.add_event"), data=event_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Event created successfully" in response.data
    assert b"Test Event" in response.data

    with app.app_context():
        assert session.query(Event).count() == 1

def test_add_event_post_error(client, app, session, test_user_and_family, monkeypatch):
    """
    Tests the behavior of adding an event when an error occurs during the event
    creation service call.

    Parameters:
    client
        Flask test client used to simulate HTTP requests.
    app
        Flask application fixture to manage application context.
    session
        Database session fixture for querying and committing transactions.
    test_user_and_family
        Tuple containing a test user object and a corresponding test family
        object.
    monkeypatch
        pytest's monkeypatching utility for mocking functions or methods.

    Raises:
    AssertionError
        Raised if the test assertions fail.

    This test verifies the following:
    - When the `create_event` method in `EventService` returns an error response,
      the system displays an appropriate error message on the response page.
    - No new event record is created in the database when an error occurs during
      the event creation process.
    """
    user, family = test_user_and_family
    family.user_id = user.user_id
    login_test_user_1(client, user)

    def mock_create_event(*args, **kwargs):
        return service_response(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "Error creating event",
            "danger",
            None
        )
    monkeypatch.setattr(EventService, "create_event", mock_create_event)

    event_data = {
        "name": "Test Event",
        "date": datetime(2025, 12, 25),
        "family": family.family_id,
        "description": "Test Description",
        "location": "Test Location"
    }
    response = client.post(url_for("event.add_event"), data=event_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Error creating event" in response.data
    assert b"Add Event" in response.data

    with app.app_context():
        assert session.query(Event).count() == 0

def test_get_events_no_events(client, test_user_and_family):
    """
    Tests the behavior of the 'get_events' endpoint when no events are present for
    a family. It checks that the correct message is displayed for both upcoming
    and past events when the events list is empty.

    Args:
        client: A Flask test client used to simulate HTTP requests in the test.
        test_user_and_family: A fixture providing a test user and their
            associated family for testing purposes.

    Raises:
        AssertionError: If the test conditions are not met.

    Test Conditions:
    - Verifies that the response status code is 200.
    - Checks if the message "No Upcoming Event at the moment" is present in the
      response when no upcoming events exist.
    - Checks if the message "No Past Event at the moment" is present in the
      response when no past events exist.
    """
    user, family = test_user_and_family
    login_test_user_1(client, user)

    response = client.get(url_for("event.get_events", family_id=family.family_id), follow_redirects=True)

    assert response.status_code == 200
    assert b"No Upcoming Event at the moment" in response.data
    assert b"No Past Event at the moment" in response.data

def test_get_events(client, test_user_and_family, test_event_1):
    """
    This function tests the behavior of retrieving events associated with a family ID
    after authenticating a test user. It ensures the correct response status code is
    returned and verifies the presence of specific event data in the response.

    Args:
        client: A test client instance used to simulate HTTP requests within the
            test environment.
        test_user_and_family: A fixture providing a test user and their associated
            family setup for the test case.
        test_event_1: A fixture representing a test event to be linked to the
            family's ID during the test.

    Raises:
        AssertionError: If the expected status code or event data is not found
            in the response.
    """
    user, family = test_user_and_family
    test_event_1.family_id = family.family_id
    login_test_user_1(client, user)

    response = client.get(url_for("event.get_events", family_id=family.family_id), follow_redirects=True)

    assert response.status_code == 200
    assert b"event_1" in response.data

def test_delete_event(client, session, app, test_user_and_family, test_event_1):
    """
    Tests the deletion of an event associated with a family and verifies that the event
    is removed from the database and that the appropriate success message is displayed.

    Parameters:
        client: The test client used to simulate HTTP requests.
        session: The database session used for querying and managing data integrity.
        app: The Flask application instance providing the application context.
        test_user_and_family: A fixture returning a test user and their associated family.
        test_event_1: A fixture providing a test event object.

    Raises:
        AssertionError: If the event deletion operation or related conditions fail.
    """
    user, family = test_user_and_family
    test_event_1.family_id = family.family_id
    login_test_user_1(client, user)

    # before deletion assert event exists
    with app.app_context():
        assert session.query(Event).count() == 1

    response = client.post(url_for("event.delete_event", event_id=test_event_1.event_id), follow_redirects=True)

    assert response.status_code == 200
    assert b"Event deleted successfully" in response.data

    # assert event does not exist after deletion
    with app.app_context():
        assert session.query(Event).count() == 0

def test_delete_event_error(client, session, app, test_user_and_family, test_event_1, monkeypatch):
    """
    Test the behavior of event deletion when an error occurs in the service layer.

    This function simulates the scenario where a user tries to delete an event, but the
    deletion fails due to an internal server error. It verifies that the event remains
    intact in the database and proper error messages are displayed to the user.

    Parameters:
        client: FlaskClient
            The testing client is used to simulate HTTP requests during tests.
        session: Session
            The SQLAlchemy session to query and manipulate the database.
        app: Flask
            The Flask application instance used during test execution.
        test_user_and_family: Tuple[User, Family]
            A tuple containing the test user and their corresponding family.
        test_event_1: Event
            The event instance representing the test event to be deleted.
        monkeypatch: MonkeyPatch
            An object used to modify or replace attributes and functions during testing.

    Raises:
        AssertionError: If any assertion regarding HTTP response, error message, or
            event existence in the database fails.
    """
    user, family = test_user_and_family
    test_event_1.family_id = family.family_id
    login_test_user_1(client, user)

    # before deletion assert event exists
    with app.app_context():
        assert session.query(Event).count() == 1

    def mock_delete_an_event(*args, **kwargs):
        return service_response(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "Error deleting event",
            "danger",
            None
        )
    monkeypatch.setattr(EventService, "delete_an_event", mock_delete_an_event)

    response = client.post(url_for("event.delete_event", event_id=test_event_1.event_id), follow_redirects=True)

    assert response.status_code == 200
    assert b"Error deleting event" in response.data
    assert b"event_1" in response.data

    # assert event still exists after an error in deletion
    with app.app_context():
        assert session.query(Event).count() == 1

    monkeypatch.undo()