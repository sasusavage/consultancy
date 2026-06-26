"""Change-password flow and the create-admin CLI command."""
from werkzeug.security import check_password_hash

from app import db
from models import User
from conftest import ADMIN_PASSWORD


def test_change_password_requires_login(client):
    r = client.get('/change_password')
    assert r.status_code == 302 and '/login' in r.headers['Location']


def test_change_password_wrong_current(auth_client):
    r = auth_client.post('/change_password', data={
        'current_password': 'nope', 'new_password': 'longenough1', 'confirm_password': 'longenough1',
    }, follow_redirects=True)
    assert b'current password is incorrect' in r.data


def test_change_password_mismatch(auth_client):
    r = auth_client.post('/change_password', data={
        'current_password': ADMIN_PASSWORD, 'new_password': 'longenough1', 'confirm_password': 'different1',
    }, follow_redirects=True)
    assert b'do not match' in r.data


def test_change_password_too_short(auth_client):
    r = auth_client.post('/change_password', data={
        'current_password': ADMIN_PASSWORD, 'new_password': 'short', 'confirm_password': 'short',
    }, follow_redirects=True)
    assert b'at least 8 characters' in r.data


def test_change_password_success(auth_client, app):
    new_pw = 'brand-new-pass-9'
    r = auth_client.post('/change_password', data={
        'current_password': ADMIN_PASSWORD, 'new_password': new_pw, 'confirm_password': new_pw,
    }, follow_redirects=True)
    assert b'Password updated successfully' in r.data
    with app.app_context():
        user = User.query.filter_by(username='admin').first()
        assert check_password_hash(user.password, new_pw)
        # restore so other tests using ADMIN_PASSWORD still pass
        from werkzeug.security import generate_password_hash
        user.password = generate_password_hash(ADMIN_PASSWORD)
        db.session.commit()


def test_no_admin_password_env_required(app):
    """App must import and run without ADMIN_PASSWORD in the environment."""
    import os
    assert 'ADMIN_PASSWORD' not in os.environ
