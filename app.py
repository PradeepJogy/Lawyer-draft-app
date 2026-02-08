import os
from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(_name_)
app.config['SECRET_KEY'] = 'legal_secret_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lawyer.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- 1. REGISTRATION & LOGIN SYSTEM ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- 2. THE DASHBOARD & AI TOOL UI ---
LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Lawyer Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-5 bg-light">
    <div class="container">
        {% if not current_user.is_authenticated %}
            <div class="card p-4 mx-auto" style="max-width: 400px;">
                <h4>Register / Login</h4>
                <form method="POST" action="/auth">
                    <input name="email" class="form-control mb-2" placeholder="Email" required>
                    <input name="password" type="password" class="form-control mb-2" placeholder="Password" required>
                    <button class="btn btn-primary w-100">Access Portal</button>
                </form>
            </div>
        {% else %}
            <div class="row">
                <div class="col-md-6">
                    <div class="card p-4 shadow-sm mb-4">
                        <h5>Supreme Court Case Sync</h5>
                        <p class="text-muted small">Enter Diary info to communicate with Registry site.</p>
                        <input id="d_no" class="form-control mb-2" placeholder="Diary Number">
                        <input id="d_year" class="form-control mb-2" placeholder="Year (e.g. 2026)">
                        <button onclick="checkDefects()" class="btn btn-dark w-100">Check Registry Defects</button>
                        <div id="defect_alert" class="mt-3 p-3 bg-white border border-danger text-danger" style="display:none;"></div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card p-4 shadow-sm">
                        <h5>AI Drafting Tool</h5>
                        <select id="type" class="form-select mb-2">
                            <option value="SLP">Special Leave Petition (Civil)</option>
                            <option value="Art32">Writ Petition (Article 32)</option>
                        </select>
                        <textarea id="facts" class="form-control mb-2" rows="5" placeholder="Enter brief facts..."></textarea>
                        <button onclick="generateDraft()" class="btn btn-primary w-100">Generate AI Draft</button>
                        <div id="draft_box" class="mt-3 p-3 bg-white border small" style="display:none; white-space: pre-wrap;"></div>
                    </div>
                </div>
            </div>
        {% endif %}
    </div>
    <script>
        async function checkDefects() {
            const d = document.getElementById('d_no').value;
            const y = document.getElementById('d_year').value;
            const box = document.getElementById('defect_alert');
            box.style.display = 'block';
            box.innerText = "Connecting to Supreme Court Registry site...";
            
            // Simulating communication with SCI portal
            setTimeout(() => {
                box.innerHTML = "<strong>⚠️ DEFECT RECORDED:</strong><br>Deficit Court Fee of ₹1500; Non-translation of Annexure-P3.";
            }, 1500);
        }

        function generateDraft() {
            const type = document.getElementById('type').value;
            const facts = document.getElementById('facts').value;
            const box = document.getElementById('draft_box');
            box.style.display = 'block';
            box.innerText = IN THE SUPREME COURT OF INDIA\\n(JURISDICTION: ${type})\\n\\nBased on Facts: ${facts}\\n\\nGROUNDS:\\n1. That the High Court erred in law...\\n2. Violation of Art. 14 of the Constitution.\\n\\nPRAYER: Set aside the impugned order...;
        }
    </script>
</body>
</html>
"""

# --- 3. ROUTES ---
@app.route('/')
def index():
    return render_template_string(LAYOUT)

@app.route('/auth', methods=['POST'])
def auth():
    email = request.form['email']
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, password=request.form['password'])
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('index'))

if _name_ == '_main_':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
