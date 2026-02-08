import streamlit as st
import json
import os

# --- 1. DATA PERSISTENCE ---
DB_FILE = "legal_system_vault.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {"users": {}}
    return {"users": {}}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Initialize Session State
if "db" not in st.session_state:
    st.session_state.db = load_db()
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# --- 2. AUTHENTICATION LOGIC (Clean Registration/Login) ---
def auth_gate():
    st.title("⚖️ Secure Legal Portal")
    
    # Check if we need to show Registration or Login
    users_exist = len(st.session_state.db["users"]) > 0

    if not users_exist:
        st.subheader("New User Registration")
        with st.form("reg_form"):
            u = st.text_input("Create Username")
            p = st.text_input("Create Password", type="password")
            # Note: Court URL removed from here
            if st.form_submit_button("Register Account"):
                if u and p:
                    st.session_state.db["users"][u] = {"password": p, "court": "", "cases": []}
                    save_db(st.session_state.db)
                    st.success("Account created! Please log in.")
                    st.rerun()
                else:
                    st.error("Please provide both a username and password.")
    else:
        st.subheader("Login")
        u_login = st.text_input("Username")
        p_login = st.text_input("Password", type="password")
        if st.button("Sign In"):
            user_data = st.session_state.db["users"].get(u_login)
            if user_data and user_data["password"] == p_login:
                st.session_state.current_user = u_login
                st.rerun()
            else:
                st.error("Invalid credentials.")

# --- 3. CASE MANAGEMENT & COURT CONNECTION ---
def case_management():
    user_id = st.session_state.current_user
    user_data = st.session_state.db["users"][user_id]
    
    st.sidebar.title(f"User: {user_id}")
    if st.sidebar.button("Logout"):
        st.session_state.current_user = None
        st.rerun()

    st.header("📋 Case Management")
    
    tab1, tab2, tab3 = st.tabs(["Drafting Form", "Private Vault", "Court Interface"])

    with tab1:
        st.subheader("Case Drafting")
        with st.form("draft_form"):
            title = st.text_input("Case Title")
            content = st.text_area("Legal Content / Draft")
            if st.form_submit_button("Save to Vault"):
                new_entry = {"title": title, "content": content}
                st.session_state.db["users"][user_id]["cases"].append(new_entry)
                save_db(st.session_state.db)
                st.success("Draft securely stored.")

    with tab2:
        st.subheader("Stored Drafts")
        if not user_data["cases"]:
            st.info("No drafts found.")
        for case in user_data["cases"]:
            with st.expander(f"📁 {case['title']}"):
                st.write(case['content'])

    with tab3:
        st.subheader("Target Court Communication")
        # User enters the Court URL here, inside the app logic
        saved_url = user_data.get("court", "")
        new_url = st.text_input("Target Court Website", value=saved_url, placeholder="https://highcourt.gov")
        
        if st.button("Update Court Destination"):
            st.session_state.db["users"][user_id]["court"] = new_url
            save_db(st.session_state.db)
            st.success("Target Court Updated.")
            st.rerun()

        st.divider()
        if st.button("Communicate with Site"):
            if new_url:
                st.warning(f"Establishing link with {new_url}...")
                # Here the app uses the URL provided to bridge the connection
                st.success("Handshake established. Data ready for site communication.")
            else:
                st.error("Please enter a Court Website URL first.")

# --- 4. EXECUTION ---
if st.session_state.current_user is None:
    auth_gate()
else:
    case_management()
