import streamlit as st
import pandas as pd

st.set_page_config(page_title="Lawyer Vault", layout="centered")

# Temporary user and case storage
if 'users' not in st.session_state:
    st.session_state['users'] = {"admin": "password123"}
if 'cases' not in st.session_state:
    st.session_state['cases'] = []

st.title("⚖️ Legal Case Manager")

menu = ["Access Portal", "Case Dashboard", "Drafting Vault"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Access Portal":
    st.subheader("Lawyer Portal")
    auth_mode = st.radio("Choose Action:", ["Login", "Register New Account"])
    if auth_mode == "Register New Account":
        new_user = st.text_input("Create Username (Bar ID)")
        new_pw = st.text_input("Create Password", type="password")
        if st.button("Sign Up"):
            st.session_state['users'][new_user] = new_pw
            st.success("Account created! Switch to Login.")
    elif auth_mode == "Login":
        user = st.text_input("Username (Bar ID)")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if user in st.session_state['users'] and st.session_state['users'][user] == password:
                st.success(f"Welcome, Advocate {user}")
                st.session_state['logged_in'] = True

elif choice == "Case Dashboard":
    st.subheader("📁 New Case Entry Form")
    with st.form("case_form"):
        st.markdown("### 👥 Litigant Information")
        lit_name = st.text_input("Primary Litigant Name")
        others = st.text_area("Additional Litigants")
        p_type = st.selectbox("Party Type", ["Petitioner", "Appellant", "Respondent", "Defendant"])

        st.markdown("### 🏛️ Court & Filing")
        court = st.text_input("Name of Court")
        f_type = st.selectbox("Filing Type", ["Diary Number", "Stamp Number", "Filing Number"])
        f_val = st.text_input("Enter Number")
        f_year = st.number_input("Year", min_value=1950, max_value=2030, value=2026)

        if st.form_submit_button("Save Case"):
            case_data = {"Name": lit_name, "Court": court, "Number": f"{f_val}/{f_year}"}
            st.session_state['cases'].append(case_data)
            st.success(f"Case for {lit_name} saved!")

    if st.session_state['cases']:
        st.write("### 📋 Your Saved Cases (This Session)")
        st.table(pd.DataFrame(st.session_state['cases']))

elif choice == "Drafting Vault":
    st.subheader("🔒 Secure Drafting")
    st.text_area("Start typing your legal draft...", height=300)
    st.button("Encrypt & Save")
