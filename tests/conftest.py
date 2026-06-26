"""Shared pytest fixtures.

Configures the app for isolated testing before importing it: a temp-file
SQLite database and a test secret key. The admin account is seeded directly
into the database (there is no admin password in the environment).
"""
import os
import tempfile

# Must be set before `app` is imported, since app reads these at import time.
# A temp file DB (not :memory:) keeps state across connections/pools.
_db_fd, _db_path = tempfile.mkstemp(suffix='.db')
os.close(_db_fd)
os.environ.setdefault('DATABASE_URL', f'sqlite:///{_db_path}')
os.environ.setdefault('SECRET_KEY', 'test-secret-key')

import pytest
from werkzeug.security import generate_password_hash

from app import app as flask_app, db, limiter  # noqa: E402
from models import User  # noqa: E402

ADMIN_PASSWORD = 'test-admin-pass'

# Rate limiting would otherwise make tests order-dependent (many /login calls
# across the suite trip the per-minute limit). Disable it for tests.
limiter.enabled = False


@pytest.fixture
def app():
    flask_app.config.update(TESTING=True)
    with flask_app.app_context():
        db.create_all()
        # Always reset the admin to a known password so tests are independent
        # of each other (e.g. the change-password tests).
        admin = User.query.filter_by(username='admin').first()
        if admin:
            admin.password = generate_password_hash(ADMIN_PASSWORD)
        else:
            db.session.add(User(username='admin',
                                password=generate_password_hash(ADMIN_PASSWORD)))
        db.session.commit()
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
    client.post('/login', data={'username': 'admin', 'password': ADMIN_PASSWORD})
    return client
