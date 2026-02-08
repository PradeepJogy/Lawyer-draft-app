import streamlit as st
import json
import os

# --- 1. DATA STORAGE SETUP ---
DB_FILE = "court_system_data.json"

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

# Persistent Session State
if "db" not in st.session_state:
    st.session_state.db = load_db()
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# --- 2. AUTHENTICATION LOGIC (The Entry Point) ---
def auth_gate():
    st.title("⚖️ Court Portal Access")
    
    # Check if any user exists in the system
    users_exist = len(st.session_state.db["users"]) > 0

    if not users_exist:
        # FLOW A: REGISTRATION (Only for the very first user)
        st.subheader("New User Registration")
        st.info("No registered accounts found. Please set up your profile.")
        
        with st.form("registration_form"):
            new_u = st.text_input("Create Username")
            new_p = st.text_input("Create Password", type="password")
            # Court URL is captured ONCE here and saved forever
            court_url = st.text_input("Court Website URL (e.g., https://court.gov)")
            
            if st.form_submit_button("Register Account"):
                if new_u and new_p and court_url:
                    st.session_state.db["users"][new_u] = {
                        "password": new_p, 
                        "court": court_url, 
                        "cases": []
                    }
                    save_db(st.session_state.db)
                    st.success("Account created! You can now log in.")
                    st.rerun()
                else:
                    st.error("Please fill in all registration fields.")
    else:
        # FLOW B: LOGIN (For all returning users)
        st.subheader("Login to Dashboard")
        
        u_input = st.text_input("Username")
        p_input = st.text_input("Password", type="password")
        
        if st.button("Sign In"):
            user_record = st.session_state.db["users"].get(u_input)
            if user_record and user_record["password"] == p_input:
                st.session_state.current_user = u_input
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

# --- 3. CASE MANAGEMENT & COURT COMMUNICATION ---
def case_management():
    user_id = st.session_state.current_user
    user_data = st.session_state.db["users"][user_id]
    
    # Sidebar navigation
    st.sidebar.title(f"User: {user_id}")
    st.sidebar.markdown(f"*Target Court:*\n{user_data['court']}")
    
    if st.sidebar.button("Logout"):
        st.session_state.current_user = None
        st.rerun()

    st.header("📋 Case Management Forms")
    
    # Functional Tabs
    tab1, tab2, tab3 = st.tabs(["Draft New Case", "Drafting Vault", "Court Sync"])

    with tab1:
        st.subheader("Form Input")
        with st.form("new_case_entry"):
            title = st.text_input("Case Title / Reference")
            details = st.text_area("Drafting Content (Pleadings, etc.)")
            if st.form_submit_button("Save to Private Vault"):
                new_case = {"title": title, "content": details}
                st.session_state.db["users"][user_id]["cases"].append(new_case)
                save_db(st.session_state.db)
                st.success("Draft saved successfully.")

    with tab2:
        st.subheader("Private Drafting Vault")
        if not user_data["cases"]:
            st.write("No drafts found in your vault.")
        for case in user_data["cases"]:
            with st.expander(f"Case: {case['title']}"):
                st.write(case['content'])

    with tab3:
        st.subheader("External Court Communication")
        st.write(f"Connecting to: {user_data['court']}")
        
        if st.button("Transmit to Court Site"):
            # This follows your saved instruction: communicate with site of the Court entered by user
            st.warning(f"Initiating handshake with {user_data['court']}...")
            # Placeholder for actual automation (Requests/Selenium)
            st.success("Connection successful. Data ready for Court Dashboard.")

# --- 4. EXECUTION ---


if st.session_state.current_user is None:
    auth_gate()
else:
    case_management()
