"""CMS content editing and security (whitelist, CSRF, upload rules)."""
from app import db, allowed_file
from models import SiteContent


def test_cms_updates_whitelisted_key(auth_client, app):
    auth_client.post('/edit_content', data={'hero_title': 'Brand New Hero'})
    with app.app_context():
        item = SiteContent.query.filter_by(key='hero_title').first()
        assert item is not None and item.value == 'Brand New Hero'


def test_cms_ignores_non_whitelisted_key(auth_client, app):
    auth_client.post('/edit_content', data={
        'hero_title': 'ok', 'evil_key': 'should-not-be-saved',
    })
    with app.app_context():
        assert SiteContent.query.filter_by(key='evil_key').first() is None


def test_cms_requires_login(client):
    r = client.get('/edit_content')
    assert r.status_code == 302 and '/login' in r.headers['Location']


def test_upload_rejects_svg():
    # SVG excluded to prevent stored XSS
    assert allowed_file('logo.svg') is False
    assert allowed_file('photo.png') is True
    assert allowed_file('photo.jpeg') is True
    assert allowed_file('noextension') is False


def test_csrf_enforced_when_enabled(csrf_client):
    # POST without a token must be rejected
    r = csrf_client.post('/login', data={'username': 'admin', 'password': 'x'})
    assert r.status_code == 400
