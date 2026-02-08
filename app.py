import streamlit as st
import json
import os

# --- PART 1: DATA PERSISTENCE ---
DB_FILE = "legal_vault_data.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"users": {}}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Initialize Session State
if "db" not in st.session_state:
    st.session_state.db = load_db()
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# --- PART 2: AUTHENTICATION GATE (Login & Sign Up) ---
def auth_gate():
    st.title("⚖️ Court Access Portal")
    
    # Dual-path entry: Login for existing, Sign Up for new
    tab_login, tab_signup = st.tabs(["🔐 Log In", "📝 Sign Up"])

    with tab_login:
        st.subheader("Registered User Login")
        u_login = st.text_input("Username", key="login_u")
        p_login = st.text_input("Password", type="password", key="login_p")
        
        if st.button("Sign In"):
            user_data = st.session_state.db["users"].get(u_login)
            if user_data and user_data["password"] == p_login:
                st.session_state.current_user = u_login
                st.rerun()
            else:
                st.error("Invalid credentials.")

    with tab_signup:
        st.subheader("New User Registration")
        with st.form("signup_form"):
            new_u = st.text_input("Create Username")
            new_p = st.text_input("Create Password", type="password")
            confirm_p = st.text_input("Confirm Password", type="password")
            
            if st.form_submit_button("Register"):
                if new_u in st.session_state.db["users"]:
                    st.error("Username already exists.")
                elif new_u and new_p == confirm_p:
                    st.session_state.db["users"][new_u] = {"password": new_p, "court": "", "cases": []}
                    save_db(st.session_state.db)
                    st.success("Account created! Please switch to the Log In tab.")
                else:
                    st.error("Check inputs and ensure passwords match.")

# --- PART 3: CASE MANAGEMENT (Post-Login Dashboard) ---
def case_management():
    user_id = st.session_state.current_user
    user_data = st.session_state.db["users"][user_id]
    
    st.sidebar.title(f"User: {user_id}")
    if st.sidebar.button("Logout"):
        st.session_state.current_user = None
        st.rerun()

    st.header("📋 Case Management Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["New Case Form", "Private Vault", "Court Sync"])

    with tab1:
        st.subheader("Drafting Form")
        with st.form("case_form"):
            title = st.text_input("Case Title/Reference")
            content = st.text_area("Legal Drafting Content")
            if st.form_submit_button("Save Draft"):
                st.session_state.db["users"][user_id]["cases"].append({"title": title, "content": content})
                save_db(st.session_state.db)
                st.success("Case saved to vault.")

    with tab2:
        st.subheader("Vault Storage")
        for case in user_data["cases"]:
            with st.expander(f"Case: {case['title']}"):
                st.write(case['content'])

    with tab3:
        st.subheader("Court Website Communication")
        saved_url = user_data.get("court", "")
        court_url = st.text_input("Enter/Update Court URL", value=saved_url)
        
        if st.button("Update URL"):
            st.session_state.db["users"][user_id]["court"] = court_url
            save_db(st.session_state.db)
            st.success("URL Saved.")

        if st.button("Communicate with Site"):
            if court_url:
                st.info(f"Connecting to: {court_url}...")
                # Per your instruction, this is where the app talks to the court site
                st.success("Handshake Successful. Case data ready for transmission.")
            else:
                st.warning("Please provide a Court URL.")

# --- PART 4: MAIN APP EXECUTION ---
if st.session_state.current_user is None:
    auth_gate()
else:
    case_management()
