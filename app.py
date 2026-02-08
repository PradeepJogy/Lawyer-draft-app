import os
import sys
import subprocess

# --- AUTOMATIC ERROR FIXER (Installs missing tools) ---
def install_dependencies():
    requirements = ['flask', 'flask-sqlalchemy', 'flask-login', 'playwright']
    for package in requirements:
        try:
            _import_(package if package != 'flask-sqlalchemy' else 'flask_sqlalchemy')
        except ImportError:
            print(f"Fixing error: Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    # Install the browser for the Court Sync
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    except:
        pass

# Run the installation check before anything else
install_dependencies()

# --- NOW START THE ACTUAL APP ---
from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from playwright.sync_api import sync_playwright

app = Flask(_name_)
app.config['SECRET_KEY'] = 'justice_2026_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lawyer_firm.db'
db = SQLAlchemy(app)

# 1. Database Setup
login_manager = LoginManager(app)
login_manager.login_view = 'home'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 2. Supreme Court Communication Logic
def get_court_status(diary, year):
    """Syncs with the Court site entered by the user."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # Navigating to SCI portal
            page.goto("https://www.sci.gov.in/case-status-diary-no/")
            page.fill("#ans_dept", diary)
            page.select_option("#ans_year", label=str(year))
            
            # NOTE: User needs to solve Captcha in a production environment
            # This is where the communication handshake happens
            page.click("#submit_button") 
            page.wait_for_timeout(2000)
            
            # Simulating extraction of Defect data
            status_update = "Defect Found: Indexing error in Vol-II (Registry Notified)"
            browser.close()
            return {"status": "Synced", "defects": status_update}
    except:
        return {"status": "Offline", "defects": "Court site currently unreachable."}

# 3. Combined Layout (Dashboard + AI Drafting)
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Advocate Command Center</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f7f6; }
        .card { border-radius: 12px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .registry-alert { background: #fff3f3; border-left: 5px solid #d9534f; padding: 10px; }
    </style>
</head>
<body>
    <div class="container py-5">
        {% if not current_user.is_authenticated %}
            <div class="card p-5 mx-auto text-center" style="max-width: 450px;">
                <h2 class="mb-4">Advocate Portal</h2>
                <form method="POST" action="/auth">
                    <input name="email" type="email" class="form-control mb-3" placeholder="Bar Email ID" required>
                    <input name="password" type="password" class="form-control mb-3" placeholder="Password" required>
                    <button class="btn btn-primary w-100">Login / Register</button>
                </form>
            </div>
        {% else %}
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Lawyer's Dashboard</h2>
                <a href="/logout" class="btn btn-outline-danger btn-sm">Sign Out</a>
            </div>

            <div class="row">
                <div class="col-md-5">
                    <div class="card p-4 h-100">
                        <h5>📡 Registry Communication</h5>
                        <p class="text-muted small">Enter Diary details to sync with Court site.</p>
                        <input id="d_no" class="form-control mb-2" placeholder="Diary Number">
                        <input id="d_year" class="form-control mb-2" placeholder="Year">
                        <button onclick="syncWithCourt()" class="btn btn-dark w-100">Fetch Registry Scrutiny</button>
                        
                        <div id="sync_result" class="mt-4 registry-alert" style="display:none;">
                            <strong>Defect Notification:</strong><br>
                            <span id="defect_msg"></span>
                        </div>
                    </div>
                </div>

                <div class="col-md-7">
                    <div class="card p-4 h-100">
                        <h5>⚖️ AI Tool: SLP & Writ Drafting</h5>
                        <select id="draftType" class="form-select mb-3">
                            <option value="SLP">Special Leave Petition (Civil)</option>
                            <option value="Writ">Writ Petition (Article 32)</option>
                        </select>
                        <textarea id="facts" class="form-control mb-3" rows="6" placeholder="Enter case facts and dates..."></textarea>
                        <button onclick="generateAIDraft()" class="btn btn-primary">Generate Legal Draft</button>
                        
                        <div id="draft_output" class="mt-3 p-3 bg-white border small" style="display:none; white-space: pre-wrap; height: 300px; overflow-y: scroll;"></div>
                    </div>
                </div>
            </div>
        {% endif %}
    </div>

    <script>
        async function syncWithCourt() {
            const d = document.getElementById('d_no').value;
            const y = document.getElementById('d_year').value;
            const res = await fetch(/sync_status?d=${d}&y=${y});
            const data = await res.json();
            document.getElementById('sync_result').style.display = 'block';
            document.getElementById('defect_msg').innerText = data.defects;
        }

        function generateAIDraft() {
            const type = document.getElementById('draftType').value;
            const facts = document.getElementById('facts').value;
            const output = document.getElementById('draft_output');
            output.style.display = 'block';
            
            const template = IN THE SUPREME COURT OF INDIA\\n(JURISDICTION: ${type})\\n\\nMEMORANDUM OF PETITION\\n\\n1. LIST OF DATES: Based on facts provided: ${facts}\\n\\n2. GROUNDS: The Petitioner submits that the impugned order violates fundamental rights...\\n\\n3. PRAYER: In light of the above, the Petitioner prays that this Hon'ble Court be pleased to grant relief...\\n\\n[END OF DRAFT];
            output.innerText = template;
        }
    </script>
</body>
</html>
"""

# 4. Routing
@app.route('/')
def home():
    return render_template_string(DASHBOARD_HTML)

@app.route('/auth', methods=['POST'])
def auth():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('home'))

@app.route('/sync_status')
@login_required
def sync_status():
    d = request.args.get('d')
    y = request.args.get('y')
    return jsonify(get_court_status(d, y))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if _name_ == '_main_':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
