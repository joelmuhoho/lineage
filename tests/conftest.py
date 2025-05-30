import pytest
from app import create_app
from app.extensions import db as _db
from config import TestConfig
from app.models import Family, User, Event
from datetime import datetime


@pytest.fixture(scope='session')
def app():
    """
    Fixture that provides an application instance for testing.

    This fixture creates an application instance configured with
    the `TestConfig` settings for testing purposes. It also ensures
    the application context is appropriately managed during the
    test session.

    Yields:
        flask.Flask: The application instance configured for testing.
    """
    app = create_app(TestConfig)
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db(app):
    """
    This fixture sets up a database for use in tests. It initializes the database, creates all
    tables, provides a database connection for the session, and ensures proper cleanup by
    removing the session and dropping all tables.

    Args:
        app (Fixture): A fixture that initializes the application for the test session.

    Yields:
        _db (database instance): The initialized database instance for use during the session.
    """
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    """
    Fixture for providing a database session with transactional rollback.

    This pytest fixture provides a scoped database session that ensures
    all operations performed during a test are rolled back upon test completion.
    It creates a new connection and transaction for each test, binds the session
    to the transactional connection, and ensures cleanup is performed so that
    no database state persists across tests.

    Parameters:
        db (SQLAlchemy): The database instance to use for creating the session.

    Yields:
        SQLAlchemy Session: A session bound to the transaction, ensuring
        that any changes made during the test do not persist.

    """
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection)
    db.session.bind = connection
    yield db.session
    transaction.rollback()
    connection.close()
    db.session.remove()

@pytest.fixture
def test_family_1(session):
    """
    Fixture to create and manage a test Family object within a database session.

    This fixture is used to create a Family object with the name "Test Family 1",
    add it to the session, and commit the transaction. After yielding the
    Family object for testing purposes, the fixture ensures cleanup by
    removing the object from the database.

    Yields:
        Family: The Family object created and added to the session.
    """
    family = Family(name="Test Family 1")
    session.add(family)
    session.commit()
    yield family
    session.delete(family)
    session.commit()

@pytest.fixture
def test_family_2(session):
    """
    Fixture to provide a reusable Family object for testing purposes.

    This fixture creates a Family object with a predefined name and interacts with
    the provided session to persist it into the database before yielding. After
    yielding the Family object to the test, it ensures cleanup by removing the
    Family object from the database.

    Yields:
        Family: A Family object initialized with the name "Test Family 2".
    """
    family = Family(name="Test Family 2")
    session.add(family)
    session.commit()
    yield family
    session.delete(family)
    session.commit()

@pytest.fixture
def test_user_1(session):
    """
    Fixture for creating and managing temporary User object for testing purposes.

    This fixture sets up a test user, adds it to the session, commits the session, and yields
    the user object for use in test functions. After the test, it cleans up by deleting the
    user from the session and committing the session to persist its removal.

    Yields:
        User: A temporary User object created for testing.

    Parameters:
        session (Session): A database session used to interact with the database.
    """
    user = User(name="Test User 1", email="user1@mail.com", password="user1password")
    session.add(user)
    session.commit()
    yield user
    session.delete(user)
    session.commit()

@pytest.fixture
def test_user_2(session):
    """
    This function is a pytest fixture used to create and manage a test user in the test database session. It sets up a
    user, commits it to the session, and ensures proper cleanup after test execution.

    Yields:
        User: A User object instance created and added to the session.

    Args:
        session: The database session fixture.
    """
    user = User(name="Test User 2", email="user2@mail.com", password="user2password")
    session.add(user)
    session.commit()
    yield user
    session.delete(user)
    session.commit()

@pytest.fixture
def test_event_1(session, test_family_1):
    """
    Provides a test fixture for an event object meant for testing purposes.

    This fixture creates an Event object with predefined attributes, adds it
    to the session, and commits the changes to the database. After the test
    is completed, the fixture ensures cleanup by deleting the event object
    from the session and committing the session.

    Parameters:
        session: Session
            SQLAlchemy session object used to handle database interactions
            during the test.
        test_family_1: Family
            Predefined family object containing the necessary attributes
            required for creating the event.

    Yields:
        Event
            The event object created within this test fixture.

    This ensures that the database remains in a consistent and clean state
    during and after test execution.
    """
    event = Event(
        event_date=datetime(25, 4, 1),
        event_name="event_1",
        family_id=test_family_1.family_id
    )
    session.add(event)
    session.commit()
    yield event
    session.delete(event)
    session.commit()

@pytest.fixture
def test_user_and_family(test_user_1, test_family_1, session):
    """
    Provides a pytest fixture that associates a test user with a test family and prepares it
    for testing. This fixture establishes a relationship between the user and the family,
    ensures the relationship is saved in the session, and yields the test data.

    Args:
        test_user_1: The test user object that will be associated with a family.
        test_family_1: The test family object to associate with the test user.
        session: The database session used to commit changes.

    Yields:
        tuple: A tuple containing the test user and test family objects after the
        association is established and persisted.
    """
    test_user_1.families.append(test_family_1)
    session.commit()
    yield test_user_1, test_family_1

@pytest.fixture
def test_user_and_families(test_user_1, test_family_1, test_family_2, session):
    """
    Creates a test fixture that associates a user with multiple families and ensures
    these relationships are persisted correctly within a database session. The fixture
    yields the user and the associated families for use in tests.

    Parameters:
        test_user_1: The first test user object.
        test_family_1: The first test family object to be associated with the user.
        test_family_2: The second test family object to be associated with the user.
        session: A database session used to commit the changes.

    Yields:
        tuple: A tuple containing the updated user and the two associated families.
    """
    test_user_1.families.append(test_family_1)
    test_user_1.families.append(test_family_2)
    session.commit()
    yield test_user_1, test_family_1, test_family_2