import os
from flask import Flask, render_template_string, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from playwright.sync_api import sync_playwright

app = Flask(_name_)
app.config['SECRET_KEY'] = 'justice_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lawyer_app.db'
db = SQLAlchemy(app)

# --- 1. LOGIN & DATABASE SYSTEM ---
login_manager = LoginManager(app)
login_manager.login_view = 'auth_page'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- 2. SUPREME COURT SYNC LOGIC (The "Communication") ---
def get_sci_status(diary, year):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # Direct link to Diary Search
            page.goto("https://www.sci.gov.in/case-status-diary-no/")
            page.fill("#ans_dept", diary)
            page.select_option("#ans_year", label=str(year))
            
            # Note: In a real scenario, an OCR or Manual Captcha solver is needed here
            page.click("#submit_button") 
            page.wait_for_timeout(2000)
            
            # Extract Petitioner and Defects
            petitioner = "Fetched Petitioner Name" # Placeholder for selector logic
            defects = "Defect: Affidavit not notarized (Registry Scrutiny)" # Placeholder
            
            browser.close()
            return {"name": petitioner, "defects": defects}
    except:
        return {"name": "Not Found", "defects": "Connection Error"}

# --- 3. UI TEMPLATES (Combined for simplicity) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Supreme Court Lawyer Dashboard</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-dark p-3">
        <span class="navbar-brand">Advocate Dashboard 2026</span>
        {% if current_user.is_authenticated %}
            <a href="/logout" class="btn btn-outline-light">Logout</a>
        {% endif %}
    </nav>

    <div class="container mt-4">
        {% if not current_user.is_authenticated %}
            <div class="card p-4 mx-auto" style="max-width: 400px;">
                <h3>Login / Register</h3>
                <form method="POST" action="/auth">
                    <input type="email" name="email" class="form-control mb-2" placeholder="Email" required>
                    <input type="password" name="password" class="form-control mb-2" placeholder="Password" required>
                    <button class="btn btn-primary w-100">Proceed</button>
                </form>
            </div>
        {% else %}
            <div class="row">
                <div class="col-md-6">
                    <div class="card p-3 shadow-sm">
                        <h4>1. New Case Entry</h4>
                        <form id="caseForm">
                            <input id="d_no" class="form-control mb-2" placeholder="Diary Number">
                            <input id="d_year" class="form-control mb-2" placeholder="Year">
                            <button type="button" onclick="syncCourt()" class="btn btn-success w-100">Sync with Supreme Court</button>
                        </form>
                        <hr>
                        <div id="result" class="mt-3"></div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card p-3 shadow-sm">
                        <h4>2. AI Drafting (SLP / Art. 32)</h4>
                        <select id="draftType" class="form-select mb-2">
                            <option value="SLP">Special Leave Petition (SLP)</option>
                            <option value="Writ">Writ Petition (Article 32)</option>
                        </select>
                        <textarea id="facts" class="form-control mb-2" rows="5" placeholder="Enter brief facts of the case..."></textarea>
                        <button onclick="generateDraft()" class="btn btn-primary w-100">AI Generate Draft</button>
                        <div id="draftOutput" class="mt-3 p-2 bg-white border" style="white-space: pre-wrap; display:none;"></div>
                    </div>
                </div>
            </div>
        {% endif %}
    </div>

    <script>
        async function syncCourt() {
            const d = document.getElementById('d_no').value;
            const y = document.getElementById('d_year').value;
            const res = await fetch(/sync?d=${d}&y=${y});
            const data = await res.json();
            document.getElementById('result').innerHTML = `
                <div class="alert alert-info">
                    <strong>Petitioner:</strong> ${data.name}<br>
                    <strong class="text-danger">Registry Defects:</strong> ${data.defects}
                </div>`;
        }

        function generateDraft() {
            const type = document.getElementById('draftType').value;
            const facts = document.getElementById('facts').value;
            const output = document.getElementById('draftOutput');
            output.style.display = 'block';
            output.innerText = IN THE SUPREME COURT OF INDIA\\n(CIVIL APPELLATE JURISDICTION)\\n\\nDrafting ${type}...\\n\\nBased on your facts: ${facts}\\n\\n[AI generated legal grounds and prayers according to the Supreme Court Rules 2013];
        }
    </script>
</body>
</html>
"""

# --- 4. ROUTES ---
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

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

@app.route('/sync')
@login_required
def sync():
    d = request.args.get('d')
    y = request.args.get('y')
    return jsonify(get_sci_status(d, y))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if _name_ == '_main_':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
