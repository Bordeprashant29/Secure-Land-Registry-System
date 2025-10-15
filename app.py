from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
import uuid
import re  # For email validation

# -------------------------
# APP CONFIGURATION
# -------------------------
app = Flask(__name__)
app.secret_key = "super_secret_key"  # Change later for better security

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

# -------------------------
# DATABASE MODEL
# -------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin / user / government


# -------------------------
# EMAIL VALIDATION FUNCTION
# -------------------------
def is_valid_email(email):
    """Check if the provided email has a valid format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)


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
# AUTH ROUTES (REGISTER / LOGIN / LOGOUT)
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

        # Email validation
        if not is_valid_email(email):
            flash("❌ Please enter a valid email address.", "error")
            return redirect(url_for('register'))

        # Password confirmation
        if password != confirm_password:
            flash("❌ Passwords do not match!", "error")
            return redirect(url_for('register'))

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("⚠️ Email already registered! Try logging in.", "warning")
            return redirect(url_for('login'))

        # Generate unique ID
        unique_id = str(uuid.uuid4())[:8].upper()

        # Save new user
        new_user = User(
            username=username,
            email=email,
            password=password,
            role=role,
            unique_id=unique_id
        )

        db.session.add(new_user)
        db.session.commit()

        flash(f"✅ Registration successful! Your unique ID is: {unique_id}. Use this to log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        unique_id = request.form['unique_id']
        password = request.form['password']
        role = request.form['role']

        # Validate user based on unique_id instead of email
        user = User.query.filter_by(unique_id=unique_id, password=password, role=role).first()
        if user:
            session['user'] = user.username
            session['role'] = user.role

            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'user':
                return redirect(url_for('user_dashboard'))
            elif role == 'government':
                return redirect(url_for('gov_dashboard'))
        else:
            flash("❌ Invalid ID, password, or role!", "error")

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
    return redirect(url_for('login'))

@app.route('/user/dashboard')
def user_dashboard():
    if session.get('role') == 'user':
        return render_template('user_dashboard.html', user=session['user'])
    return redirect(url_for('login'))

@app.route('/government/dashboard')
def gov_dashboard():
    if session.get('role') == 'government':
        return render_template('gov_dashboard.html', user=session['user'])
    return redirect(url_for('login'))


# -------------------------
# INITIALIZE DB AND RUN
# -------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
