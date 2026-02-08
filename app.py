import json
import os
import sys

class VaultManager:
    """Handles storage of drafts and private notes."""
    VAULT_DIR = "private_vault"

    @classmethod
    def ensure_vault_exists(cls):
        if not os.path.exists(cls.VAULT_DIR):
            os.makedirs(cls.VAULT_DIR)

    @classmethod
    def save_draft(cls, title, content):
        cls.ensure_vault_exists()
        filename = f"{cls.VAULT_DIR}/{title.replace(' ', '_')}.txt"
        with open(filename, 'w') as f:
            f.write(content)
        print(f"\n[Vault] Draft '{title}' saved successfully.")

    @classmethod
    def list_drafts(cls):
        if not os.path.exists(cls.VAULT_DIR):
            return []
        return os.listdir(cls.VAULT_DIR)

class CourtApp:
    def _init_(self):
        self.session_file = "user_session.json"
        self.user_data = self.load_session()
        self.is_authenticated = bool(self.user_data)

    def load_session(self):
        if os.path.exists(self.session_file):
            with open(self.session_file, 'r') as f:
                return json.load(f)
        return None

    def save_session(self, u, p):
        data = {"username": u, "password": p}
        with open(self.session_file, 'w') as f:
            json.dump(data, f)
        self.user_data = data
        self.is_authenticated = True

    def start(self):
        print("=== Secure Court System v1.0 ===")
        if self.is_authenticated:
            self.show_dashboard()
        else:
            self.show_auth_screen()

    def show_auth_screen(self):
        print("\n--- LOGIN / REGISTRATION ---")
        u = input("Username: ")
        p = input("Password: ")
        if u and p:
            self.save_session(u, p)
            self.show_dashboard()

    def show_dashboard(self):
        print(f"\n--- DASHBOARD (User: {self.user_data['username']}) ---")
        print("1. [Vault] Create New Draft")
        print("2. [Vault] View Saved Drafts")
        print("3. Communicate with Court Site")
        print("4. Logout & Exit")
        
        choice = input("\nSelect Option: ")

        if choice == "1":
            self.create_draft()
        elif choice == "2":
            self.view_vault()
        elif choice == "3":
            self.communicate_with_court()
        elif choice == "4":
            sys.exit()
        else:
            self.show_dashboard()

    def create_draft(self):
        print("\n--- NEW DRAFT ---")
        title = input("Enter Case/Draft Title: ")
        content = input("Enter Content: ")
        VaultManager.save_draft(title, content)
        self.show_dashboard()

    def view_vault(self):
        print("\n--- PRIVATE VAULT ---")
        drafts = VaultManager.list_drafts()
        if not drafts:
            print("No drafts found.")
        for i, d in enumerate(drafts):
            print(f"{i+1}. {d}")
        input("\nPress Enter to return...")
        self.show_dashboard()

    def communicate_with_court(self):
        print("\n[Connecting to Court Site...]")
        # This will eventually use your drafts to fill the court forms
        print("Ready to push data from Vault to Court Dashboard.")
        self.show_dashboard()

if _name_ == "_main_":
    app = CourtApp()
    app.start()
