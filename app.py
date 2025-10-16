from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import os, uuid, re

# -------------------------
# APP CONFIGURATION
# -------------------------
app = Flask(__name__)
app.secret_key = "super_secret_key"  # Change later

# Ensure instance folder exists
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR)

# Database configuration
db_path = os.path.join(INSTANCE_DIR, 'landchain.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Email configuration (Optional, replace with your credentials)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='your_email@gmail.com',
    MAIL_PASSWORD='your_app_password'
)
mail = Mail(app)

# -------------------------
# DATABASE MODEL
# -------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin / user / government

# -------------------------
# VALIDATION HELPERS
# -------------------------
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

def is_strong_password(password):
    """Password must have 8+ chars, uppercase, lowercase, number, special char"""
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$'
    return re.match(pattern, password)

# -------------------------
# STATIC + LANDING ROUTES
# -------------------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/how')
def how():
    return render_template('how.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory('static/assets', filename)

# -------------------------
# AUTH ROUTES
# -------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form.get('confirm_password')
        role = request.form['role']

        # Validate inputs
        if not username or not email or not password or not role:
            flash("⚠️ All fields are required!", "error")
            return redirect(url_for('register'))

        if not is_valid_email(email):
            flash("❌ Please enter a valid email address.", "error")
            return redirect(url_for('register'))

        if password != confirm_password:
            flash("❌ Passwords do not match!", "error")
            return redirect(url_for('register'))

        if not is_strong_password(password):
            flash("⚠️ Password must be 8+ chars with uppercase, lowercase, number, special char.", "error")
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash("⚠️ Email already registered! Try logging in.", "warning")
            return redirect(url_for('login'))

        # Generate unique ID and hash password
        unique_id = str(uuid.uuid4())[:8].upper()
        hashed_password = generate_password_hash(password)

        # Save user
        new_user = User(username=username, email=email, password=hashed_password, role=role, unique_id=unique_id)
        db.session.add(new_user)
        db.session.commit()

        # Send unique ID via email
        try:
            msg = Message("Welcome to LandChain 🌱", sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f"Hello {username},\n\nYour registration was successful!\nYour Unique ID: {unique_id}\nUse this ID to log in.\n\n- LandChain Team"
            mail.send(msg)
        except Exception as e:
            print("⚠️ Email send failed:", e)

        flash(f"✅ Registration successful! Your Unique ID: {unique_id}. It has been sent to your email.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        unique_id = request.form['unique_id'].strip()
        password = request.form['password']
        role = request.form['role']

        user = User.query.filter_by(unique_id=unique_id, role=role).first()

        if user and check_password_hash(user.password, password):
            session['user'] = user.username
            session['role'] = user.role
            session['unique_id'] = user.unique_id
            flash(f"✅ Welcome back, {user.username}!", "success")

            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'user':
                return redirect(url_for('user_dashboard'))
            else:
                return redirect(url_for('gov_dashboard'))
        else:
            flash("❌ Invalid credentials! Check your ID, password, and role.", "error")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("✅ You have been logged out successfully.", "info")
    return redirect(url_for('home'))

# -------------------------
# DASHBOARDS
# -------------------------
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') == 'admin':
        return render_template('admin_dashboard.html', user=session['user'])
    flash("⚠️ Unauthorized access.", "error")
    return redirect(url_for('login'))

@app.route('/user/dashboard')
def user_dashboard():
    if session.get('role') == 'user':
        return render_template('user_dashboard.html', user=session['user'])
    flash("⚠️ Unauthorized access.", "error")
    return redirect(url_for('login'))

@app.route('/government/dashboard')
def gov_dashboard():
    if session.get('role') == 'government':
        return render_template('gov_dashboard.html', user=session['user'])
    flash("⚠️ Unauthorized access.", "error")
    return redirect(url_for('login'))

# -------------------------
# INITIALIZE DB AND RUN
# -------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
