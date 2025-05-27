import pytest
from app import create_app
from app.extensions import db as _db
from config import TestConfig

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