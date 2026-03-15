from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import os

app = Flask(__name__)

# ── CONFIG ────────────────────────────────────────────────────────────────────
app.config['SECRET_KEY'] = 'tino-photography-secret'
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

# ── DATABASE MODEL ─────────────────────────────────────────────────────────────
class Booking(db.Model):
    id         = db.Column(db.Integer,     primary_key=True)
    name       = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(120), nullable=False)
    shoot_type = db.Column(db.String(80),  nullable=False)
    message    = db.Column(db.Text,        nullable=False)
    date       = db.Column(db.String(40),  default=lambda: datetime.now().strftime('%d %b %Y, %H:%M'))
    status     = db.Column(db.String(20),  default='new')

# ── ROUTES ─────────────────────────────────────────────────────────────────────
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

@app.route('/admin')
def admin():
    bookings = Booking.query.order_by(Booking.id.desc()).all()
    return render_template('admin.html', bookings=bookings)

@app.route('/admin/mark/<int:bid>/<status>')
def mark(bid, status):
    b = Booking.query.get_or_404(bid)
    b.status = status
    db.session.commit()
    return jsonify({'ok': True})

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
  <h2 style="font-size:20px;letter-spacing:2px;text-transform:uppercase;margin-bottom:24px;">New Booking Enquiry</h2>
  <table style="width:100%;border-collapse:collapse;">
    <tr><td style="padding:10px 0;color:#888888;width:110px;">Name</td><td style="padding:10px 0;font-weight:bold;">{name}</td></tr>
    <tr><td style="padding:10px 0;color:#888888;">Email</td><td style="padding:10px 0;"><a href="mailto:{email}" style="color:#e8000d;">{email}</a></td></tr>
    <tr><td style="padding:10px 0;color:#888888;">Shoot Type</td><td style="padding:10px 0;">{shoot_type}</td></tr>
    <tr><td style="padding:10px 0;color:#888888;vertical-align:top;">Message</td><td style="padding:10px 0;">{message}</td></tr>
  </table>
  <p style="margin-top:24px;font-size:12px;color:#555555;">Reply directly to this email to respond to {name}.</p>
</div>"""
        )
        mail.send(msg)
    except Exception as ex:
        print(f'[MAIL ERROR] {ex}')

    return jsonify({'success': True})

# ── INIT & RUN ─────────────────────────────────────────────────────────────────
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
