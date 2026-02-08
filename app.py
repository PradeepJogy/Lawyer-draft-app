import streamlit as st
import pandas as pd

st.set_page_config(page_title="Lawyer Vault", layout="centered")

# --- USER SESSION STATE ---
# This acts as a temporary database for your testing session
if 'users' not in st.session_state:
    st.session_state['users'] = {"admin": "password123"} # Default user

st.title("⚖️ Legal Case Manager")

# Sidebar for Navigation
menu = ["Access Portal", "Case Dashboard", "Drafting Vault"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Access Portal":
    st.subheader("Lawyer Portal")
    
    # Toggle between Login and Registration
    auth_mode = st.radio("Choose Action:", ["Login", "Register New Account"])

    if auth_mode == "Register New Account":
        new_user = st.text_input("Create Username (Bar ID)")
        new_pw = st.text_input("Create Password", type="password")
        if st.button("Sign Up"):
            if new_user in st.session_state['users']:
                st.error("User already exists!")
            else:
                st.session_state['users'][new_user] = new_pw
                st.success("Account created! You can now switch to Login.")

    elif auth_mode == "Login":
        user = st.text_input("Username (Bar ID)")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if user in st.session_state['users'] and st.session_state['users'][user] == password:
                st.success(f"Welcome, Advocate {user}")
                st.session_state['logged_in_user'] = user
            else:
                st.error("Invalid Username or Password")

# ... rest of your Dashboard and Vault code
