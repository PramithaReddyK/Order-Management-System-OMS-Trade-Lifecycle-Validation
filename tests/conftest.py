"""
Pytest fixtures shared across all test suites.

DB isolation strategy: each test runs inside a savepoint that is rolled back
after the test completes, so the database is always clean.
"""
import os

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app import create_app
from app.models import Base
from tests.utils.api_client import OMSClient

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://oms_user:oms_pass@localhost:5432/oms_test",
)

# ---------------------------------------------------------------------------
# Engine / session fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Yields a session that wraps each test in a savepoint rollback."""
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    # Use nested transactions so each test gets a clean slate
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# App / HTTP fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def flask_app(db_engine):
    app = create_app(testing=True)
    app.config["DATABASE_URL"] = TEST_DATABASE_URL
    yield app


@pytest.fixture(scope="function")
def client(flask_app, db_session, monkeypatch):
    """Flask test client wired to the per-test DB session.

    Monkeypatches SessionLocal so before_request uses the transactional
    test session instead of opening a new connection to oms_db.
    """
    import app.db as db_module
    monkeypatch.setattr(db_module, "SessionLocal", lambda: db_session)

    with flask_app.test_client() as c:
        yield c


@pytest.fixture(scope="function")
def oms(client):
    return OMSClient(client)


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

@pytest.fixture
def new_order_payload():
    def _make(
        client_order_id="TEST-001",
        symbol="AAPL",
        side="BUY",
        quantity=100,
        order_type="LIMIT",
        price=150.00,
        **kwargs,
    ):
        payload = {
            "client_order_id": client_order_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "order_type": order_type,
        }
        if order_type == "LIMIT":
            payload["price"] = price
        payload.update(kwargs)
        return payload

    return _make


@pytest.fixture
def created_order(oms, new_order_payload):
    """Creates a single NEW order and returns its response body."""
    body, status = oms.create_order(new_order_payload())
    assert status == 201
    return body
