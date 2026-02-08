import streamlit as st
import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Lawyer Desktop Portal",
    page_icon="⚖️",
    layout="wide"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'email' not in st.session_state:
    st.session_state.email = ""
if 'sync_status' not in st.session_state:
    st.session_state.sync_status = "Waiting for sync..."
if 'draft_text' not in st.session_state:
    st.session_state.draft_text = ""

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #3498db;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .status-box {
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .warning { background-color: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
    .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .info { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
</style>
""", unsafe_allow_html=True)

# LOGIN PAGE
if not st.session_state.logged_in:
    st.markdown('<div class="main-header">⚖️ Lawyer Desktop Portal</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7f8c8d;">Supreme Court Interface</p>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown("### Login")
        email = st.text_input("Email Address", value="lawyer@example.com")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Enter Dashboard", type="primary", use_container_width=True):
                if email and "@" in email and "." in email:
                    st.session_state.logged_in = True
                    st.session_state.email = email
                    st.rerun()
                else:
                    st.error("Please enter a valid email address")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #95a5a6;'>Supreme Court of India • Legal Tech Interface</p>", 
                unsafe_allow_html=True)

# DASHBOARD PAGE
else:
    # HEADER
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        st.markdown(f'<div class="main-header">Lawyer Portal • {st.session_state.email}</div>', unsafe_allow_html=True)
    with col3:
        if st.button("Logout", type="secondary"):
            st.session_state.logged_in = False
            st.rerun()
    
    # MAIN CONTENT - Two columns
    col1, col2 = st.columns(2)
    
    # COLUMN 1: Supreme Court Sync
    with col1:
        st.markdown('<div class="section-header">1. Supreme Court Registry Sync</div>', unsafe_allow_html=True)
        
        diary_no = st.text_input("Diary Number", value="12345", key="diary")
        year = st.text_input("Year", value="2024", key="year")
        
        if st.button("Fetch Status from Court Site", type="primary"):
            if diary_no and year:
                if year.isdigit():
                    # Simulate API call
                    with st.spinner("Connecting to Supreme Court Registry..."):
                        time.sleep(1.5)
                    
                    # Determine status
                    if int(year) < 2020:
                        status_class = "warning"
                        status_text = f"*CONNECTED TO SUPREME COURT REGISTRY*  \nDiary: {diary_no}/{year}  \n*STATUS:* Case Archived  \n*ACTION:* Contact Registry"
                    elif "123" in diary_no:
                        status_class = "error"
                        status_text = f"*CONNECTED TO SUPREME COURT REGISTRY*  \nDiary: {diary_no}/{year}  \n*STATUS:* Defect Found  \n*ACTION:* Check Registry Scrutiny"
                    else:
                        status_class = "success"
                        status_text = f"*CONNECTED TO SUPREME COURT REGISTRY*  \nDiary: {diary_no}/{year}  \n*STATUS:* Ready for Listing  \n*ACTION:* Awaiting Date"
                    
                    st.session_state.sync_status = f'<div class="status-box {status_class}">{status_text}</div>'
                else:
                    st.error("Year must be a number")
            else:
                st.error("Please enter both Diary and Year")
        
        # Display status
        st.markdown(st.session_state.sync_status, unsafe_allow_html=True)
        
        # Additional court info
        with st.expander("Court Information"):
            st.info("""
            *Supreme Court Registry Contact:*
            - Email: registry.sci@gov.in
            - Phone: 011-23388942
            - Working Hours: 10:00 AM - 5:30 PM
            """)
    
    # COLUMN 2: AI Drafting
    with col2:
        st.markdown('<div class="section-header">2. AI Drafting (SLP / Writ Petition)</div>', unsafe_allow_html=True)
        
        facts = st.text_area("Enter Case Facts:", 
                           value="The petitioner, a resident of Delhi, was denied the right to...",
                           height=150)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Generate Draft", type="primary", use_container_width=True):
                if facts:
                    today = datetime.datetime.now().strftime("%d %B, %Y")
                    
                    draft_template = f"""IN THE SUPREME COURT OF INDIA
CIVIL ORIGINAL JURISDICTION
WRIT PETITION (CIVIL) NO. ___ OF {datetime.datetime.now().year}
---------------------------------------------------------------------------------

IN THE MATTER OF:
Petitioner(s)   : [Name(s)]
Versus
Respondent(s)   : [Name(s)]

GROUNDS:
1. Violation of Fundamental Rights under Article(s) 14, 19, and 21 of the Constitution.
2. Error apparent on the face of the record in the impugned judgment.
3. Substantial questions of law of general importance.
4. Inconsistent views between different High Courts.

BRIEF FACTS:
{facts}

PRAYER:
For the reasons stated above, it is respectfully prayed that this Hon'ble Court may:
a) Issue appropriate writ/direction/order;
b) Grant interim relief as deemed fit;
c) Pass any other order(s) as this Hon'ble Court may deem fit in the interest of justice.

Dated: {today}
Place: New Delhi

COUNSEL FOR PETITIONER(S)
[Signature]
"""
                    st.session_state.draft_text = draft_template
                else:
                    st.error("Please enter case facts")
        
        with col_btn2:
            if st.button("Clear Draft", use_container_width=True):
                st.session_state.draft_text = ""
                st.rerun()
        
        # Draft output
        st.markdown("*Generated Draft:*")
        draft_output = st.text_area("", 
                                   value=st.session_state.draft_text,
                                   height=400,
                                   key="draft_output")
        
        # Export options
        if st.session_state.draft_text:
            st.download_button(
                label="Download Draft as .txt",
                data=st.session_state.draft_text,
                file_name=f"supreme_court_draft_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
    
    # FOOTER
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 📊 Case Statistics")
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    
    with stats_col1:
        st.metric("Pending Cases", "12", "3 this month")
    with stats_col2:
        st.metric("Listed Today", "2", "1 urgent")
    with stats_col3:
        st.metric("Drafts Created", "8", "2 today")
    with stats_col4:
        st.metric("Sync Success", "94%", "2% ▲")

# Installation Requirements:
st.sidebar.markdown("## 📦 Installation")
st.sidebar.code("pip install streamlit")

st.sidebar.markdown("## 🚀 Run the App")
st.sidebar.code("streamlit run app.py")

st.sidebar.markdown("## 🔧 Requirements")
st.sidebar.info("""
- Python 3.8+
- Streamlit
- Internet connection for deployment
""")
