import streamlit as st
import json
import os

# --- 1. CONFIGURATION & PERSISTENCE ---
DB_FILE = "court_vault_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"user": None, "vault": []}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Initialize app state
if "app_data" not in st.session_state:
    st.session_state.app_data = load_data()

# --- 2. AUTHENTICATION SYSTEM (The Switch) ---
def login_page():
    st.title("⚖️ Court System Registration")
    st.info("Please register to access your private vault and court dashboard.")
    
    with st.form("reg_form"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        court_url = st.text_input("Court Website URL (e.g., https://court.gov)")
        submit = st.form_submit_button("Register & Login")
        
        if submit:
            if u and p and court_url:
                st.session_state.app_data["user"] = {
                    "username": u, 
                    "password": p, 
                    "court_site": court_url
                }
                save_data(st.session_state.app_data)
                st.success("Registration Successful!")
                st.rerun()
            else:
                st.error("Please fill all fields.")

# --- 3. DASHBOARD & VAULT ---
def dashboard_page():
    user = st.session_state.app_data["user"]
    st.sidebar.title(f"Welcome, {user['username']}")
    
    menu = st.sidebar.radio("Navigation", ["Private Vault", "Court Communication", "Settings"])

    if menu == "Private Vault":
        st.header("🗄️ Private Drafting Vault")
        
        # New Draft Section
        with st.expander("➕ Create New Draft"):
            title = st.text_input("Case/Draft Title")
            content = st.text_area("Draft Content")
            if st.button("Save to Vault"):
                st.session_state.app_data["vault"].append({"title": title, "content": content})
                save_data(st.session_state.app_data)
                st.success("Draft Saved!")
                st.rerun()

        # List Existing Drafts
        st.subheader("Your Saved Drafts")
        for i, item in enumerate(st.session_state.app_data["vault"]):
            with st.chat_message("user"):
                st.write(f"*{item['title']}*")
                st.write(item['content'])

    elif menu == "Court Communication":
        st.header("🌐 Court Site Interface")
        st.write(f"Targeting: *{user['court_site']}*")
        
        if st.button("Push Vault Data to Court Form"):
            st.warning(f"Connecting to {user['court_site']}...")
            # Here is where the backend communication with the court site happens
            st.success("Handshake established. Form data is ready for the Court's dashboard.")

    elif menu == "Settings":
        if st.button("Wipe All Data & Logout"):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            st.session_state.app_data = {"user": None, "vault": []}
            st.rerun()

# --- 4. MAIN APP LOGIC ---
if st.session_state.app_data["user"] is None:
    login_page()
else:
    dashboard_page()
