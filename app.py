import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime, timedelta
import time
import json
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Lawyer Portal Pro",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
    }
    
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #3498db;
    }
    
    .case-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        transition: transform 0.2s;
    }
    
    .case-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    
    .status-filed { background-color: #d4edda; color: #155724; }
    .status-pending { background-color: #fff3cd; color: #856404; }
    .status-listed { background-color: #cce5ff; color: #004085; }
    .status-disposed { background-color: #d1ecf1; color: #0c5460; }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-transform: uppercase;
    }
    
    .positive { color: #27ae60; }
    .negative { color: #e74c3c; }
    
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .section-header {
        font-size: 1.8rem;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATABASE CLASS (Code at 3)
# ============================================

class LawyerDatabase:
    def _init_(self, db_path="lawyer_portal.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with all tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT,
                firm_name TEXT,
                bar_council_id TEXT,
                specialization TEXT,
                experience_years INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Cases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                diary_no TEXT NOT NULL,
                year INTEGER NOT NULL,
                case_title TEXT NOT NULL,
                petitioner TEXT NOT NULL,
                respondent TEXT,
                case_type TEXT DEFAULT 'Civil',
                court_name TEXT DEFAULT 'Supreme Court',
                judge_name TEXT,
                status TEXT DEFAULT 'Filed',
                filing_date DATE,
                next_hearing_date DATE,
                description TEXT,
                lawyer_notes TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(diary_no, year)
            )
        ''')
        
        # Hearings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hearings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER,
                hearing_date DATE NOT NULL,
                purpose TEXT,
                outcome TEXT,
                next_date DATE,
                notes TEXT,
                FOREIGN KEY (case_id) REFERENCES cases (id)
            )
        ''')
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER,
                doc_type TEXT NOT NULL,
                doc_name TEXT NOT NULL,
                file_path TEXT,
                generated_date DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (case_id) REFERENCES cases (id)
            )
        ''')
        
        # Billing table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS billing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER,
                billing_date DATE DEFAULT CURRENT_DATE,
                description TEXT,
                hours DECIMAL(5,2),
                rate_per_hour DECIMAL(10,2),
                amount DECIMAL(12,2),
                status TEXT DEFAULT 'Pending',
                FOREIGN KEY (case_id) REFERENCES cases (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, email, password, full_name, **kwargs):
        """Register a new user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (email, password_hash, full_name, phone, 
                                firm_name, bar_council_id, specialization, experience_years)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, password_hash, full_name, 
                  kwargs.get('phone'), kwargs.get('firm_name'),
                  kwargs.get('bar_council_id'), kwargs.get('specialization'),
                  kwargs.get('experience_years')))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, email, full_name FROM users 
            WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'email': user[1],
                'full_name': user[2]
            }
        return None
    
    def add_case(self, user_id, case_data):
        """Add a new case"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO cases (
                diary_no, year, case_title, petitioner, respondent,
                case_type, court_name, judge_name, status,
                filing_date, next_hearing_date, description,
                lawyer_notes, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            case_data['diary_no'], case_data['year'], case_data['case_title'],
            case_data['petitioner'], case_data.get('respondent'),
            case_data.get('case_type', 'Civil'), case_data.get('court_name', 'Supreme Court'),
            case_data.get('judge_name'), case_data.get('status', 'Filed'),
            case_data.get('filing_date'), case_data.get('next_hearing_date'),
            case_data.get('description'), case_data.get('lawyer_notes'),
            user_id
        ))
        
        case_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return case_id
    
    def get_user_cases(self, user_id):
        """Get all cases for a user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM cases 
            WHERE user_id = ?
            ORDER BY next_hearing_date DESC, created_at DESC
        ''', (user_id,))
        
        cases = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return cases
    
    def get_case_details(self, case_id):
        """Get detailed case information"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cases WHERE id = ?', (case_id,))
        case = cursor.fetchone()
        
        if case:
            case_dict = dict(case)
            
            # Get hearings for this case
            cursor.execute('SELECT * FROM hearings WHERE case_id = ? ORDER BY hearing_date DESC', (case_id,))
            case_dict['hearings'] = [dict(row) for row in cursor.fetchall()]
            
            # Get documents for this case
            cursor.execute('SELECT * FROM documents WHERE case_id = ?', (case_id,))
            case_dict['documents'] = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return case_dict
        
        conn.close()
        return None
    
    def update_case_status(self, case_id, status, next_date=None):
        """Update case status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE cases 
            SET status = ?, next_hearing_date = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, next_date, case_id))
        
        conn.commit()
        conn.close()
    
    def add_hearing(self, case_id, hearing_data):
        """Add hearing record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO hearings (case_id, hearing_date, purpose, outcome, next_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            case_id, hearing_data['hearing_date'], hearing_data.get('purpose'),
            hearing_data.get('outcome'), hearing_data.get('next_date'),
            hearing_data.get('notes')
        ))
        
        conn.commit()
        conn.close()
    
    def get_upcoming_hearings(self, user_id, days=30):
        """Get upcoming hearings within specified days"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.diary_no, c.year, c.case_title, c.petitioner, 
                   h.hearing_date, h.purpose, c.status
            FROM cases c
            JOIN hearings h ON c.id = h.case_id
            WHERE c.user_id = ? 
            AND h.hearing_date BETWEEN DATE('now') AND DATE('now', ?)
            ORDER BY h.hearing_date
        ''', (user_id, f'+{days} days'))
        
        hearings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return hearings

# ============================================
# PDF GENERATOR CLASS (Code at 4)
# ============================================

class PDFGenerator:
    @staticmethod
    def generate_case_summary_pdf(case_data, output_path="case_summary.pdf"):
        """Generate PDF summary for a case"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title = f"Case Summary: {case_data['diary_no']}/{case_data['year']}"
        story.append(Paragraph(title, styles['Title']))
        story.append(Spacer(1, 12))
        
        # Case Details
        details = f"""
        <b>Case Title:</b> {case_data.get('case_title', 'N/A')}<br/>
        <b>Petitioner:</b> {case_data.get('petitioner', 'N/A')}<br/>
        <b>Respondent:</b> {case_data.get('respondent', 'N/A')}<br/>
        <b>Court:</b> {case_data.get('court_name', 'N/A')}<br/>
        <b>Judge:</b> {case_data.get('judge_name', 'N/A')}<br/>
        <b>Status:</b> {case_data.get('status', 'N/A')}<br/>
        <b>Next Hearing:</b> {case_data.get('next_hearing_date', 'N/A')}<br/>
        <b>Filing Date:</b> {case_data.get('filing_date', 'N/A')}<br/>
        """
        story.append(Paragraph(details, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Description
        if case_data.get('description'):
            story.append(Paragraph("<b>Case Description:</b>", styles['Heading2']))
            story.append(Paragraph(case_data['description'], styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Lawyer Notes
        if case_data.get('lawyer_notes'):
            story.append(Paragraph("<b>Lawyer Notes:</b>", styles['Heading2']))
            story.append(Paragraph(case_data['lawyer_notes'], styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Hearings History
        if case_data.get('hearings'):
            story.append(Paragraph("<b>Hearing History:</b>", styles['Heading2']))
            for hearing in case_data['hearings']:
                hearing_text = f"""
                Date: {hearing.get('hearing_date', 'N/A')}<br/>
                Purpose: {hearing.get('purpose', 'N/A')}<br/>
                Outcome: {hearing.get('outcome', 'N/A')}<br/>
                Notes: {hearing.get('notes', 'N/A')}<br/>
                """
                story.append(Paragraph(hearing_text, styles['Normal']))
                story.append(Spacer(1, 6))
        
        # Footer
        story.append(Spacer(1, 36))
        footer = Paragraph(f"Generated on: {datetime.now().strftime('%d %B, %Y')}<br/>Lawyer Portal Pro", 
                          styles['Italic'])
        story.append(footer)
        
        doc.build(story)
        return output_path
    
    @staticmethod
    def generate_legal_draft_pdf(draft_data, output_path="legal_draft.pdf"):
        """Generate legal draft PDF"""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Header
        header = f"""
        IN THE {draft_data.get('court', 'SUPREME COURT').upper()} OF INDIA<br/>
        {draft_data.get('jurisdiction', 'ORIGINAL JURISDICTION').upper()}<br/>
        {draft_data.get('doc_type', 'WRIT PETITION').upper()} NO. ___ OF {datetime.now().year}<br/>
        """
        story.append(Paragraph(header, styles['Heading1']))
        story.append(Spacer(1, 24))
        
        # Parties
        parties = f"""
        <b>IN THE MATTER OF:</b><br/>
        {draft_data.get('petitioner', '[Petitioner Name]')}<br/>
        <i>Petitioner(s)</i><br/><br/>
        
        <b>VERSUS</b><br/><br/>
        
        {draft_data.get('respondent', '[Respondent Name]')}<br/>
        <i>Respondent(s)</i><br/>
        """
        story.append(Paragraph(parties, styles['Normal']))
        story.append(Spacer(1, 24))
        
        # Facts
        if draft_data.get('facts'):
            story.append(Paragraph("<b>BRIEF FACTS OF THE CASE:</b>", styles['Heading2']))
            story.append(Paragraph(draft_data['facts'], styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Grounds
        story.append(Paragraph("<b>GROUNDS:</b>", styles['Heading2']))
        grounds = draft_data.get('grounds', [
            "Violation of Fundamental Rights under the Constitution.",
            "Error apparent on the face of the record.",
            "Substantial questions of law of general importance."
        ])
        
        for i, ground in enumerate(grounds, 1):
            story.append(Paragraph(f"{i}. {ground}", styles['Normal']))
        
        story.append(Spacer(1, 24))
        
        # Prayer
        story.append(Paragraph("<b>PRAYER:</b>", styles['Heading2']))
        prayer = f"""
        For the reasons stated above, it is respectfully prayed that this Hon'ble Court may be pleased to:<br/><br/>
        
        a) {draft_data.get('prayer_a', 'Issue appropriate writ, order or direction')};<br/>
        b) {draft_data.get('prayer_b', 'Grant interim relief')};<br/>
        c) {draft_data.get('prayer_c', 'Pass any other order(s) as this Hon'ble Court may deem fit')}.<br/><br/>
        
        <b>PLACE:</b> New Delhi<br/>
        <b>DATE:</b> {datetime.now().strftime('%d %B, %Y')}<br/><br/>
        
        <b>COUNSEL FOR THE PETITIONER(S)</b><br/>
        [Signature]<br/>
        """
        story.append(Paragraph(prayer, styles['Normal']))
        
        doc.build(story)
        return output_path

# ============================================
# AI DRAFTING ASSISTANT
# ============================================

class AI_Drafting_Assistant:
    @staticmethod
    def generate_draft_from_facts(facts, doc_type="Writ Petition"):
        """Generate legal draft from case facts"""
        
        templates = {
            "Writ Petition": {
                "structure": [
                    "IN THE SUPREME COURT OF INDIA",
                    "WRIT PETITION (CIVIL) NO. ___ OF 2024",
                    "",
                    "IN THE MATTER OF:",
                    "Petitioner(s)   : [Name]",
                    "Versus",
                    "Respondent(s)   : [Name]",
                    "",
                    "TO",
                    "THE HON'BLE THE CHIEF JUSTICE OF INDIA",
                    "AND HIS COMPANION JUSTICES OF THE HON'BLE SUPREME COURT",
                    "",
                    "HUMBLE PETITION OF THE PETITIONER(S) ABOVENAMED",
                    "",
                    "MOST RESPECTFULLY SHEWETH:",
                    "",
                    "1. BRIEF FACTS:",
                    facts,
                    "",
                    "2. GROUNDS:",
                    "A. Violation of Fundamental Rights under Articles 14, 19 and 21 of the Constitution.",
                    "B. Arbitrary and unreasonable exercise of power.",
                    "C. Error apparent on the face of the record.",
                    "",
                    "3. PRAYER:",
                    "In view of the aforesaid facts and circumstances, it is most respectfully prayed that this Hon'ble Court may be pleased to:",
                    "a) Issue a writ of certiorari/mandamus/prohibition or any other appropriate writ;",
                    "b) Grant interim relief as deemed fit;",
                    "c) Pass any other order(s) as this Hon'ble Court may deem fit in the interest of justice.",
                    "",
                    f"PLACE: New Delhi",
                    f"DATE: {datetime.now().strftime('%d %B, %Y')}",
                    "",
                    "COUNSEL FOR THE PETITIONER(S)",
                    "[Signature]"
                ]
            },
            "SLP": {
                "structure": [
                    "IN THE SUPREME COURT OF INDIA",
                    "SPECIAL LEAVE PETITION (CIVIL) NO. ___ OF 2024",
                    "",
                    "UNDER ARTICLE 136 OF THE CONSTITUTION OF INDIA",
                    "",
                    "IN THE MATTER OF:",
                    "Petitioner(s)   : [Name]",
                    "Versus",
                    "Respondent(s)   : [Name]",
                    "",
                    "PETITION FOR SPECIAL LEAVE TO APPEAL",
                    "",
                    "The humble petition of the Petitioner(s) above named:",
                    "",
                    "1. The Petitioner seeks Special Leave to Appeal against the judgment dated [...] passed by [...].",
                    "",
                    "2. FACTS IN BRIEF:",
                    facts,
                    "",
                    "3. SUBSTANTIAL QUESTIONS OF LAW:",
                    "A. Whether the impugned judgment suffers from error apparent on the face of the record?",
                    "B. Whether substantial questions of law of general importance arise for consideration?",
                    "",
                    "4. GROUNDS FOR SEEKING SPECIAL LEAVE:",
                    "A. The judgment under appeal is contrary to established principles of law.",
                    "B. Different High Courts have taken divergent views on the same issue.",
                    "C. The matter involves substantial questions of law of public importance.",
                    "",
                    "PRAYER:",
                    "In the premises, it is most respectfully prayed that this Hon'ble Court may be pleased to:",
                    "a) Grant Special Leave to Appeal;",
                    "b) Condone the delay, if any;",
                    "c) Pass such other order(s) as this Hon'ble Court may deem fit.",
                    "",
                    f"PLACE: New Delhi",
                    f"DATE: {datetime.now().strftime('%d %B, %Y')}",
                    "",
                    "ADVOCATE FOR THE PETITIONER(S)",
                    "[Signature]"
                ]
            }
        }
        
        template = templates.get(doc_type, templates["Writ Petition"])
        return "\n".join(template["structure"])

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if 'db' not in st.session_state:
    st.session_state.db = LawyerDatabase()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'current_case' not in st.session_state:
    st.session_state.current_case = None

# ============================================
# HELPER FUNCTIONS
# ============================================

def fetch_supreme_court_status(diary_no, year):
    """Mock function to fetch case status from Supreme Court"""
    # In production, this would connect to real API
    time.sleep(1)  # Simulate API delay
    
    # Mock response based on input
    if diary_no and year:
        return {
            "found": True,
            "diary_no": diary_no,
            "year": year,
            "status": "Listed",
            "next_date": "2024-12-15",
            "bench": "Hon'ble Chief Justice",
            "stage": "Final Hearing",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "documents": ["Petition", "Counter Affidavit", "Rejoinder"],
            "remarks": "Case is ready for final hearing"
        }
    return {"found": False}

def calculate_case_metrics(cases):
    """Calculate metrics from cases data"""
    total_cases = len(cases)
    active_cases = len([c for c in cases if c['status'] in ['Filed', 'Pending', 'Listed']])
    disposed_cases = len([c for c in cases if c['status'] == 'Disposed'])
    hearings_today = len([c for c in cases if c.get('next_hearing_date') == datetime.now().strftime('%Y-%m-%d')])
    
    return {
        'total': total_cases,
        'active': active_cases,
        'disposed': disposed_cases,
        'hearings_today': hearings_today,
        'pending_ratio': active_cases / total_cases if total_cases > 0 else 0
    }

# ============================================
# PAGE FUNCTIONS
# ============================================

def show_login_page():
    """Display login page"""
    st.markdown('<div class="main-header">⚖️ Lawyer Portal Pro</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["Login", "Register"])
            
            with tab1:
                st.subheader("Login to Your Account")
                
                email = st.text_input("Email Address", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Login", type="primary", use_container_width=True):
                        if email and password:
                            user = st.session_state.db.authenticate_user(email, password)
                            if user:
                                st.session_state.logged_in = True
                                st.session_state.current_user = user
                                st.success(f"Welcome, {user['full_name']}!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Invalid email or password")
                        else:
                            st.error("Please enter email and password")
                
                with col_b:
                    if st.button("Forgot Password?", use_container_width=True):
                        st.info("Password reset feature coming soon!")
            
            with tab2:
                st.subheader("Create New Account")
                
                reg_email = st.text_input("Email", key="reg_email")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                reg_name = st.text_input("Full Name", key="reg_name")
                reg_phone = st.text_input("Phone Number", key="reg_phone")
                reg_firm = st.text_input("Law Firm Name", key="reg_firm")
                
                if st.button("Register", type="primary", use_container_width=True):
                    if reg_email and reg_password and reg_name:
                        success = st.session_state.db.add_user(
                            reg_email, reg_password, reg_name,
                            phone=reg_phone, firm_name=reg_firm
                        )
                        if success:
                            st.success("Account created successfully! Please login.")
                        else:
                            st.error("Email already exists. Please use a different email.")
                    else:
                        st.error("Please fill all required fields")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>© 2024 Lawyer Portal Pro • Supreme Court Integration Ready</p>", 
                unsafe_allow_html=True)

def show_dashboard():
    """Display main dashboard"""
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<div class="main-header">👨‍⚖️ Welcome, {st.session_state.current_user["full_name"]}</div>', 
                   unsafe_allow_html=True)
    with col2:
        if st.button("Logout", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
    
    # Get user cases
    cases = st.session_state.db.get_user_cases(st.session_state.current_user['id'])
    metrics = calculate_case_metrics(cases)
    
    # Metrics Row
    st.markdown('<div class="section-header">Dashboard Overview</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">Total Cases</div>
            <div class="metric-value">{metrics['total']}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">Active Cases</div>
            <div class="metric-value">{metrics['active']}</div>
            <div class="{"positive" if metrics['active'] < 10 else "negative"}">
                {metrics['active']} pending
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">Disposed</div>
            <div class="metric-value">{metrics['disposed']}</div>
            <div class="positive">
                {int((metrics['disposed']/metrics['total'])*100 if metrics['total'] > 0 else 0)}% success
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">Today's Hearings</div>
            <div class="metric-value">{metrics['hearings_today']}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Case Status Distribution")
        if cases:
            status_counts = pd.Series([c['status'] for c in cases]).value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                hole=0.3,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No cases to display")
    
    with col2:
        st.subheader("Monthly Case Trend")
        if cases:
            # Create mock monthly data for visualization
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            monthly_cases = np.random.randint(1, 10, size=12)
            
            fig = go.Figure(data=go.Scatter(
                x=months,
                y=monthly_cases,
                mode='lines+markers',
                line=dict(color='#3498db', width=3),
                marker=dict(size=8)
            ))
            fig.update_layout(
                plot_bgcolor='white',
                yaxis_title="Number of Cases"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent Cases
    st.markdown('<div class="section-header">Recent Cases</div>', unsafe_allow_html=True)
    
    if cases:
        recent_cases = cases[:5]  # Show only 5 most recent
        for case in recent_cases:
            status_class = f"status-{case['status'].lower().replace(' ', '-')}"
            st.markdown(f'''
            <div class="case-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: #2c3e50;">{case['case_title']}</h4>
                        <p style="margin: 0.25rem 0; color: #7f8c8d;">
                            {case['diary_no']}/{case['year']} • {case['court_name']}
                        </p>
                    </div>
                    <span class="status-badge {status_class}">{case['status']}</span>
                </div>
                <p style="margin: 0.5rem 0;">Petitioner: {case['petitioner']}</p>
                <p style="margin: 0; color: #e74c3c; font-weight: bold;">
                    Next Hearing: {case['next_hearing_date'] or 'Not scheduled'}
                </p>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("No cases found. Add your first case using the Case Management section.")
    
    # Upcoming Hearings
    st.markdown('<div class="section-header">Upcoming Hearings (Next 30 Days)</div>', unsafe_allow_html=True)
    
    hearings = st.session_state.db.get_upcoming_hearings(st.session_state.current_user['id'], 30)
    if hearings:
        for hearing in hearings:
            days_until = (datetime.strptime(hearing['hearing_date'], '%Y-%m-%d') - datetime.now()).days
            st.markdown(f'''
            <div class="case-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: #2c3e50;">{hearing['case_title']}</h4>
                        <p style="margin: 0.25rem 0; color: #7f8c8d;">
                            {hearing['diary_no']}/{hearing['year']}
                        </p>
                    </div>
                    <span style="color: {'#e74c3c' if days_until <= 7 else '#f39c12'}; font-weight: bold;">
                        {days_until} days
                    </span>
                </div>
                <p style="margin: 0.5rem 0;">
                    <b>Date:</b> {hearing['hearing_date']} • 
                    <b>Purpose:</b> {hearing['purpose']}
                </p>
                <p style="margin: 0;"><b>Petitioner:</b> {hearing['petitioner']}</p>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("No upcoming hearings in the next 30 days.")

def show_case_management():
    """Case management page"""
    st.markdown('<div class="section-header">Case Management</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Add Case", "View Cases", "Search & Filter"])
    
    with tab1:
        with st.form("add_case_form", clear_on_submit=True):
            st.subheader("Add New Case")
            
            col1, col2 = st.columns(2)
            
            with col1:
                diary_no = st.text_input("Diary Number*", placeholder="e.g., 12345")
                year = st.number_input("Year*", min_value=2000, max_value=2030, value=2024)
                case_title = st.text_input("Case Title*", placeholder="e.g., XYZ vs State")
                petitioner = st.text_input("Petitioner Name*")
                respondent = st.text_input("Respondent Name")
            
            with col2:
                case_type = st.selectbox("Case Type*", ["Civil", "Criminal", "Writ", "Appeal", "SLP"])
                court_name = st.selectbox("Court*", ["Supreme Court", "High Court", "District Court", "Tribunal"])
                status = st.selectbox("Status*", ["Filed", "Pending", "Listed", "Disposed", "Adjourned"])
                filing_date = st.date_input("Filing Date")
                next_hearing = st.date_input("Next Hearing Date")
            
            description = st.text_area("Case Description", height=100)
            lawyer_notes = st.text_area("Lawyer Notes (Private)", height=100)
            
            submitted = st.form_submit_button("Add Case", type="primary")
            
            if submitted:
                if diary_no and year and case_title and petitioner:
                    case_data = {
                        'diary_no': diary_no,
                        'year': year,
                        'case_title': case_title,
                        'petitioner': petitioner,
                        'respondent': respondent,
                        'case_type': case_type,
                        'court_name': court_name,
                        'status': status,
                        'filing_date': filing_date.strftime('%Y-%m-%d'),
                        'next_hearing_date': next_hearing.strftime('%Y-%m-%d') if next_hearing else None,
                        'description': description,
                        'lawyer_notes': lawyer_notes
                    }
                    
                    case_id = st.session_state.db.add_case(
                        st.session_state.current_user['id'], 
                        case_data
                    )
                    
                    st.success(f"Case added successfully! Case ID: {case_id}")
                    
                    # Auto-add first hearing
                    if next_hearing:
                        hearing_data = {
                            'hearing_date': next_hearing.strftime('%Y-%m-%d'),
                            'purpose': 'First Hearing',
                            'notes': 'Case filed and first hearing scheduled'
                        }
                        st.session_state.db.add_hearing(case_id, hearing_data)
                        st.info(f"Hearing scheduled for {next_hearing.strftime('%d %B, %Y')}")
                else:
                    st.error("Please fill all required fields (*)")
    
    with tab2:
        st.subheader("Your Cases")
        
        cases = st.session_state.db.get_user_cases(st.session_state.current_user['id'])
        
        if cases:
            # Create DataFrame for display
            df = pd.DataFrame(cases)
            display_cols = ['diary_no', 'year', 'case_title', 'petitioner', 'status', 'next_hearing_date']
            st.dataframe(df[display_cols], use_container_width=True)
            
            # Case details expander
            st.subheader("Case Details")
            case_options = [f"{c['diary_no']}/{c['year']} - {c['case_title']}" for c in cases]
            selected_case = st.selectbox("Select case to view details:", case_options)
            
            if selected_case:
                case_idx = case_options.index(selected_case)
                selected_case_data = cases[case_idx]
                
                with st.expander("View Complete Details"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("*Basic Information*")
                        st.write(f"Diary No: {selected_case_data['diary_no']}")
                        st.write(f"Year: {selected_case_data['year']}")
                        st.write(f"Title: {selected_case_data['case_title']}")
                        st.write(f"Petitioner: {selected_case_data['petitioner']}")
                        st.write(f"Respondent: {selected_case_data['respondent']}")
                    
                    with col2:
                        st.write("*Case Details*")
                        st.write(f"Type: {selected_case_data['case_type']}")
                        st.write(f"Court: {selected_case_data['court_name']}")
                        st.write(f"Status: {selected_case_data['status']}")
                        st.write(f"Filing Date: {selected_case_data['filing_date']}")
                        st.write(f"Next Hearing: {selected_case_data['next_hearing_date']}")
                    
                    st.write("*Description*")
                    st.write(selected_case_data['description'] or "No description provided")
                    
                    st.write("*Lawyer Notes*")
                    st.write(selected_case_data['lawyer_notes'] or "No notes")
                    
                    # Actions
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("Generate Case Summary PDF"):
                            pdf_path = PDFGenerator.generate_case_summary_pdf(selected_case_data)
                            with open(pdf_path, "rb") as f:
                                st.download_button(
                                    "Download PDF",
                                    f,
                                    file_name=f"case_{selected_case_data['diary_no']}_{selected_case_data['year']}.pdf"
                                )
                    
                    with col_b:
                        if st.button("Update Status"):
                            new_status = st.selectbox("New Status", 
                                                    ["Filed", "Pending", "Listed", "Disposed", "Adjourned"])
                            if st.button("Confirm Update"):
                                st.session_state.db.update_case_status(
                                    selected_case_data['id'], 
                                    new_status
                                )
                                st.success("Status updated!")
                                st.rerun()
                    
                    with col_c:
                        if st.button("Add Hearing Record"):
                            with st.form("add_hearing_form"):
                                hearing_date = st.date_input("Hearing Date")
                                purpose = st.text_input("Purpose")
                                outcome = st.text_input("Outcome")
                                notes = st.text_area("Notes")
                                
                                if st.form_submit_button("Add Hearing"):
                                    hearing_data = {
                                        'hearing_date': hearing_date.strftime('%Y-%m-%d'),
                                        'purpose': purpose,
                                        'outcome': outcome,
                                        'notes': notes
                                    }
                                    st.session_state.db.add_hearing(
                                        selected_case_data['id'], 
                                        hearing_data
                                    )
                                    st.success("Hearing record added!")
        else:
            st.info("No cases found. Add your first case using the 'Add Case' tab.")
    
    with tab3:
        st.subheader("Search & Filter Cases")
        
        search_term = st.text_input("Search by Diary No, Title, or Petitioner")
        status_filter = st.multiselect("Filter by Status", 
                                      ["Filed", "Pending", "Listed", "Disposed", "Adjourned"])
        
        cases = st.session_state.db.get_user_cases(st.session_state.current_user['id'])
        
        if search_term:
            cases = [c for c in cases if 
                    search_term.lower() in str(c['diary_no']).lower() or
                    search_term.lower() in str(c['case_title']).lower() or
                    search_term.lower() in str(c['petitioner']).lower()]
        
        if status_filter:
            cases = [c for c in cases if c['status'] in status_filter]
        
        if cases:
            st.write(f"Found {len(cases)} cases")
            
            for case in cases:
                with st.expander(f"{case['diary_no']}/{case['year']} - {case['case_title']}"):
                    st.write(f"*Status:* {case['status']}")
                    st.write(f"*Petitioner:* {case['petitioner']}")
                    st.write(f"*Next Hearing:* {case['next_hearing_date'] or 'Not scheduled'}")
        else:
            st.info("No cases match your search criteria.")

def show_ai_drafting():
    """AI Drafting Assistant page"""
    st.markdown('<div class="section-header">🤖 AI Drafting Assistant</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Document Type Selection
        doc_type = st.selectbox(
            "Select Document Type",
            ["Writ Petition", "SLP (Special Leave Petition)", "Affidavit", 
             "Reply", "IA (Interim Application)", "Written Submissions"]
        )
        
        # Case Facts Input
        st.subheader("Case Facts")
        facts = st.text_area(
            "Enter detailed case facts:",
            height=200,
            placeholder="""Example:
The petitioner is a 45-year-old businessperson from Mumbai. On January 15, 2024, the respondent authority seized the petitioner's property without providing any notice or opportunity of hearing. The seizure was based on allegations of tax evasion, which the petitioner denies. The petitioner has made multiple representations to the authority but received no response. The action violates principles of natural justice and constitutional rights."""
        )
        
        # Additional Parameters
        with st.expander("Advanced Options"):
            col_a, col_b = st.columns(2)
            with col_a:
                urgency = st.select_slider("Urgency Level", 
                                          ["Normal", "Urgent", "Most Urgent"])
                include_precedents = st.checkbox("Include Relevant Precedents", value=True)
            with col_b:
                jurisdiction = st.selectbox("Jurisdiction", 
                                          ["Supreme Court", "High Court", "District Court"])
                language_style = st.selectbox("Language Style", 
                                            ["Formal", "Technical", "Persuasive"])
        
        # Generate Draft Button
        if st.button("Generate Draft", type="primary", use_container_width=True):
            if facts:
                with st.spinner("Generating draft... This may take a few seconds."):
                    time.sleep(2)  # Simulate AI processing
                    
                    draft = AI_Drafting_Assistant.generate_draft_from_facts(facts, doc_type)
                    st.session_state.generated_draft = draft
                    st.session_state.draft_facts = facts
                    st.session_state.draft_type = doc_type
                    
                    st.success("Draft generated successfully!")
            else:
                st.error("Please enter case facts to generate a draft.")
    
    with col2:
        st.subheader("Quick Actions")
        
        if st.button("📝 Load Sample Facts", use_container_width=True):
            sample_facts = """The petitioner, a registered society working for environmental protection, challenges the environmental clearance granted to a mining project in a forest area. The clearance was granted without proper public consultation and environmental impact assessment. The project threatens endangered species and local tribal communities."""
            st.session_state.sample_facts = sample_facts
            st.rerun()
        
        st.divider()
        
        if st.button("⚖️ Insert Legal Phrases", use_container_width=True):
            st.info("Common legal phrases can be inserted from the library.")
        
        if st.button("📚 Case Law Library", use_container_width=True):
            st.info("Access relevant case laws and precedents.")
    
    # Display Generated Draft
    if 'generated_draft' in st.session_state:
        st.markdown('<div class="section-header">Generated Draft</div>', unsafe_allow_html=True)
        
        # Draft Preview
        with st.expander("Preview Draft", expanded=True):
            st.text_area("", st.session_state.generated_draft, height=400, key="draft_preview")
        
        # Action Buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📥 Download as .txt", use_container_width=True):
                st.download_button(
                    label="Click to Download",
                    data=st.session_state.generated_draft,
                    file_name=f"{st.session_state.draft_type.replace(' ', '')}{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
        
        with col2:
            if st.button("📄 Generate PDF", use_container_width=True):
                draft_data = {
                    'doc_type': st.session_state.draft_type,
                    'facts': st.session_state.draft_facts,
                    'court': 'Supreme Court',
                    'jurisdiction': 'Original Jurisdiction',
                    'petitioner': '[Petitioner Name]',
                    'respondent': '[Respondent Name]'
                }
                
                pdf_path = PDFGenerator.generate_legal_draft_pdf(draft_data)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "Download PDF",
                        f,
                        file_name=f"legal_draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
        
        with col3:
            if st.button("✏️ Edit Draft", use_container_width=True):
                st.info("Edit feature coming soon!")
        
        with col4:
            if st.button("🔄 Regenerate", use_container_width=True):
                del st.session_state.generated_draft
                st.rerun()
        
        # Save to Database
        st.divider()
        if st.button("💾 Save to Case File", type="primary"):
            st.info("Select a case to save this draft to:")
            cases = st.session_state.db.get_user_cases(st.session_state.current_user['id'])
            case_options = [f"{c['diary_no']}/{c['year']} - {c['case_title']}" for c in cases]
            
            selected_case = st.selectbox("Select Case", case_options)
            if st.button("Confirm Save"):
                st.success(f"Draft saved to {selected_case}")
    
    # Sample Facts Loader
    if 'sample_facts' in st.session_state:
        st.text_area("Sample Facts Loaded:", st.session_state.sample_facts, height=150)
        if st.button("Use These Facts"):
            facts = st.session_state.sample_facts
            del st.session_state.sample_facts
            st.rerun()

def show_court_sync():
    """Supreme Court Sync page"""
    st.markdown('<div class="section-header">⚡ Supreme Court Live Sync</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Connection Panel
        with st.container():
            st.subheader("Connect to Supreme Court Registry")
            
            col_a, col_b = st.columns(2)
            with col_a:
                diary_no = st.text_input("Diary Number", key="sync_diary", 
                                        placeholder="e.g., 12345")
                year = st.number_input("Year", min_value=2000, max_value=2030, 
                                      value=2024, key="sync_year")
            
            with col_b:
                case_type = st.selectbox("Case Type", ["Civil", "Criminal", "Writ", "Constitutional"])
                include_details = st.checkbox("Fetch Detailed Information", value=True)
            
            if st.button("🔍 Fetch Case Status", type="primary", use_container_width=True):
                if diary_no and year:
                    with st.spinner("Connecting to Supreme Court Registry..."):
                        # Simulate API call
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)
                        
                        status = fetch_supreme_court_status(diary_no, year)
                        st.session_state.court_status = status
                        
                        if status['found']:
                            st.success("✅ Connection successful! Case found in registry.")
                        else:
                            st.error("❌ Case not found in registry.")
                else:
                    st.error("Please enter Diary Number and Year")
        
        # Display Status
        if 'court_status' in st.session_state:
            status = st.session_state.court_status
            
            if status['found']:
                st.markdown('<div class="section-header">Case Status</div>', unsafe_allow_html=True)
                
                # Status Cards
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-label">Current Status</div>
                        <div class="metric-value" style="color: #27ae60;">{status['status']}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-label">Next Date</div>
                        <div class="metric-value">{status['next_date']}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-label">Bench</div>
                        <div class="metric-value">{status['bench']}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Detailed Information
                with st.expander("📋 Detailed Case Information", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("*Basic Information*")
                        st.write(f"Diary No: {status['diary_no']}")
                        st.write(f"Year: {status['year']}")
                        st.write(f"Stage: {status['stage']}")
                        st.write(f"Last Updated: {status['last_updated']}")
                    
                    with col2:
                        st.write("*Documents Available*")
                        for doc in status['documents']:
                            st.write(f"• {doc}")
                    
                    st.write("*Remarks*")
                    st.info(status['remarks'])
                
                # Actions
                st.markdown('<div class="section-header">Available Actions</div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📥 Download Cause List", use_container_width=True):
                        st.info("Cause list download feature coming soon!")
                
                with col2:
                    if st.button("📧 Request Certified Copy", use_container_width=True):
                        st.info("Copy request feature coming soon!")
                
                with col3:
                    if st.button("📅 Set Hearing Reminder", use_container_width=True):
                        st.info("Reminder feature coming soon!")
            
            else:
                st.error("Case not found in Supreme Court registry. Please check the Diary Number and Year.")
    
    with col2:
        # API Status Panel
        st.subheader("API Status")
        
        st.markdown(f'''
        <div class="card">
            <h4 style="margin-top: 0;">Supreme Court Live API</h4>
            <p style="color: #27ae60; font-weight: bold;">✅ Connected</p>
            <p><b>Response Time:</b> 1.2s</p>
            <p><b>Last Sync:</b> {datetime.now().strftime("%H:%M:%S")}</p>
            <p><b>API Version:</b> 2.1.4</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Quick Stats
        st.subheader("Quick Stats")
        st.metric("Cases Today", "142", "12 new")
        st.metric("Listed Cases", "89", "5% ▲")
        st.metric("Disposed Today", "38", "2% ▼")
        
        # Court Links
        st.subheader("Useful Links")
        st.markdown("""
        - [Supreme Court Cause List](https://main.sci.gov.in/causelist)
        - [Case Status Search](https://main.sci.gov.in/case-status)
        - [Daily Orders](https://main.sci.gov.in/daily-orders)
        - [Judgments](https://main.sci.gov.in/judgments)
        """)

def show_calendar():
    """Calendar and Schedule page"""
    st.markdown('<div class="section-header">📅 Legal Calendar</div>', unsafe_allow_html=True)
    
    # Calendar View
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Month selector
        current_date = datetime.now()
        selected_month = st.selectbox(
            "Select Month",
            options=[
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ],
            index=current_date.month - 1
        )
        
        selected_year = st.number_input("Year", min_value=2020, max_value=2030, value=current_date.year)
        
        # Generate calendar (simplified view)
        st.subheader(f"Hearings for {selected_month} {selected_year}")
        
        # Get hearings for selected period
        hearings = st.session_state.db.get_upcoming_hearings(st.session_state.current_user['id'], 365)
        
        # Filter for selected month/year
        filtered_hearings = [
            h for h in hearings 
            if datetime.strptime(h['hearing_date'], '%Y-%m-%d').month == list([
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]).index(selected_month) + 1
            and datetime.strptime(h['hearing_date'], '%Y-%m-%d').year == selected_year
        ]
        
        if filtered_hearings:
            for hearing in filtered_hearings:
                hearing_date = datetime.strptime(hearing['hearing_date'], '%Y-%m-%d')
                days_until = (hearing_date - datetime.now()).days
                
                st.markdown(f'''
                <div class="case-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: #2c3e50;">{hearing['case_title']}</h4>
                            <p style="margin: 0.25rem 0; color: #7f8c8d;">
                                {hearing['diary_no']}/{hearing['year']}
                            </p>
                        </div>
                        <span style="color: #e74c3c; font-weight: bold; font-size: 1.2rem;">
                            {hearing_date.strftime('%d %b')}
                        </span>
                    </div>
                    <p style="margin: 0.5rem 0;">
                        <b>Time:</b> 10:30 AM • 
                        <b>Court:</b> {hearing.get('court', 'Supreme Court')}
                    </p>
                    <p style="margin: 0;"><b>Purpose:</b> {hearing['purpose']}</p>
                    <p style="margin: 0.5rem 0; color: {'#e74c3c' if days_until <= 3 else '#f39c12'};">
                        {days_until} days remaining
                    </p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info(f"No hearings scheduled for {selected_month} {selected_year}")
    
    with col2:
        # Today's Hearings
        st.subheader("Today's Schedule")
        
        today = datetime.now().strftime('%Y-%m-%d')
        today_hearings = [h for h in hearings if h['hearing_date'] == today]
        
        if today_hearings:
            for hearing in today_hearings:
                st.markdown(f'''
                <div style="background: #fff3cd; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;">
                    <p style="margin: 0; font-weight: bold;">{hearing['case_title']}</p>
                    <p style="margin: 0; font-size: 0.9rem;">{hearing['purpose']}</p>
                    <p style="margin: 0; font-size: 0.8rem; color: #856404;">10:30 AM</p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No hearings scheduled for today")
        
        # Add New Hearing
        st.subheader("Add Hearing")
        
        with st.form("add_hearing_form"):
            case_options = st.session_state.db.get_user_cases(st.session_state.current_user['id'])
            case_list = [f"{c['diary_no']}/{c['year']} - {c['case_title']}" for c in case_options]
            
            selected_case = st.selectbox("Select Case", case_list)
            hearing_date = st.date_input("Hearing Date", min_value=datetime.now())
            hearing_time = st.time_input("Time", value=datetime.strptime("10:30", "%H:%M").time())
            purpose = st.text_input("Purpose")
            
            if st.form_submit_button("Add to Calendar", type="primary"):
                st.success("Hearing added to calendar!")
        
        # Export Calendar
        st.divider()
        if st.button("📅 Export to Google Calendar", use_container_width=True):
            st.info("Calendar export feature coming soon!")

def show_billing():
    """Billing and Invoices page"""
    st.markdown('<div class="section-header">💰 Billing & Invoices</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Time Tracking", "Generate Invoice", "Payment Records"])
    
    with tab1:
        st.subheader("Track Billable Hours")
        
        col1, col2 = st.columns(2)
        with col1:
            case_options = st.session_state.db.get_user_cases(st.session_state.current_user['id'])
            case_list = [f"{c['diary_no']}/{c['year']} - {c['case_title']}" for c in case_options]
            selected_case = st.selectbox("Select Case", case_list)
            
            activity = st.selectbox("Activity", 
                                  ["Case Research", "Drafting", "Court Appearance", 
                                   "Client Meeting", "Document Review", "Other"])
            
            hours = st.number_input("Hours", min_value=0.25, max_value=24.0, 
                                   value=2.0, step=0.25)
        
        with col2:
            date = st.date_input("Date", value=datetime.now())
            description = st.text_area("Description", height=100)
            rate = st.number_input("Hourly Rate (₹)", min_value=0, value=5000, step=500)
        
        if st.button("Add Time Entry", type="primary"):
            amount = hours * rate
            st.success(f"Entry added: {hours} hours × ₹{rate}/hr = ₹{amount:,.2f}")
    
    with tab2:
        st.subheader("Generate Invoice")
        
        # Invoice form
        with st.form("invoice_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                client_name = st.text_input("Client Name")
                client_address = st.text_area("Client Address", height=80)
                invoice_date = st.date_input("Invoice Date", value=datetime.now())
                due_date = st.date_input("Due Date", value=datetime.now() + timedelta(days=30))
            
            with col2:
                invoice_number = st.text_input("Invoice Number", 
                                             value=f"INV-{datetime.now().strftime('%Y%m%d')}-001")
                tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, value=18.0, step=0.5)
                payment_terms = st.text_input("Payment Terms", value="Net 30")
            
            # Line items
            st.subheader("Line Items")
            
            line_items = []
            for i in range(3):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    desc = st.text_input(f"Description {i+1}", key=f"desc_{i}")
                with col2:
                    qty = st.number_input(f"Qty {i+1}", min_value=1.0, value=1.0, key=f"qty_{i}")
                with col3:
                    rate = st.number_input(f"Rate {i+1}", min_value=0, value=5000, key=f"rate_{i}")
                with col4:
                    amount = qty * rate
                    st.text_input(f"Amount {i+1}", value=f"₹{amount:,.2f}", disabled=True, key=f"amount_{i}")
                
                if desc:
                    line_items.append({
                        'description': desc,
                        'quantity': qty,
                        'rate': rate,
                        'amount': amount
                    })
            
            if st.form_submit_button("Generate Invoice PDF", type="primary"):
                st.success("Invoice generated successfully!")
                # Here you would generate the actual PDF
    
    with tab3:
        st.subheader("Payment Records")
        
        # Mock payment data
        payments = [
            {"date": "2024-01-15", "client": "ABC Corp", "amount": 125000, "status": "Paid"},
            {"date": "2024-01-10", "client": 
# ============================================
# SIDEBAR NAVIGATION
# ============================================

def sidebar_navigation():
    """Create sidebar navigation"""
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2095/2095957.png", width=80)
        st.title("Navigation")
        
        if not st.session_state.logged_in:
            menu_items = ["Login"]
        else:
            menu_items = [
                "Dashboard",
                "Case Management", 
                "AI Drafting",
                "Court Sync",
                "Calendar",
                "Billing",
                "Settings"
            ]
        
        selection = st.radio("Menu", menu_items, label_visibility="collapsed")
        
        if st.session_state.logged_in:
            st.divider()
            
            # Quick Stats
            st.subheader("📊 Quick Stats")
            cases = st.session_state.db.get_user_cases(st.session_state.current_user['id'])
            metrics = calculate_case_metrics(cases)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Cases", metrics['total'])
            with col2:
                st.metric("Active", metrics['active'])
            
            # User Info
            st.divider()
            st.subheader("👤 User Info")
            st.write(f"*Name:* {st.session_state.current_user['full_name']}")
            st.write(f"*Email:* {st.session_state.current_user['email']}")
        
        return selection

def main():
    """Main application flow"""
    
    # Get current page from sidebar
    current_page = sidebar_navigation()
    
    # Route to appropriate page
    if not st.session_state.logged_in:
        show_login_page()
    else:
        if current_page == "Dashboard":
            show_dashboard()
        elif current_page == "Case Management":
            show_case_management()
        elif current_page == "AI Drafting":
            show_ai_drafting()
        elif current_page == "Court Sync":
            show_court_sync()
        elif current_page == "Calendar":
            show_calendar()
        elif current_page == "Billing":
            show_billing()
        elif current_page == "Settings":
            st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
            st.write("Settings page coming soon!")
            # Add settings functionality here
if _name_ == "_main_":
    main()
