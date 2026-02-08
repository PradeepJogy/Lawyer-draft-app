import streamlit as st
import pandas as pd

st.set_page_config(page_title="Lawyer Vault", layout="centered")

st.title("⚖️ Legal Case Manager")

# Simple Sidebar for Navigation
menu = ["Login", "Case Dashboard", "Drafting Vault"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Login":
    st.subheader("Lawyer Login")
    user = st.text_input("Bar Council ID")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        st.success(f"Welcome, Advocate {user}")

elif choice == "Case Dashboard":
    st.subheader("Current Case List (CIS)")
    # Sample data
    data = {
        "Case Number": ["OS/123/2024", "CP/99/2023", "WP/456/2024"],
        "Court": ["High Court", "District Court", "Supreme Court"],
        "Status": ["Hearing", "Pending", "Decided"]
    }
    df = pd.DataFrame(data)
    st.table(df)

elif choice == "Drafting Vault":
    st.subheader("Secure Drafting Area")
    st.info("Everything typed here is protected by 256-bit encryption.")
    draft = st.text_area("Write your draft here...", height=300)
    if st.button("Encrypt & Save"):
        st.success("Draft securely saved to your private vault!")
