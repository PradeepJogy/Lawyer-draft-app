from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from playwright.sync_api import sync_playwright
import os

app = Flask(_name_)
app.config['SECRET_KEY'] = 'legal_tech_2026_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///court_firm.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    cases = db.relationship('Case', backref='owner', lazy=True)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diary_no = db.Column(db.String(20), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- REAL-TIME COURT COMMUNICATION LOGIC ---
def fetch_defects_from_court(diary_no, year):
    """Automated interaction with the Court Registry site."""
    try:
        with sync_playwright() as p:
            # Launching browser (headless=True means no window pops up)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 1. Navigate to the Court Status site
            page.goto("https://www.sci.gov.in/case-status-diary-no/")
            
            # 2. Fill the form entered by the user
            page.fill("#ans_dept", diary_no)
            page.select_option("#ans_year", label=year)
            
            # 3. Trigger search (Assumes a simple submit button)
            page.click("#get_status_btn") 
            page.wait_for_timeout(2000) # Wait for results to load
            
            # 4. Extract Scrutiny/Defect info
            # Replace '.defect-info' with the actual class/ID from the court site
            content = page.inner_text("body") 
            
            browser.close()
            return {"status": "Success", "data": content}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

# --- ROUTES ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'])
        new_user = User(email=request.form['email'], password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please login.')
        return redirect(url_for('login'))
    return '''<form method="post">Email: <input name="email"><br>Pass: <input type="password" name="password"><br><button>Register</button></form>'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Login Failed')
    return '''<form method="post">Email: <input name="email"><br>Pass: <input type="password" name="password"><br><button>Login</button></form>'''

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        # User fills the dashboard form
        new_case = Case(diary_no=request.form['diary'], year=request.form['year'], owner=current_user)
        db.session.add(new_case)
        db.session.commit()
        
    user_cases = Case.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', cases=user_cases)

@app.route('/api/sync/<int:case_id>')
@login_required
def sync_case(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    # Trigger the Court Site communication
    result = fetch_defects_from_court(case.diary_no, case.year)
    return jsonify(result)

if _name_ == '_main_':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
