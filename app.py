from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from datetime import datetime
import os

app = Flask(__name__)

# ── CONFIG ─────────────────────────────────────────
app.config['SECRET_KEY'] = 'tino-photography-secret-2026-upgrade'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.mail.me.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tinotend4official@icloud.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = ('TINO Photography', 'tinotend4official@icloud.com')

db = SQLAlchemy(app)
mail = Mail(app)

# ── LOGIN SETUP ────────────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return AdminUser(user_id)

# ── DATABASE MODEL ─────────────────────────────────
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    shoot_type = db.Column(db.String(100))
    message = db.Column(db.Text)
    status = db.Column(db.String(50), default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ── ADMIN LOGIN ────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'tinotenda' and password == 'hillary2026':
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

# ── ROUTES ─────────────────────────────────────────
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

# ── ADMIN DASHBOARD ────────────────────────────────
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

# ── CONTACT FORM ───────────────────────────────────
@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    shoot_type = data.get('shoot_type', '').strip()
    message = data.get('message', '').strip()

    if not all([name, email, shoot_type, message]):
        return jsonify({'success': False, 'error': 'All fields required'}), 400

    booking = Booking(
        name=name,
        email=email,
        shoot_type=shoot_type,
        message=message
    )

    db.session.add(booking)
    db.session.commit()

    try:
        msg = Message(
            subject=f'New Booking Enquiry — {shoot_type}',
            recipients=['tinotend4official@icloud.com'],
            reply_to=email,
            html=f"""
<div style="font-family:Arial,sans-serif;max-width:600px;background:#111111;color:#f5f0eb;padding:32px;border-top:4px solid #e8000d;">
  <h2 style="font-size:20px;">New Booking Request</h2>
  <p><strong>Name:</strong> {name}</p>
  <p><strong>Email:</strong> {email}</p>
  <p><strong>Shoot Type:</strong> {shoot_type}</p>
  <p><strong>Message:</strong> {message}</p>
</div>
"""
        )
        mail.send(msg)
    except Exception as e:
        print("Mail error:", e)

    return jsonify({'success': True})

# ── RUN APP ────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
