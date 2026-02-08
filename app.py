import json
import os

class CourtApp:
    def _init_(self):
        self.db_file = "app_data.json"
        self.state = self.load_all_data()

    def load_all_data(self):
        """Loads everything (User & Vault) in one go to prevent sync errors."""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                return json.load(f)
        # Default empty state if app is 'new' or 'spoiled'
        return {"user": None, "vault": []}

    def save_all_data(self):
        """Writes current state to disk immediately."""
        with open(self.db_file, 'w') as f:
            json.dump(self.state, f, indent=4)

    def run(self):
        """The brain of the app: Checks login status first."""
        if not self.state["user"]:
            self.show_login()
        else:
            self.show_dashboard()

    def show_login(self):
        print("\n--- APP REGISTRATION ---")
        u = input("Username: ")
        p = input("Password: ")
        if u and p:
            self.state["user"] = {"name": u, "pass": p}
            self.save_all_data()
            print("Success! Restarting to Dashboard...")
            self.run()

    def show_dashboard(self):
        print(f"\n--- DASHBOARD (User: {self.state['user']['name']}) ---")
        print("1. Private Vault (Drafts)")
        print("2. Communicate with Court")
        print("3. Reset App (Clear all)")
        print("4. Exit")
        
        cmd = input("\nSelect: ")
        if cmd == "1": self.open_vault()
        elif cmd == "2": self.court_sync()
        elif cmd == "3": self.reset_app()
        elif cmd == "4": exit()
        else: self.run()

    def open_vault(self):
        print("\n--- PRIVATE VAULT ---")
        for i, draft in enumerate(self.state["vault"]):
            print(f"[{i}] {draft['title']}")
        
        choice = input("\n[N]ew Draft or [B]ack: ").lower()
        if choice == 'n':
            t = input("Title: ")
            c = input("Content: ")
            self.state["vault"].append({"title": t, "content": c})
            self.save_all_data()
        self.run()

    def court_sync(self):
        print(f"\n[Connecting...] Fetching Court Site for {self.state['user']['name']}...")
        print("Status: Connected. Ready to push drafts.")
        input("Press Enter to return...")
        self.run()

    def reset_app(self):
        """Fixes 'Spoiled' apps by wiping the data file."""
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
        print("\n[Wiped] Data cleared. Restarting...")
        self.state = {"user": None, "vault": []}
        self.run()

if _name_ == "_main_":
    CourtApp().run()
