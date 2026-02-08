import streamlit as st
import json
import os

# --- 1. DATA PERSISTENCE ---
DB_FILE = "legal_vault.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"users": {}}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Initialize database in session state
if "db" not in st.session_state:
    st.session_state.db = load_db()
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# --- 2. AUTHENTICATION LOGIC (Registration vs Login) ---
def auth_gate():
    st.title("⚖️ Legal Portal Access")
    
    # If no users exist, force Registration
    if not st.session_state.db["users"]:
        st.subheader("New User Registration")
        with st.form("reg_form"):
            u = st.text_input("Create Username")
            p = st.text_input("Create Password", type="password")
            court = st.text_input("Court Website URL (e.g. https://highcourt.gov)")
            if st.form_submit_button("Register"):
                if u and p and court:
                    st.session_state.db["users"][u] = {"password": p, "court": court, "cases": []}
                    save_db(st.session_state.db)
                    st.success("Registration complete! Please log in.")
                    st.rerun()
    
    # If users exist, show Login
    else:
        st.subheader("User Login")
        u_login = st.text_input("Username")
        p_login = st.text_input("Password", type="password")
        if st.button("Login"):
            user_data = st.session_state.db["users"].get(u_login)
            if user_data and user_data["password"] == p_login:
                st.session_state.current_user = u_login
                st.rerun()
            else:
                st.error("Invalid credentials")

# --- 3. CASE MANAGEMENT FORMS ---
def case_management():
    user_id = st.session_state.current_user
    user_data = st.session_state.db["users"][user_id]
    
    st.sidebar.title(f"Logged in: {user_id}")
    st.sidebar.write(f"Connected to: {user_data['court']}")
    if st.sidebar.button("Logout"):
        st.session_state.current_user = None
        st.rerun()

    st.header("📋 Case Management Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["New Case Form", "Private Vault", "Court Sync"])

    with tab1:
        st.subheader("Draft New Case")
        with st.form("case_form"):
            c_title = st.text_input("Case Reference / Title")
            c_type = st.selectbox("Type", ["Civil", "Criminal", "Family", "Appellate"])
            c_desc = st.text_area("Draft Details / Pleading")
            if st.form_submit_button("Save Draft to Vault"):
                new_case = {"title": c_title, "type": c_type, "details": c_desc}
                st.session_state.db["users"][user_id]["cases"].append(new_case)
                save_db(st.session_state.db)
                st.success("Draft securely stored.")

    with tab2:
        st.subheader("Your Private Drafts")
        for case in user_data["cases"]:
            with st.expander(f"Case: {case['title']}"):
                st.write(f"*Type:* {case['type']}")
                st.write(case['details'])

    with tab3:
        st.subheader("Court Communication")
        st.write(f"Ready to communicate with: *{user_data['court']}*")
        if st.button("Transmit to Court Dashboard"):
            st.info(f"Establishing handshake with {user_data['court']}...")
            # Communication logic goes here
            st.success("Data prepared for Court Dashboard submission.")

# --- 4. MAIN APP FLOW ---

if st.session_state.current_user is None:
    auth_gate()
else:
    case_management()
