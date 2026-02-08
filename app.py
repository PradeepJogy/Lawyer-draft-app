from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user

app = Flask(_name_)
app.config['SECRET_KEY'] = '123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# Login Setup
login_manager = LoginManager(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Minimal UI
HTML = """
<!DOCTYPE html>
<html>
<body style="font-family: sans-serif; padding: 50px;">
    {% if not current_user.is_authenticated %}
        <h2>Lawyer Login</h2>
        <form method="POST" action="/login">
            <input name="email" placeholder="Email" required><br><br>
            <input name="password" type="password" placeholder="Password" required><br><br>
            <button type="submit">Enter Dashboard</button>
        </form>
    {% else %}
        <h2>Lawyer Dashboard</h2>
        <div style="border: 1px solid black; padding: 20px;">
            <h3>1. Supreme Court Sync</h3>
            <input id="d" placeholder="Diary No"> <input id="y" placeholder="Year">
            <button onclick="sync()">Sync Registry</button>
            <p id="status" style="color: red;"></p>
        </div>
        <div style="border: 1px solid black; padding: 20px; margin-top: 20px;">
            <h3>2. AI Draft (SLP/Art 32)</h3>
            <textarea id="f" placeholder="Enter Facts" style="width:100%"></textarea><br>
            <button onclick="draft()">Generate Draft</button>
            <pre id="out" style="background: #eee;"></pre>
        </div>
    {% endif %}

    <script>
        function sync() {
            document.getElementById('status').innerText = "Communicating with SCI Site... Defect Found: Section 5 Limitation Delay.";
        }
        function draft() {
            document.getElementById('out').innerText = "IN THE SUPREME COURT OF INDIA...\\nDrafting Petition based on provided facts...";
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, password=request.form['password'])
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('home'))

if _name_ == '_main_':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
