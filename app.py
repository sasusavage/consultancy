import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from models import db, Lead, User

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'super_secret_key')

database_url = os.getenv('DATABASE_URL', 'sqlite:///comfort.db')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    from models import SiteContent
    content_list = SiteContent.query.all()
    content = {c.key: c.value for c in content_list}
    return render_template('index.html', content=content)

@app.route('/submit_lead', methods=['POST'])
def submit_lead():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    service = request.form.get('service')
    message = request.form.get('message', '')
    
    if not full_name or not email or not service:
        flash('Please fill out all required fields.', 'error')
        return redirect(url_for('index'))

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
                           service_filter=service_filter)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/edit_content', methods=['GET', 'POST'])
@login_required
def edit_content():
    from models import SiteContent
    if request.method == 'POST':
        # Handle text fields
        for key, val in request.form.items():
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

def create_admin_if_not_exists():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin', password=generate_password_hash('admin'))
            db.session.add(user)
            db.session.commit()

if __name__ == '__main__':
    create_admin_if_not_exists()
    app.run(debug=True, port=5007)
