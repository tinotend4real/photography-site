from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import os
import json
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# ── CONFIG ─────────────────────────────────────────────────────────────────────
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tino-photography-secret-2026-upgrade')

# ── DATABASE ───────────────────────────────────────────────────────────────────
database_url = os.environ.get('DATABASE_URL', 'sqlite:///tino.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# ── MAIL ───────────────────────────────────────────────────────────────────────
app.config['MAIL_SERVER']         = 'smtp.mail.me.com'
app.config['MAIL_PORT']           = 587
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USERNAME']       = 'tinotend4official@icloud.com'
app.config['MAIL_PASSWORD']       = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = ('TINO Photography', 'tinotend4official@icloud.com')

# ── CLOUDINARY ─────────────────────────────────────────────────────────────────
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dpnv6wqth'),
    api_key    = os.environ.get('CLOUDINARY_API_KEY',    '659647557914374'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET', 'wo0_XC_dqLW730Wh-qFuWObA13M')
)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'jfif', 'webp'}

db   = SQLAlchemy(app)
mail = Mail(app)

# ── LOGIN ───────────────────────────────────────────────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return AdminUser(user_id)

# ── MODELS ──────────────────────────────────────────────────────────────────────
class Booking(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100))
    email      = db.Column(db.String(100))
    shoot_type = db.Column(db.String(100))
    message    = db.Column(db.Text)
    status     = db.Column(db.String(50), default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Photo(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    filename    = db.Column(db.String(200), unique=True)
    url         = db.Column(db.Text)
    title       = db.Column(db.String(200))
    category    = db.Column(db.String(100))
    featured    = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Note(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    content    = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class PageView(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    page       = db.Column(db.String(100))
    visited_at = db.Column(db.DateTime, default=datetime.utcnow)

class SiteSettings(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    key   = db.Column(db.String(100), unique=True)
    value = db.Column(db.Text)

class BlogPost(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(200))
    slug         = db.Column(db.String(200), unique=True)
    body         = db.Column(db.Text)
    cover_url    = db.Column(db.Text)
    category     = db.Column(db.String(100), default='general')
    published    = db.Column(db.Boolean, default=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow)

# ── CREATE TABLES ───────────────────────────────────────────────────────────────
with app.app_context():
    db.create_all()

# ── HELPERS ─────────────────────────────────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def track(page):
    try:
        db.session.add(PageView(page=page))
        db.session.commit()
    except:
        db.session.rollback()

def get_setting(key, default=''):
    try:
        s = SiteSettings.query.filter_by(key=key).first()
        return s.value if s else default
    except:
        return default

def set_setting(key, value):
    try:
        s = SiteSettings.query.filter_by(key=key).first()
        if s:
            s.value = value
        else:
            db.session.add(SiteSettings(key=key, value=value))
        db.session.commit()
    except:
        db.session.rollback()

def slugify(text):
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text

# ── PUBLIC ROUTES ───────────────────────────────────────────────────────────────
@app.route('/')
def index():
    track('home')
    featured = Photo.query.filter_by(featured=True).order_by(Photo.uploaded_at.desc()).all()
    latest_posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).limit(3).all()
    return render_template('index.html', featured=featured, latest_posts=latest_posts)

@app.route('/portfolio')
def portfolio():
    track('portfolio')
    photos = Photo.query.order_by(Photo.uploaded_at.desc()).all()
    return render_template('portfolio.html', photos=photos)

@app.route('/services')
def services():
    track('services')
    return render_template('services.html')

@app.route('/about')
def about():
    track('about')
    about_settings = {
        'about_name':     get_setting('about_name',     'Tino'),
        'about_location': get_setting('about_location', 'Nottingham'),
        'about_bio1':     get_setting('about_bio1',     "I didn't start photography because I wanted to be a photographer. I started because I kept seeing moments that deserved to be remembered properly."),
        'about_bio2':     get_setting('about_bio2',     "Six months ago I picked up a camera for the first time. No course, no mentor, no plan. Just me figuring it out, shot by shot."),
        'about_bio3':     get_setting('about_bio3',     "I'm based in Nottingham and I shoot everything."),
        'about_bio4':     get_setting('about_bio4',     "What drives me is the idea that every scene has a version of itself that most people walk past."),
        'about_bio5':     get_setting('about_bio5',     "Six months in. A lot more to come."),
        'about_photo':    get_setting('about_photo',    ''),
        'about_months':   get_setting('about_months',   '6'),
        'about_stat1_n':  get_setting('about_stat1_n',  '40+'),
        'about_stat1_l':  get_setting('about_stat1_l',  'Shots in Portfolio'),
        'about_stat2_n':  get_setting('about_stat2_n',  '5+'),
        'about_stat2_l':  get_setting('about_stat2_l',  'Categories'),
        'about_stat3_n':  get_setting('about_stat3_n',  '24h'),
        'about_stat3_l':  get_setting('about_stat3_l',  'Turnaround'),
    }
    return render_template('about.html', s=about_settings)

@app.route('/contact')
def contact():
    track('contact')
    return render_template('contact.html')

@app.route('/blog')
def blog():
    track('blog')
    posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/blog/<slug>')
def blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template('blog_post.html', post=post)

# ── SECRET LOGIN ────────────────────────────────────────────────────────────────
@app.route('/backstage')
def backstage():
    return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'tinotenda' and password == 'hillary2026':
            login_user(AdminUser(1))
            return redirect(url_for('admin'))
        flash('Wrong username or password')
    return render_template('admin_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

# ── ADMIN DASHBOARD ─────────────────────────────────────────────────────────────
@app.route('/admin')
@login_required
def admin():
    try:
        bookings  = Booking.query.order_by(Booking.id.desc()).all()
        photos    = Photo.query.order_by(Photo.uploaded_at.desc()).all()
        notes     = Note.query.order_by(Note.updated_at.desc()).all()
        posts     = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    except:
        db.session.rollback()
        bookings, photos, notes, posts = [], [], [], []

    settings = {
        'hero_title':      get_setting('hero_title',      'The Art of Real Shots.'),
        'hero_subtitle':   get_setting('hero_subtitle',   'Portraits, street, fashion, food & events across Nottingham.'),
        'taking_bookings': get_setting('taking_bookings', 'yes'),
        'instagram':       get_setting('instagram',       'https://www.instagram.com/tino4_real'),
        'tiktok':          get_setting('tiktok',          'https://www.tiktok.com/@tino4real._'),
        'location':        get_setting('location',        'Nottingham, UK'),
        'about_name':      get_setting('about_name',      'Tino'),
        'about_location':  get_setting('about_location',  'Nottingham'),
        'about_bio1':      get_setting('about_bio1',      ''),
        'about_bio2':      get_setting('about_bio2',      ''),
        'about_bio3':      get_setting('about_bio3',      ''),
        'about_bio4':      get_setting('about_bio4',      ''),
        'about_bio5':      get_setting('about_bio5',      ''),
        'about_photo':     get_setting('about_photo',     ''),
        'about_months':    get_setting('about_months',    '6'),
        'about_stat1_n':   get_setting('about_stat1_n',   '40+'),
        'about_stat1_l':   get_setting('about_stat1_l',   'Shots in Portfolio'),
        'about_stat2_n':   get_setting('about_stat2_n',   '5+'),
        'about_stat2_l':   get_setting('about_stat2_l',   'Categories'),
        'about_stat3_n':   get_setting('about_stat3_n',   '24h'),
        'about_stat3_l':   get_setting('about_stat3_l',   'Turnaround'),
    }

    try:
        total_views = PageView.query.count()
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_views = PageView.query.filter(PageView.visited_at >= today_start).count()
        week_views  = PageView.query.filter(
            PageView.visited_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        page_counts = {}
        for pv in PageView.query.all():
            page_counts[pv.page] = page_counts.get(pv.page, 0) + 1
        chart_labels, chart_data = [], []
        for i in range(6, -1, -1):
            day       = datetime.utcnow() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end   = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            count     = PageView.query.filter(
                PageView.visited_at >= day_start,
                PageView.visited_at <= day_end
            ).count()
            chart_labels.append(day.strftime('%a'))
            chart_data.append(count)
    except:
        db.session.rollback()
        total_views, today_views, week_views = 0, 0, 0
        page_counts, chart_labels, chart_data = {}, [], []

    analytics = {
        'total':        total_views,
        'today':        today_views,
        'week':         week_views,
        'page_counts':  page_counts,
        'chart_labels': json.dumps(chart_labels),
        'chart_data':   json.dumps(chart_data),
    }

    return render_template('admin.html',
        bookings=bookings,
        photos=photos,
        notes=notes,
        posts=posts,
        settings=settings,
        analytics=analytics
    )

# ── BOOKING ROUTES ──────────────────────────────────────────────────────────────
@app.route('/admin/mark/<int:bid>/<status>')
@login_required
def mark(bid, status):
    b = Booking.query.get_or_404(bid)
    b.status = status
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/admin/booking/delete/<int:bid>', methods=['POST'])
@login_required
def delete_booking(bid):
    b = Booking.query.get_or_404(bid)
    db.session.delete(b)
    db.session.commit()
    return jsonify({'ok': True})

# ── IMAGE UPLOAD ────────────────────────────────────────────────────────────────
@app.route('/admin/upload', methods=['POST'])
@login_required
def upload_photo():
    if 'file' not in request.files:
        return jsonify({'ok': False, 'error': 'No file'}), 400
    file     = request.files['file']
    title    = request.form.get('title', '').strip()
    category = request.form.get('category', 'people').strip()
    featured = request.form.get('featured', 'false') == 'true'
    if file.filename == '':
        return jsonify({'ok': False, 'error': 'Empty filename'}), 400
    try:
        result   = cloudinary.uploader.upload(file, folder='tino_photography')
        url      = result['secure_url']
        filename = result['public_id'].replace('tino_photography/', '')
        existing = Photo.query.filter_by(filename=filename).first()
        if existing:
            existing.title    = title
            existing.category = category
            existing.featured = featured
            existing.url      = url
        else:
            db.session.add(Photo(filename=filename, url=url, title=title, category=category, featured=featured))
        db.session.commit()
        return jsonify({'ok': True, 'url': url})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

# ── EDIT PHOTO ──────────────────────────────────────────────────────────────────
@app.route('/admin/photo/edit/<int:pid>', methods=['POST'])
@login_required
def edit_photo(pid):
    p          = Photo.query.get_or_404(pid)
    p.title    = request.form.get('title', p.title)
    p.category = request.form.get('category', p.category)
    p.featured = request.form.get('featured', 'false') == 'true'
    db.session.commit()
    return jsonify({'ok': True})

# ── DELETE PHOTO ─────────────────────────────────────────────────────────────────
@app.route('/admin/photo/delete/<int:pid>', methods=['POST'])
@login_required
def delete_photo(pid):
    p = Photo.query.get_or_404(pid)
    try:
        cloudinary.uploader.destroy('tino_photography/' + p.filename)
    except Exception as e:
        print('Cloudinary delete error:', e)
    db.session.delete(p)
    db.session.commit()
    return jsonify({'ok': True})

# ── BLOG ROUTES ──────────────────────────────────────────────────────────────────
@app.route('/admin/blog/save', methods=['POST'])
@login_required
def save_blog():
    data      = request.get_json()
    post_id   = data.get('id')
    title     = data.get('title', '').strip()
    body      = data.get('body', '').strip()
    cover_url = data.get('cover_url', '').strip()
    category  = data.get('category', 'general').strip()
    published = data.get('published', False)

    if post_id:
        p = BlogPost.query.get(post_id)
        if p:
            p.title      = title
            p.body       = body
            p.cover_url  = cover_url
            p.category   = category
            p.published  = published
            p.updated_at = datetime.utcnow()
            if not p.slug:
                p.slug = slugify(title)
    else:
        slug = slugify(title)
        existing = BlogPost.query.filter_by(slug=slug).first()
        if existing:
            slug = slug + '-' + str(int(datetime.utcnow().timestamp()))
        p = BlogPost(title=title, slug=slug, body=body, cover_url=cover_url, category=category, published=published)
        db.session.add(p)

    db.session.commit()
    return jsonify({'ok': True, 'id': p.id, 'slug': p.slug})

@app.route('/admin/blog/delete/<int:pid>', methods=['POST'])
@login_required
def delete_blog(pid):
    p = BlogPost.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return jsonify({'ok': True})

# ── NOTES ───────────────────────────────────────────────────────────────────────
@app.route('/admin/note/save', methods=['POST'])
@login_required
def save_note():
    data    = request.get_json()
    note_id = data.get('id')
    content = data.get('content', '').strip()
    if note_id:
        n = Note.query.get(note_id)
        if n:
            n.content    = content
            n.updated_at = datetime.utcnow()
    else:
        n = Note(content=content)
        db.session.add(n)
    db.session.commit()
    return jsonify({'ok': True, 'id': n.id})

@app.route('/admin/note/delete/<int:nid>', methods=['POST'])
@login_required
def delete_note(nid):
    n = Note.query.get_or_404(nid)
    db.session.delete(n)
    db.session.commit()
    return jsonify({'ok': True})

# ── SITE SETTINGS ────────────────────────────────────────────────────────────────
@app.route('/admin/settings/save', methods=['POST'])
@login_required
def save_settings():
    data = request.get_json()
    for key, value in data.items():
        set_setting(key, value)
    return jsonify({'ok': True})

# ── CONTACT FORM ─────────────────────────────────────────────────────────────────
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
            subject=f'New Booking — {shoot_type}',
            recipients=['tinotend4official@icloud.com'],
            reply_to=email,
            html=f"""
<div style="font-family:Arial,sans-serif;max-width:600px;background:#111;color:#f5f0eb;padding:32px;border-top:4px solid #e8000d;">
  <h2>New Booking Request</h2>
  <p><strong>Name:</strong> {name}</p>
  <p><strong>Email:</strong> {email}</p>
  <p><strong>Shoot Type:</strong> {shoot_type}</p>
  <p><strong>Message:</strong> {message}</p>
</div>"""
        )
        mail.send(msg)
    except Exception as e:
        print('Mail error:', e)
    return jsonify({'success': True})

#____blog_settings_addition______________________________________________________

@app.route('/admin/blog/get/<int:pid>')
@login_required
def get_blog(pid):
    p = BlogPost.query.get_or_404(pid)
    return jsonify({'body': p.body, 'title': p.title})
    
# ── RUN ──────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
