import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from models import db, Lead, User

load_dotenv()

app = Flask(__name__)

# Secret key is required; fall back only in non-production/local dev.
secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    if os.getenv('FLASK_ENV') == 'production':
        raise RuntimeError("SECRET_KEY environment variable must be set in production.")
    secret_key = 'dev-only-insecure-key'
app.secret_key = secret_key

database_url = os.getenv('DATABASE_URL', 'sqlite:///comfort.db')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# CSRF protection for all POST forms
csrf = CSRFProtect(app)

# Rate limiting (in-memory by default; suitable for single-process deploys)
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=[])

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    from models import SiteContent
    content_list = SiteContent.query.all()
    content = {c.key: c.value for c in content_list}
    return render_template('index.html', content=content)

VALID_SERVICES = {'Consultancy', 'Logistics', 'Trade', 'Merchandise'}

@app.route('/submit_lead', methods=['POST'])
@limiter.limit("5 per minute; 30 per hour")
def submit_lead():
    full_name = (request.form.get('full_name') or '').strip()
    email = (request.form.get('email') or '').strip()
    service = (request.form.get('service') or '').strip()
    message = (request.form.get('message', '') or '').strip()

    # Honeypot: bots fill hidden fields humans never see.
    if request.form.get('website'):
        return redirect(url_for('index'))

    if not full_name or not email or not service:
        flash('Please fill out all required fields.', 'error')
        return redirect(url_for('index'))

    if not EMAIL_RE.match(email):
        flash('Please enter a valid email address.', 'error')
        return redirect(url_for('index'))

    if service not in VALID_SERVICES:
        flash('Please select a valid service.', 'error')
        return redirect(url_for('index'))

    full_name = full_name[:150]
    email = email[:150]
    message = message[:2000]

    lead = Lead(full_name=full_name, email=email, service=service, message=message)
    db.session.add(lead)
    db.session.commit()
    
    flash('Lead submitted successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search = request.args.get('search', '', type=str)
    service_filter = request.args.get('service', '', type=str)

    query = Lead.query

    if search:
        query = query.filter(
            db.or_(
                Lead.full_name.ilike(f'%{search}%'),
                Lead.email.ilike(f'%{search}%')
            )
        )

    if service_filter:
        query = query.filter_by(service=service_filter)

    total_leads = Lead.query.count()
    new_leads = Lead.query.filter_by(status='New').count()
    urgent_leads = Lead.query.filter_by(status='Urgent').count()

    filtered_count = query.count()
    total_pages = max(1, (filtered_count + per_page - 1) // per_page)
    page = min(page, total_pages)

    recent_leads = query.order_by(Lead.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    all_leads_board = query.order_by(Lead.created_at.desc()).limit(200).all()

    start_num = (page - 1) * per_page + 1
    end_num = min(page * per_page, filtered_count)

    return render_template('leads_management.html',
                           total_leads=total_leads,
                           new_leads=new_leads,
                           urgent_leads=urgent_leads,
                           recent_leads=recent_leads,
                           filtered_count=filtered_count,
                           page=page,
                           total_pages=total_pages,
                           start_num=start_num,
                           end_num=end_num,
                           search=search,
                           service_filter=service_filter,
                           all_leads_board=all_leads_board)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# SVG intentionally excluded: it can carry embedded JavaScript (stored XSS).
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Only these keys may be written to SiteContent via the CMS editor.
ALLOWED_CONTENT_KEYS = {
    # Hero
    'hero_title', 'hero_subtitle',
    # Four Pillars
    'pillars_heading', 'pillars_subheading',
    'pillar1_title', 'pillar1_text',
    'pillar2_title', 'pillar2_text',
    'pillar3_title', 'pillar3_text',
    'pillar4_title', 'pillar4_text',
    # About + stats
    'about_heading', 'about_text', 'about_quote',
    'stat1_value', 'stat1_label',
    'stat2_value', 'stat2_label',
    'stat3_value', 'stat3_label',
    # Service deep dives
    'dive1_label', 'dive1_title', 'dive1_text',
    'dive1_bullet1', 'dive1_bullet2', 'dive1_bullet3',
    'dive2_label', 'dive2_title', 'dive2_text',
    'dive2_bullet1', 'dive2_bullet2', 'dive2_bullet3',
    # Testimonials (Trusted Excellence)
    'testimonials_heading', 'testimonials_subheading',
    'testimonial1_text', 'testimonial1_name', 'testimonial1_role',
    'testimonial2_text', 'testimonial2_name', 'testimonial2_role',
    'testimonial3_text', 'testimonial3_name', 'testimonial3_role',
    # Reviews
    'reviews_heading',
    'review1_author', 'review1_text',
    'review2_author', 'review2_text',
    'review3_author', 'review3_text',
    # Contact
    'contact_heading', 'contact_subheading',
    'contact_email', 'contact_phone',
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/edit_content', methods=['GET', 'POST'])
@login_required
def edit_content():
    from models import SiteContent
    if request.method == 'POST':
        # Handle text fields (only whitelisted keys)
        for key, val in request.form.items():
            if key not in ALLOWED_CONTENT_KEYS:
                continue
            if val is not None and val.strip() != "":
                item = SiteContent.query.filter_by(key=key).first()
                if item:
                    item.value = val
                else:
                    item = SiteContent(key=key, value=val)
                    db.session.add(item)

        # Handle image uploads
        image_fields = ['hero_image', 'about_image', 'strategy_image', 'logistics_image']
        for field in image_fields:
            file = request.files.get(field)
            if file and file.filename and allowed_file(file.filename):
                from werkzeug.utils import secure_filename
                import uuid
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{field}_{uuid.uuid4().hex[:8]}.{ext}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                url = f"/static/uploads/{filename}"
                item = SiteContent.query.filter_by(key=field).first()
                if item:
                    item.value = url
                else:
                    item = SiteContent(key=field, value=url)
                    db.session.add(item)

        db.session.commit()
        flash('Homepage content updated.', 'success')
        return redirect(url_for('edit_content'))

    content_list = SiteContent.query.all()
    content = {c.key: c.value for c in content_list}
    return render_template('edit_content.html', content=content)

@app.route('/update_status/<int:id>', methods=['POST'])
@login_required
def update_status(id):
    lead = Lead.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status:
        lead.status = new_status
        db.session.commit()
        flash('Status updated.', 'success')
    return redirect(url_for('admin_dashboard'))

import csv
from io import StringIO
from flask import Response

@app.route('/export_leads')
@login_required
def export_leads():
    search = request.args.get('search', '', type=str)
    service_filter = request.args.get('service', '', type=str)
    query = Lead.query
    if search:
        query = query.filter(db.or_(Lead.full_name.ilike(f'%{search}%'), Lead.email.ilike(f'%{search}%')))
    if service_filter:
        query = query.filter_by(service=service_filter)

    leads = query.order_by(Lead.created_at.desc()).all()

    def generate():
        data = StringIO()
        writer = csv.writer(data)
        writer.writerow(['ID', 'Name', 'Email', 'Service', 'Status', 'Date', 'Message'])
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)
        for lead in leads:
            writer.writerow([
                lead.id, lead.full_name, lead.email, lead.service, lead.status, 
                lead.created_at.strftime('%Y-%m-%d %H:%M:%S'), 
                lead.message.replace('\r', '').replace('\n', ' ') if lead.message else ''
            ])
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=leads_export.csv"})

@app.route('/api/update_status/<int:id>', methods=['POST'])
@login_required
def api_update_status(id):
    lead = Lead.query.get_or_404(id)
    data = request.get_json()
    new_status = data.get('status')
    if new_status:
        lead.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'status': new_status})
    return jsonify({'success': False}), 400

@app.route('/edit_lead/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_lead(id):
    lead = Lead.query.get_or_404(id)
    if request.method == 'POST':
        lead.full_name = request.form.get('full_name')
        lead.email = request.form.get('email')
        lead.service = request.form.get('service')
        lead.status = request.form.get('status')
        lead.message = request.form.get('message', '')
        db.session.commit()
        flash('Lead updated successfully.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_lead.html', lead=lead)

@app.route('/delete_lead/<int:id>', methods=['POST'])
@login_required
def delete_lead(id):
    lead = Lead.query.get_or_404(id)
    db.session.delete(lead)
    db.session.commit()
    flash('Lead deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute; 50 per hour", methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current = request.form.get('current_password', '')
        new = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')

        if not check_password_hash(current_user.password, current):
            flash('Your current password is incorrect.', 'error')
        elif len(new) < 8:
            flash('New password must be at least 8 characters.', 'error')
        elif new != confirm:
            flash('New passwords do not match.', 'error')
        else:
            current_user.password = generate_password_hash(new)
            db.session.commit()
            flash('Password updated successfully.', 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('change_password.html')

@app.errorhandler(400)
def bad_request(e):
    return render_template('error.html', code=400, title='Bad Request',
                           message="Your request couldn't be processed. This can happen if a "
                                   "form session expired — please go back and try again."), 400

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, title='Forbidden',
                           message="You don't have permission to access this page."), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, title='Page Not Found',
                           message="The page you're looking for doesn't exist or has moved."), 404

@app.errorhandler(429)
def too_many_requests(e):
    return render_template('error.html', code=429, title='Too Many Requests',
                           message="You're doing that too often. Please wait a moment and try again."), 429

@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    return render_template('error.html', code=500, title='Something Went Wrong',
                           message="An unexpected error occurred on our end. Please try again later."), 500


def ensure_tables():
    """Create tables if they don't exist yet (convenience for first boot).

    Schema is otherwise owned by Alembic migrations (`flask db upgrade`).
    Admin accounts are NOT created here — there is no password in the
    environment. Create the first admin with `flask create-admin`.
    """
    with app.app_context():
        from sqlalchemy import inspect
        if not inspect(db.engine).has_table(User.__tablename__):
            db.create_all()


import click


@app.cli.command('create-admin')
@click.option('--username', prompt='Username', default='admin', show_default=True)
@click.option('--password', prompt='Password', hide_input=True,
              confirmation_prompt=True)
def create_admin_command(username, password):
    """Create or update an admin user.

    Interactive:   flask create-admin
    Scripted:      flask create-admin --username admin --password 'secret'

    The password is hashed and stored only in the database.
    """
    username = (username or '').strip() or 'admin'
    if not password:
        click.echo('[ERROR] Password cannot be empty.')
        return
    user = User.query.filter_by(username=username).first()
    if user:
        user.password = generate_password_hash(password)
        db.session.commit()
        click.echo(f"[OK] Password updated for existing user '{username}'.")
    else:
        db.session.add(User(username=username, password=generate_password_hash(password)))
        db.session.commit()
        click.echo(f"[OK] Admin user '{username}' created.")


# Ensure tables exist whether run locally or via Gunicorn. Skipped during
# `flask db ...` migration commands so Alembic can manage the schema cleanly.
# Wrapped so a transient DB outage at boot doesn't crash the web process
# (which would otherwise trigger a container restart loop).
if os.getenv('SKIP_BOOTSTRAP') != '1':
    try:
        ensure_tables()
    except Exception as exc:  # noqa: BLE001
        app.logger.error("Startup DB bootstrap failed (continuing): %s", exc)

if __name__ == '__main__':
    app.run(debug=True, port=5007)
