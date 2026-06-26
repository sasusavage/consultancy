"""Authentication and admin lead-management operations."""
import pytest

from app import db, Lead


@pytest.fixture
def a_lead(app):
    with app.app_context():
        lead = Lead(full_name='Test Lead', email='t@test.com',
                    service='Logistics', status='New', message='hi')
        db.session.add(lead)
        db.session.commit()
        return lead.id


def test_admin_requires_login(client):
    r = client.get('/admin')
    assert r.status_code == 302
    assert '/login' in r.headers['Location']


def test_login_success(client):
    r = client.post('/login', data={'username': 'admin', 'password': 'test-admin-pass'})
    assert r.status_code == 302 and r.headers['Location'].endswith('/admin')


def test_login_bad_password(client):
    r = client.post('/login', data={'username': 'admin', 'password': 'wrong'},
                    follow_redirects=True)
    assert b'Invalid username or password' in r.data


def test_dashboard_lists_leads(auth_client, a_lead):
    r = auth_client.get('/admin')
    assert r.status_code == 200 and b'Test Lead' in r.data


def test_update_status(auth_client, a_lead, app):
    auth_client.post(f'/update_status/{a_lead}', data={'status': 'Qualified'})
    with app.app_context():
        assert db.session.get(Lead, a_lead).status == 'Qualified'


def test_api_update_status(auth_client, a_lead, app):
    r = auth_client.post(f'/api/update_status/{a_lead}', json={'status': 'Urgent'})
    assert r.status_code == 200 and r.get_json()['status'] == 'Urgent'
    with app.app_context():
        assert db.session.get(Lead, a_lead).status == 'Urgent'


def test_edit_lead(auth_client, a_lead, app):
    auth_client.post(f'/edit_lead/{a_lead}', data={
        'full_name': 'Renamed', 'email': 't@test.com',
        'service': 'Trade', 'status': 'New', 'message': 'x',
    })
    with app.app_context():
        assert db.session.get(Lead, a_lead).full_name == 'Renamed'


def test_delete_lead(auth_client, a_lead, app):
    auth_client.post(f'/delete_lead/{a_lead}')
    with app.app_context():
        assert db.session.get(Lead, a_lead) is None


def test_export_csv(auth_client, a_lead):
    r = auth_client.get('/export_leads')
    assert r.status_code == 200
    assert r.mimetype == 'text/csv'
    assert b'Test Lead' in r.data


def test_logout(auth_client):
    r = auth_client.get('/logout')
    assert r.status_code == 302
    # After logout, admin is protected again
    assert auth_client.get('/admin').status_code == 302
