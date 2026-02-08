import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# --- THE LAWYER APP INTERFACE ---
class LawyerApp:
    def _init_(self, root):
        self.root = root
        self.root.title("Advocate Command Center - Supreme Court of India")
        self.root.geometry("900x700")
        
        # Simple Login State
        self.is_logged_in = False
        self.show_login_screen()

    def show_login_screen(self):
        self.login_frame = ttk.Frame(self.root, padding="20")
        self.login_frame.pack(expand=True)

        ttk.Label(self.login_frame, text="Lawyer Login / Registration", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self.login_frame, text="Email:").grid(row=1, column=0, sticky="e")
        self.email_entry = ttk.Entry(self.login_frame, width=30)
        self.email_entry.grid(row=1, column=1, pady=5)

        ttk.Label(self.login_frame, text="Password:").grid(row=2, column=0, sticky="e")
        self.pass_entry = ttk.Entry(self.login_frame, width=30, show="*")
        self.pass_entry.grid(row=2, column=1, pady=5)

        ttk.Button(self.login_frame, text="Enter Dashboard", command=self.login).grid(row=3, column=0, columnspan=2, pady=20)

    def login(self):
        if self.email_entry.get() and self.pass_entry.get():
            self.login_frame.destroy()
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Please enter Email and Password")

    def show_dashboard(self):
        # Create Main Dashboard Layout
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        # LEFT SIDE: Supreme Court Sync
        left_panel = ttk.LabelFrame(main_frame, text=" 📡 Supreme Court Case Sync ", padding="10")
        left_panel.pack(side="left", fill="both", expand=True, padx=5)

        ttk.Label(left_panel, text="Diary Number:").pack(anchor="w")
        self.diary_entry = ttk.Entry(left_panel)
        self.diary_entry.pack(fill="x", pady=5)

        ttk.Label(left_panel, text="Year of Filing:").pack(anchor="w")
        self.year_entry = ttk.Entry(left_panel)
        self.year_entry.pack(fill="x", pady=5)

        ttk.Button(left_panel, text="Fetch Registry Status", command=self.sync_court).pack(fill="x", pady=10)
        
        self.status_box = tk.Text(left_panel, height=10, bg="#fdf2f2", fg="#a00")
        self.status_box.pack(fill="both", expand=True)
        self.status_box.insert("1.0", "Registry Notifications will appear here...")

        # RIGHT SIDE: AI Drafting Tool
        right_panel = ttk.LabelFrame(main_frame, text=" ⚖️ AI Drafting (SLP / Art. 32) ", padding="10")
        right_panel.pack(side="right", fill="both", expand=True, padx=5)

        self.draft_type = ttk.Combobox(right_panel, values=["Special Leave Petition (Civil)", "Writ Petition (Article 32)"])
        self.draft_type.set("Select Petition Type")
        self.draft_type.pack(fill="x", pady=5)

        ttk.Label(right_panel, text="Brief Facts of Case:").pack(anchor="w")
        self.facts_text = tk.Text(right_panel, height=8)
        self.facts_text.pack(fill="x", pady=5)

        ttk.Button(right_panel, text="Generate AI Legal Draft", command=self.generate_draft).pack(fill="x", pady=10)

        self.draft_output = scrolledtext.ScrolledText(right_panel, height=12, bg="white")
        self.draft_output.pack(fill="both", expand=True)

    def sync_court(self):
        d = self.diary_entry.get()
        y = self.year_entry.get()
        # Simulated communication with SCI Registry site
        self.status_box.delete("1.0", tk.END)
        self.status_box.insert("1.0", f"COMMUNICATING WITH SCI SITE...\n\nDIARY NO: {d}/{y}\nSTATUS: Defect Found\nREASON: Index not paginated correctly. Vakalatnama missing stamp.")

    def generate_draft(self):
        p_type = self.draft_type.get()
        facts = self.facts_text.get("1.0", tk.END)
        self.draft_output.delete("1.0", tk.END)
        template = f"IN THE SUPREME COURT OF INDIA\n\nMEMORANDUM OF {p_type.upper()}\n\nLIST OF DATES:\n{facts}\n\nGROUNDS:\n1. Violation of Art. 14 & 21.\n2. The High Court erred in its finding...\n\nPRAYER:\nThe Petitioner prays for leave to appeal..."
        self.draft_output.insert("1.0", template)

# --- START THE PROGRAM ---
if _name_ == "_main_":
    root = tk.Tk()
    app = LawyerApp(root)
    root.mainloop()
