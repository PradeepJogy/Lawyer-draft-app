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

