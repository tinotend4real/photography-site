from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)

# ── CONFIG ────────────────────────────────────────────────────────────────────
app.config['SECRET_KEY'] = 'tino-photography-secret-2026-upgrade'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER']         = 'smtp.mail.me.com'
app.config['MAIL_PORT']           = 587
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USERNAME']       = 'tinotend4official@icloud.com'
app.config['MAIL_PASSWORD']       = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = ('TINO Photography', 'tinotend4official@icloud.com')

db   = SQLAlchemy(app)
mail = Mail(app)

# ── FLASK-LOGIN SETUP ──────────────────────────────────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id

# Admin credentials (CHANGE PASSWORD!)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # YOUR PERSONAL CREDENTIALS
        if username == 'tinotenda' and password == 'hillary2026':
            user = AdminUser(1)
            login_user(user)
            return redirect(url_for('admin'))
        flash('Wrong username or password')
    
    return render_template('admin_login.html')
# ── ADMIN ROUTES (NEW) ─────────────────────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'tino' and check_password_hash(ADMIN_PASSWORD_HASH, password):
            user = AdminUser(1)
            login_user(user)
            return redirect(url_for('admin'))
        flash('Wrong username or password')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

# ── YOUR EXISTING ROUTES (PROTECTED) ──────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# PROTECTED ADMIN DASHBOARD (your existing /admin)
@app.route('/admin')
@login_required
def admin():
    bookings = Booking.query.order_by(Booking.id.desc()).all()
    return render_template('admin.html', bookings=bookings)

@app.route('/admin/mark/<int:bid>/<status>')
@login_required
def mark(bid, status):
    b = Booking.query.get_or_404(bid)
    b.status = status
    db.session.commit()
    return jsonify({'ok': True})

# ── YOUR CONTACT FORM (UNCHANGED) ─────────────────────────────────────────────
@app.route('/submit', methods=['POST'])
def submit():
    data       = request.get_json()
    name       = data.get('name', '').strip()
    email      = data.get('email', '').strip()
    shoot_type = data.get('shoot_type', '').strip()
    message    = data.get('message', '').strip()

    if not all([name, email, shoot_type, message]):
        return jsonify({'success': False, 'error': 'All fields required'}), 400

    booking = Booking(name=name, email=email, shoot_type=shoot_type, message=message)
    db.session.add(booking)
    db.session.commit()

    try:
        msg = Message(
            subject=f'New Booking Enquiry — {shoot_type}',
            recipients=['tinotend4official@icloud.com'],
            reply_to=email,
            html=f"""
<div style="font-family:Arial,sans-serif;max-width:600px;background:#111111;color:#f5f0eb;padding:32px;border-top:4px solid #e8000d;">
  <h2 style="font-size:20px;letter-spacing:2px;text-transform
