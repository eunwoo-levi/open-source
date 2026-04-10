"""
conftest.py — Pytest fixtures for the Dev Journal Flask app.

TDD Lab: Human defines specs (test names & assertions),
         AI implements the fixtures and test body.
"""

import pytest
from app import app as flask_app, db as _db


@pytest.fixture(scope="session")
def app():
    """
    Session-scoped Flask application configured for testing.
    Uses an in-memory SQLite database so each test session is
    isolated from the production 'instance/journal.db'.
    """
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test-secret-key",
    )
    yield flask_app


@pytest.fixture(scope="function")
def client(app):
    """
    Function-scoped test client.
    Creates all tables before each test and drops them after,
    guaranteeing a clean database state for every test case.
    """
    with app.app_context():
        _db.create_all()
        yield app.test_client()
        _db.session.remove()
        _db.drop_all()
