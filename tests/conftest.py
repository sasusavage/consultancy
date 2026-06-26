"""Shared pytest fixtures.

Configures the app for isolated testing before importing it: an in-memory
SQLite database, a test secret key, and a known admin password.
"""
import os
import tempfile

# Must be set before `app` is imported, since app reads these at import time.
# A temp file DB (not :memory:) keeps state across connections/pools.
_db_fd, _db_path = tempfile.mkstemp(suffix='.db')
os.close(_db_fd)
os.environ.setdefault('DATABASE_URL', f'sqlite:///{_db_path}')
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('ADMIN_USERNAME', 'admin')
os.environ.setdefault('ADMIN_PASSWORD', 'test-admin-pass')

import pytest

from app import app as flask_app, db  # noqa: E402


@pytest.fixture
def app():
    flask_app.config.update(TESTING=True)
    yield flask_app


@pytest.fixture
def client(app):
    """A test client with CSRF disabled (CSRF is exercised separately)."""
    app.config['WTF_CSRF_ENABLED'] = False
    return app.test_client()


@pytest.fixture
def csrf_client(app):
    """A test client with CSRF protection enabled."""
    app.config['WTF_CSRF_ENABLED'] = True
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """A client already logged in as admin."""
    client.post('/login', data={'username': 'admin', 'password': 'test-admin-pass'})
    return client
