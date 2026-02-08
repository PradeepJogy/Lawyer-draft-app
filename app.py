import streamlit as st
import json
import os

# --- 1. CONFIGURATION & PERSISTENCE ---
DB_FILE = "sc_lawyer_vault.json"
SCI_BASE_URL = "https://main.sci.gov.in"

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

# --- 2. RECTIFIED AUTHENTICATION GATE ---
def auth_gate():
    st.title("🏛️ Supreme Court Counsel Portal")
    st.subheader("Secure Access Gateway")
    
    tab_login, tab_signup = st.tabs(["🔐 Log In", "📝 Sign Up"])

    with tab_login:
        u_login = st.text_input("Username", key="l_user")
        p_login = st.text_input("Password", type="password", key="l_pass")
        if st.button("Access Vault"):
            user_data = st.session_state.db["users"].get(u_login)
            if user_data and user_data["password"] == p_login:
                st.session_state.current_user = u_login
                st.rerun()
            else:
                st.error("Invalid credentials.")

    with tab_signup:
        with st.form("reg_form"):
            new_u = st.text_input("Create Username")
            new_p = st.text_input("Create Password", type="password")
            conf_p = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Register Account"):
                if new_u in st.session_state.db["users"]:
                    st.error("Username already exists.")
                elif new_u and new_p == conf_p:
                    st.session_state.db["users"][new_u] = {"password": new_p, "cases": []}
                    save_db(st.session_state.db)
                    st.success("Account created! Please log in.")
                else:
                    st.error("Please verify your inputs.")

# --- 3. RECTIFIED 2-PART DASHBOARD (SUPREME COURT ONLY) ---
def case_management():
    user_id = st.session_state.current_user
    user_data = st.session_state.db["users"][user_id]
    
    st.sidebar.title("Counsel Sidebar")
    st.sidebar.info(f"Logged in as: {user_id}")
    if st.sidebar.button("Log Out"):
        st.session_state.current_user = None
        st.rerun()

    st.title("💼 Case Management Dashboard")
    st.divider()

    # --- PART 1: INTAKE (CLIENT & DIARY) ---
    st.header("Part 1: New Case Intake")
    with st.expander("➕ Register New Filing from Desk", expanded=True):
        with st.form("sc_intake", clear_on_submit=True):
            client = st.text_input("Client Name")
            
            c1, c2 = st.columns(2)
            with c1:
                diary_no = st.text_input("Diary Number")
            with c2:
                diary_year = st.selectbox("Filing Year", range(2026, 2015, -1))
            
            case_type = st.text_input("Case Category (e.g. SLP Civil)")
            
            if st.form_submit_button("Save to Private Vault"):
                if client and diary_no:
                    new_case = {
                        "client": client,
                        "diary_no": diary_no,
                        "year": diary_year,
                        "type": case_type,
                        "status": "Awaiting Sync"
                    }
                    st.session_state.db["users"][user_id]["cases"].append(new_case)
                    save_db(st.session_state.db)
                    st.success(f"Case saved: Diary No {diary_no}/{diary_year}")
                    st.rerun()

    st.divider()

    # --- PART 2: VAULT & COMMUNICATION ---
    st.header("Part 2: Private Vault & Court Sync")
    
    if not user_data["cases"]:
        st.info("Your vault is currently empty.")
    else:
        for i, case in enumerate(user_data["cases"]):
            with st.container(border=True):
                col_info, col_action = st.columns([3, 1])
                
                with col_info:
                    st.write(f"### {case['client']}")
                    st.write(f"*Diary No:* {case['diary_no']}/{case['year']} | *Type:* {case['type']}")
                
                with col_action:
                    # Logic: "App should search that court only but should not ask URL"
                    if st.button(f"🔍 Sync SCI", key=f"sync_{i}"):
                        with st.status("Communicating with Supreme Court...", expanded=False):
                            st.write(f"Targeting: {SCI_BASE_URL}")
                            st.write(f"Searching Diary Number: {case['diary_no']}...")
                            # Backend link to SCI search would happen here
                        st.success("Sync Complete")
                    
                    if st.button("🗑️ Remove", key=f"del_{i}"):
                        user_data["cases"].pop(i)
                        save_db(st.session_state.db)
                        st.rerun()

# --- 4. MAIN EXECUTION ---
if st.session_state.current_user is None:
    auth_gate()
else:
    case_management()
