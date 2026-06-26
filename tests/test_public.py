"""Public-facing routes: homepage, lead submission, validation, anti-spam."""
from app import db, Lead


def test_homepage_ok(client):
    r = client.get('/')
    assert r.status_code == 200
    assert b'app.css' in r.data


def test_submit_valid_lead(client, app):
    r = client.post('/submit_lead', data={
        'full_name': 'Acme Corp', 'email': 'ops@acme.com',
        'service': 'Logistics', 'message': 'hello',
    }, follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        assert Lead.query.filter_by(email='ops@acme.com').count() == 1


def test_reject_invalid_email(client, app):
    client.post('/submit_lead', data={
        'full_name': 'Bad', 'email': 'not-an-email', 'service': 'Logistics',
    }, follow_redirects=True)
    with app.app_context():
        assert Lead.query.filter_by(full_name='Bad').count() == 0


def test_reject_invalid_service(client, app):
    client.post('/submit_lead', data={
        'full_name': 'X', 'email': 'x@x.com', 'service': 'Hacking',
    }, follow_redirects=True)
    with app.app_context():
        assert Lead.query.filter_by(full_name='X').count() == 0


def test_missing_required_fields(client, app):
    client.post('/submit_lead', data={'full_name': 'NoEmail'}, follow_redirects=True)
    with app.app_context():
        assert Lead.query.filter_by(full_name='NoEmail').count() == 0


def test_honeypot_blocks_bot(client, app):
    client.post('/submit_lead', data={
        'full_name': 'Bot', 'email': 'bot@bot.com', 'service': 'Trade',
        'website': 'http://spam',
    }, follow_redirects=True)
    with app.app_context():
        assert Lead.query.filter_by(full_name='Bot').count() == 0


def test_404_page(client):
    r = client.get('/this-does-not-exist')
    assert r.status_code == 404
    assert b'404' in r.data
