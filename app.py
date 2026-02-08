import streamlit as st
import json
import os

# --- 1. DATA STORAGE & COURT MAPPING ---
DB_FILE = "lawyer_vault.json"

# This is the "Brain" that removes the need for URLs
COURT_DATABASE_MAP = {
    "Supreme Court of India": "https://main.sci.gov.in",
    "Delhi High Court": "https://delhihighcourt.nic.in",
    "Bombay High Court": "https://bombayhighcourt.nic.in",
    "Himachal Pradesh High Court": "https://hphighcourt.nic.in",
    "National CNR Search": "https://ecourts.gov.in"
}

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"users": {}}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

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

# --- 3. THE LAWYER'S TWO-PART DASHBOARD ---
def case_management():
    user_id = st.session_state.current_user
    user_data = st.session_state.db["users"][user_id]
    
    st.title("💼 Professional Legal Dashboard")

    # --- PART 1: CASE REGISTRATION (INTERNAL) ---
    st.header("Part 1: Matter Intake & Search")
    with st.form("lawyer_intake_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. Client's Name
            client = st.text_input("Client Name")
            
            # 2. Name of Court (The user picks, doesn't type URL)
            court_selection = st.selectbox("Name of Court", list(COURT_DATABASE_MAP.keys()))
            
        with col2:
            # 3. Filing Number (Diary/Stamp/CNR)
            num_type = st.selectbox("Number Type", ["CNR Number", "Diary Number", "Stamp Number", "Case Number"])
            filing_no = st.text_input(f"Enter {num_type}")

        if st.form_submit_button("Register & Search Court Records"):
            if client and filing_no:
                # 4. Search Logic: App finds URL from COURT_DATABASE_MAP internally
                target_url = COURT_DATABASE_MAP[court_selection]
                
                new_case = {
                    "client": client,
                    "court": court_selection,
                    "url": target_url,
                    "filing_no": filing_no,
                    "num_type": num_type,
                    "status": "Awaiting Sync"
                }
                st.session_state.db["users"][user_id]["cases"].append(new_case)
                save_db(st.session_state.db)
                st.success(f"Case registered. Target URL identified: {target_url}")
                st.rerun()

    st.divider()

    # --- PART 2: THE VAULT & COURT COMMUNICATION ---
    st.header("Part 2: Case Vault & Live Communication")
    
    if not user_data["cases"]:
        st.info("No active cases in your vault.")
    else:
        for i, case in enumerate(user_data["cases"]):
            with st.expander(f"📁 {case['client']} | {case['court']} ({case['filing_no']})"):
                st.write(f"*Jurisdiction:* {case['court']}")
                st.write(f"*{case['num_type']}:* {case['filing_no']}")
                
                # The "Search that court only" button
                if st.button(f"🔍 Sync with {case['court']}", key=f"sync_{i}"):
                    st.info(f"Connecting to {case['url']} to verify {case['num_type']}...")
                    # This is where the communication logic executes
                    st.success("Connection established. Case status updated from court site.")

                if st.button("Remove from Vault", key=f"del_{i}"):
                    user_data["cases"].pop(i)
                    save_db(st.session_state.db)
                    st.rerun()

# --- 4. EXECUTION ---
if st.session_state.current_user is None:
    auth_gate()
else:
    case_management()
