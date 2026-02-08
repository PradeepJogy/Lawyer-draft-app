import tkinter as tk
from tkinter import messagebox

# 1. SETUP THE WINDOW
root = tk.Tk()
root.title("Lawyer Desktop Portal")
root.geometry("800x600")

# 2. LOGIN FUNCTION
def login_action():
    if email_entry.get() == "":
        messagebox.showwarning("Login", "Please enter your Email")
    else:
        login_frame.pack_forget() # Hide login
        main_frame.pack(fill="both", expand=True) # Show Dashboard

# 3. SUPREME COURT SYNC FUNCTION
def sync_with_court():
    d = diary_entry.get()
    y = year_entry.get()
    status_label.config(text=f"CONNECTED TO COURT SITE\nDiary: {d}/{y}\nSTATUS: Defect Found\nACTION: Check Registry Scrutiny", fg="red")

# 4. AI DRAFTING FUNCTION
def generate_draft():
    facts = facts_input.get("1.0", "end")
    draft_output.delete("1.0", "end")
    header = "IN THE SUPREME COURT OF INDIA\n----------------------------\n"
    draft_output.insert("1.0", header + "GROUNDS:\n1. Error in Law\n2. Violation of Rights\n\nFACTS PROVIDED:\n" + facts)

# --- THE LOGIN SCREEN ---
login_frame = tk.Frame(root, pady=50)
login_frame.pack()
tk.Label(login_frame, text="Lawyer Login", font=("Arial", 18)).pack(pady=10)
email_entry = tk.Entry(login_frame, width=30)
email_entry.insert(0, "lawyer@example.com")
email_entry.pack(pady=5)
tk.Button(login_frame, text="Enter Dashboard", command=login_action).pack(pady=20)

# --- THE DASHBOARD (Hidden until login) ---
main_frame = tk.Frame(root, padx=20, pady=20)

# Section: Court Sync
tk.Label(main_frame, text="1. Supreme Court Registry Sync", font=("Arial", 12, "bold")).pack(anchor="w")
diary_entry = tk.Entry(main_frame)
diary_entry.pack(fill="x", pady=2)
year_entry = tk.Entry(main_frame)
year_entry.pack(fill="x", pady=2)
tk.Button(main_frame, text="Fetch Status from Court Site", command=sync_with_court).pack(pady=5)
status_label = tk.Label(main_frame, text="Waiting for Sync...", fg="gray")
status_label.pack(pady=10)

# Section: AI Drafting
tk.Label(main_frame, text="2. AI Drafting (SLP / Art. 32)", font=("Arial", 12, "bold")).pack(anchor="w", pady=(20, 0))
facts_input = tk.Text(main_frame, height=5)
facts_input.pack(fill="x", pady=5)
tk.Button(main_frame, text="Generate Draft", command=generate_draft).pack(pady=5)
draft_output = tk.Text(main_frame, height=10, bg="#f0f0f0")
draft_output.pack(fill="both", expand=True)

root.mainloop(
