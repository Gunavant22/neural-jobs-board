import streamlit as st
import requests
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
import os
import pandas as pd
import PyPDF2
import uuid
import json
import zipfile
import io
import urllib.parse
import ssl
import secrets
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta

try:
    import google.generativeai as genai
except ImportError:
    pass

# ==========================================
# 1. PRODUCTION CONFIGURATION & SECRETS
# ==========================================
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]
ADMIN_EMAILS = [st.secrets["ADMIN_EMAIL"]]
DB_CONN_STR = st.secrets["DB_CONNECTION_STRING"]
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ==========================================
# 2. FUTURISTIC UI & ANIMATIONS
# ==========================================
st.set_page_config(page_title="NEURAL // Jobs", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

def apply_futuristic_css():
    css = """
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
    * { font-family: 'Outfit', sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #050810; background-image: linear-gradient(rgba(0, 242, 254, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 242, 254, 0.03) 1px, transparent 1px); background-size: 30px 30px; background-position: center center; }
    .login-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 5vh; animation: float 6s ease-in-out infinite; }
    @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0px); } }
    .login-card { background: linear-gradient(145deg, rgba(15, 23, 42, 0.7) 0%, rgba(20, 20, 30, 0.5) 100%); border: 1px solid rgba(0, 242, 254, 0.3); border-radius: 20px; padding: 40px 30px; box-shadow: 0 0 40px rgba(0, 242, 254, 0.1); text-align: center; backdrop-filter: blur(16px); width: 100%; max-width: 500px; transition: all 0.5s ease;}
    .maintenance-card { border: 1px solid rgba(255, 71, 87, 0.5) !important; box-shadow: 0 0 50px rgba(255, 71, 87, 0.2) !important; }
    .app-title-large { font-size: 3rem; font-weight: 900; background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #b06ab3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0px 0px 25px rgba(0, 242, 254, 0.5); letter-spacing: -2px; margin-bottom: 5px; line-height: 1.1; }
    .app-title-maintenance { color: #ff4757 !important; background: none !important; -webkit-text-fill-color: #ff4757 !important; text-shadow: 0px 0px 25px rgba(255, 71, 87, 0.8) !important;}
    .system-status { font-family: 'Share Tech Mono', monospace; color: #00ffcc; font-size: 0.8rem; margin-bottom: 15px; animation: blink 2s linear infinite; }
    .system-status-offline { color: #ff4757 !important; text-shadow: 0 0 10px #ff4757 !important; }
    @keyframes blink { 0%, 100% { opacity: 1; text-shadow: 0 0 10px #00ffcc; } 50% { opacity: 0.4; text-shadow: none; } }
    .cyber-btn { position: relative; z-index: 999; cursor: pointer; display: inline-block; margin-top: 20px; padding: 15px 40px; background: rgba(0, 242, 254, 0.1); color: #00f2fe !important; font-family: 'Share Tech Mono', monospace; font-size: 1.2rem; font-weight: bold; text-decoration: none; border: 1px solid #00f2fe; border-radius: 4px; text-transform: uppercase; letter-spacing: 2px; transition: all 0.3s ease; box-shadow: inset 0 0 10px rgba(0, 242, 254, 0.1), 0 0 15px rgba(0, 242, 254, 0.2); }
    .cyber-btn:hover { background: #00f2fe; color: #050810 !important; box-shadow: 0 0 30px rgba(0, 242, 254, 0.8); transform: scale(1.05); }
    .admin-bypass-btn { margin-top: 15px; font-size: 0.8rem !important; border: 1px solid #ff4757 !important; color: #ff4757 !important; background: transparent !important; box-shadow: none !important;}
    .admin-bypass-btn:hover { background: #ff4757 !important; color: white !important; box-shadow: 0 0 20px #ff4757 !important; }
    .app-title-small { font-size: 2.5rem; font-weight: 900; background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #b06ab3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0px 0px 15px rgba(0, 242, 254, 0.3); margin-bottom: 0px; text-transform: uppercase; }
    .cyber-warning-banner { background: rgba(255, 165, 2, 0.1); border: 1px solid #ffa502; color: #ffa502; padding: 12px; border-radius: 5px; text-align: center; font-family: 'Share Tech Mono', monospace; font-weight: bold; margin-bottom: 20px; box-shadow: 0 0 10px rgba(255, 165, 2, 0.2); animation: pulse-warn 2s infinite; letter-spacing: 1px;}
    @keyframes pulse-warn { 0% { box-shadow: 0 0 10px rgba(255, 165, 2, 0.2); } 50% { box-shadow: 0 0 20px rgba(255, 165, 2, 0.5); } 100% { box-shadow: 0 0 10px rgba(255, 165, 2, 0.2); } }
    [data-testid="stVerticalBlockBorderWrapper"] { border-radius: 12px !important; border: 1px solid rgba(0, 242, 254, 0.15) !important; background: rgba(15, 23, 42, 0.4) !important; backdrop-filter: blur(10px) !important; transition: all 0.2s ease-in-out; margin-bottom: 15px; }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { border: 1px solid rgba(0, 242, 254, 0.5) !important; box-shadow: 0 0 20px rgba(0, 242, 254, 0.15); }
    .tech-tag { background: rgba(0, 242, 254, 0.1); color: #00f2fe; padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: 700; border: 1px solid rgba(0, 242, 254, 0.3); margin-right: 8px; font-family: 'Share Tech Mono', monospace;}
    .tech-tag-redacted { background: rgba(255, 71, 87, 0.1); color: #ff4757; padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: 700; border: 1px solid rgba(255, 71, 87, 0.3); margin-right: 8px; font-family: 'Share Tech Mono', monospace;}
    .company-avatar { width: 50px; height: 50px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 2px solid #b06ab3; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: bold; color: #b06ab3; box-shadow: 0 0 15px rgba(176, 106, 179, 0.4); margin: auto; }
    .company-avatar-locked { border: 2px solid #ff4757; color: #ff4757; box-shadow: 0 0 15px rgba(255, 71, 87, 0.4); }
    .stTabs [data-baseweb="tab-list"] { gap: 30px; }
    .stTabs [data-baseweb="tab"] { font-size: 1.1rem; font-weight: 700; color: #8892b0; }
    .stTabs [aria-selected="true"] { color: #00f2fe !important; border-bottom: 2px solid #00f2fe !important; text-shadow: 0 0 10px rgba(0, 242, 254, 0.5); }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

apply_futuristic_css()

# ==========================================
# 3. HELPER FUNCTIONS & POOLED DB ACCESS
# ==========================================
@st.cache_resource
def init_connection_pool():
    """Initializes a shared, multi-threaded connection pool to bypass DB limits."""
    try:
        return ThreadedConnectionPool(minconn=1, maxconn=10, dsn=DB_CONN_STR)
    except Exception as e:
        print(f"DATABASE CONNECTION POOL CRITICAL ERROR: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    """🛠️ CRASH-PROOF & SECURE DB RUNTIME: Uses connection pooling and hides raw SQL traces."""
    pool = init_connection_pool()
    if not pool:
        st.error("Infrastructure Error: Secure connection pool initialization failed.")
        return pd.DataFrame()
        
    try:
        conn = pool.getconn()
    except Exception as e:
        print(f"POOLED DB ERROR (getConnection): {e}")
        st.error("System capacity limit reached. Please try again in a few moments.")
        return pd.DataFrame()
        
    try:
        c = conn.cursor()
        if params: c.execute(query, params)
        else: c.execute(query)
        
        if fetch:
            rows = c.fetchall()
            cols = [desc[0] for desc in c.description] if c.description else []
            conn.commit()
            return pd.DataFrame(rows, columns=cols)
            
        conn.commit()
        return pd.DataFrame()
    except Exception as e:
        conn.rollback()
        # Security: Log raw system/schema issues to backend server logs only
        print(f"SECURE DATABASE CRITICAL EXCEPTION: {e}")
        st.error("A secure network database exception occurred. System Administrators have been notified.")
        return pd.DataFrame()
    finally:
        pool.putconn(conn)

def init_db():
    execute_query('''CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, title TEXT, company TEXT, location TEXT, url TEXT, source TEXT, description TEXT, salary_amount TEXT, salary_type TEXT, date_added TEXT)''')
    execute_query('''CREATE TABLE IF NOT EXISTS sys_settings (id INTEGER PRIMARY KEY, is_maintenance INTEGER, resume_time TEXT, message TEXT, is_warning INTEGER DEFAULT 0, warning_msg TEXT DEFAULT '')''')
    execute_query('''CREATE TABLE IF NOT EXISTS saved_jobs (user_email TEXT, job_id TEXT, PRIMARY KEY (user_email, job_id))''')
    execute_query('''CREATE TABLE IF NOT EXISTS user_resumes (user_email TEXT PRIMARY KEY, resume_data BYTEA, skills_text TEXT, date_uploaded TEXT)''')
    execute_query('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, name TEXT, role TEXT, last_active TEXT, total_logins INTEGER DEFAULT 0)''')
    execute_query("INSERT INTO sys_settings (id, is_maintenance, resume_time, message, is_warning, warning_msg) VALUES (1, 0, '', '', 0, '') ON CONFLICT (id) DO NOTHING")

init_db()

def get_sys_status():
    df = execute_query("SELECT is_maintenance, resume_time, message, is_warning, warning_msg FROM sys_settings WHERE id=1", fetch=True)
    if not df.empty:
        row = df.iloc[0]
        is_maint, res_time, msg, is_warn, warn_msg = row['is_maintenance'], row['resume_time'], row['message'], row['is_warning'], row['warning_msg']
        if is_maint == 1 and res_time and datetime.now() > datetime.strptime(res_time, "%Y-%m-%d %H:%M:%S"):
            execute_query("UPDATE sys_settings SET is_maintenance=0, is_warning=0 WHERE id=1")
            return (0, "", "", 0, "")
        return (is_maint, res_time, msg, is_warn, warn_msg)
    return (0, "", "", 0, "")

def generate_zip_datapack(active_resumes):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for index, cand in active_resumes.iterrows():
            if cand['resume_data'] is not None:
                zip_file.writestr(f"{cand['user_email'].split('@')[0]}_resume.pdf", bytes(cand['resume_data']))
    return zip_buffer.getvalue()

def extract_text_from_pdf(uploaded_file):
    try: return "".join([page.extract_text() + " " for page in PyPDF2.PdfReader(uploaded_file).pages]).lower()
    except: return ""

def format_salary(salary_amount, salary_type):
    """Sanitizes and formats unlisted or misformatted compensation strings."""
    sal_val = str(salary_amount).strip()
    if not sal_val or sal_val.lower() in ["n/a", ""]:
        return "Unlisted"
    if not sal_val.startswith("$"):
        sal_val = f"${sal_val}"
    return f"{sal_val} / {salary_type}"

def display_job_card(row, is_admin=False, user_email=None, is_saved=False, is_teaser=False):
    is_expired = is_admin and pd.to_datetime(row['date_added']) < (pd.to_datetime('today') - timedelta(days=30))
    sal = format_salary(row['salary_amount'], row['salary_type'])
    date_str = str(row['date_added'])[:10]

    if is_teaser:
        with st.container(border=True):
            col_icon, col_details, col_action = st.columns([1, 7, 2])
            with col_icon: st.markdown("<div class='company-avatar company-avatar-locked'>🔒</div>", unsafe_allow_html=True)
            with col_details:
                st.markdown(f"<h3 style='margin-bottom:0px; color:#ffffff;'>{row['title']}</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color:#ff4757; font-size: 1rem; margin-top: 5px;'>[ COMPANY REDACTED ]</p>", unsafe_allow_html=True)
                st.markdown(f"<span class='tech-tag-redacted'>LOC: [ ENCRYPTED ]</span> <span class='tech-tag'>PAY: {sal}</span>", unsafe_allow_html=True)
            with col_action:
                st.write("")
                st.markdown("<p style='color:#8892b0; font-size:0.8rem; text-align:center;'>Log in to decrypt link.</p>", unsafe_allow_html=True)
        return

    # Check for NaN / Empty Company Name to prevent indexing crash
    company_val = str(row['company']).strip() if pd.notna(row['company']) else ""
    avatar_char = company_val[0].upper() if company_val else "X"

    with st.container(border=True):
        col_icon, col_details, col_action = st.columns([1, 7, 2])
        with col_icon: st.markdown(f"<div class='company-avatar'>{avatar_char}</div>", unsafe_allow_html=True)
        with col_details:
            title_html = f"<h3 style='margin-bottom:0px; color:#ff4757;'>[EXPIRED] {row['title']}</h3>" if is_expired else f"<h3 style='margin-bottom:0px; color:#ffffff;'>{row['title']}</h3>"
            st.markdown(title_html, unsafe_allow_html=True)
            st.markdown(f"<p style='color:#8892b0; font-size: 1rem; margin-top: 5px;'>{company_val if company_val else 'Unspecified Entity'}</p>", unsafe_allow_html=True)
            st.markdown(f"<span class='tech-tag'>LOC: {row['location']}</span> <span class='tech-tag'>PAY: {sal}</span> <span class='tech-tag'>DATE: {date_str}</span>", unsafe_allow_html=True)
        with col_action:
            st.write("")
            st.link_button("INITIATE UPLINK", row['url'], use_container_width=True, type="primary")
            if not is_admin and user_email:
                if is_saved:
                    if st.button("❌ REMOVE", key=f"unsave_{row['id']}", use_container_width=True):
                        execute_query("DELETE FROM saved_jobs WHERE user_email=%s AND job_id=%s", (user_email, row['id']))
                        st.rerun()
                else:
                    if st.button("⭐ SAVE NODE", key=f"save_{row['id']}", use_container_width=True):
                        execute_query("INSERT INTO saved_jobs (user_email, job_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (user_email, row['id']))
                        st.rerun()

        with st.expander("DECRYPT DATAFILE (View Description)"):
            st.write(row['description'])

# ==========================================
# 5. STATE MANAGEMENT & SECURE OAUTH
# ==========================================
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_role' not in st.session_state: st.session_state['user_role'] = None
if 'user_name' not in st.session_state: st.session_state['user_name'] = ""
if 'user_email' not in st.session_state: st.session_state['user_email'] = "" 
if 'show_bulk_purge' not in st.session_state: st.session_state['show_bulk_purge'] = False
if 'draft_job' not in st.session_state: st.session_state['draft_job'] = None
if 'last_heartbeat' not in st.session_state: st.session_state['last_heartbeat'] = datetime.min

# Secure State Generation (CSRF Mitigation)
if 'oauth_state' not in st.session_state:
    st.session_state['oauth_state'] = secrets.token_urlsafe(16)

is_maint, res_time, maint_msg, is_warn, warn_msg = get_sys_status()
state_token = st.session_state['oauth_state']
auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=openid%20email%20profile&state={state_token}"

if not st.session_state['logged_in'] and 'code' in st.query_params:
    with st.spinner("Decrypting neural pathways..."):
        returned_state = st.query_params.get("state")
        
        # Verify OAuth state matches local token to block CSRF exploits
        if not returned_state or returned_state != st.session_state['oauth_state']:
            st.error("Authentication security error: state token mismatch (anti-CSRF barrier failed).")
            st.stop()
            
        code = st.query_params['code']
        res = requests.post("https://oauth2.googleapis.com/token", data={"code": code, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "redirect_uri": REDIRECT_URI, "grant_type": "authorization_code"})
        if res.status_code == 200:
            user_data = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {res.json().get('access_token')}"}).json()
            email = user_data.get("email")
            role = "admin" if email in ADMIN_EMAILS else "seeker"
            name = user_data.get("name")
            
            st.session_state.update({'logged_in': True, 'user_name': name, 'user_email': email, 'user_role': role})
            st.query_params.clear()
            
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            execute_query("INSERT INTO users (email, name, role, last_active, total_logins) VALUES (%s, %s, %s, %s, 1) ON CONFLICT (email) DO UPDATE SET last_active = EXCLUDED.last_active, name = EXCLUDED.name, total_logins = users.total_logins + 1", (email, name, role, now_str))
            st.rerun()
        else: 
            st.error("Access Denied. Invalid authorization protocols.")

if is_maint == 1 and st.session_state['user_role'] != "admin":
    if st.session_state['logged_in']:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="login-wrapper">
                <div class="login-card maintenance-card">
                    <h2 style="color: #ff4757; font-weight: 900; margin-bottom: 20px;">[ INTRUDER DETECTED ]</h2>
                    <img src="https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif" style="width: 100%; border-radius: 10px; border: 2px solid #ff4757; margin-bottom: 20px;">
                    <h3 style="color: #00ffcc; font-family: 'Share Tech Mono', monospace; font-style: italic;">"Good try brother let me fix website for you"</h3>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("RETREAT (Disconnect)", use_container_width=True):
                st.session_state.update({'logged_in': False, 'user_role': None, 'user_name': "", 'user_email': ""})
                st.rerun()
        st.stop()
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div class="login-wrapper">
                <div class="login-card maintenance-card">
                    <p class="system-status system-status-offline">[ SYSTEM CRITICAL: OFFLINE FOR UPGRADES ]</p>
                    <div class="app-title-large app-title-maintenance">NEURAL</div>
                    <div class="app-title-large app-title-maintenance" style="font-size: 2.5rem; margin-bottom: 20px;">// LOCKED</div>
                    <p style="color: #8892b0; font-size: 1.1rem; line-height: 1.5; margin-bottom: 10px;">{maint_msg}</p>
                    <p style="color: #ff4757; font-family: 'Share Tech Mono', monospace; font-size: 1.2rem; margin-bottom: 30px;">
                        EXPECTED UPLINK RESTORED: <br> {res_time}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("STAFF LOGIN", auth_url, type="secondary", use_container_width=True)
        st.stop() 

if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"""
        <div class="login-wrapper" style="margin-top: 2vh; margin-bottom: 3vh; animation: none;">
            <div style="text-align: center;">
                <p class="system-status" style="margin-bottom:5px;">[ PUBLIC ACCESS: LIMITED ]</p>
                <div class="app-title-large" style="font-size: 3rem;">NEURAL</div>
                <div class="app-title-large" style="font-size: 2rem; margin-bottom: 15px;">// TALENT GRID</div>
                <p style="color: #8892b0; font-size: 1.1rem; line-height: 1.5; margin-bottom: 20px;">
                    The premier decentralized hub for Artificial Intelligence, Large Language Models, and Data Science operatives.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("🔐 LOGIN TO UNLOCK", auth_url, type="primary", use_container_width=True)
        
    st.divider()
    st.markdown("<h4 style='text-align: center; color: #8892b0; margin-bottom: 30px;'>[ RECENT ACTIVE NODES ]</h4>", unsafe_allow_html=True)
    
    # SQL optimization: Fetch past 30 days and limit to 10 entries directly from the DB
    thirty_days_str = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    df_public = execute_query("SELECT * FROM jobs WHERE date_added >= %s ORDER BY date_added DESC LIMIT 10", (thirty_days_str,), fetch=True)
    if not df_public.empty:
        for _, row in df_public.iterrows(): display_job_card(row, is_admin=False, is_teaser=True)
    else: st.info("Grid is currently initiating. Check back later for new uplinks.")

# ==========================================
# 6. DASHBOARDS (Logged In)
# ==========================================
else:
    if (datetime.now() - st.session_state['last_heartbeat']).total_seconds() > 60:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execute_query("UPDATE users SET last_active = %s WHERE email = %s", (now_str, st.session_state['user_email']))
        st.session_state['last_heartbeat'] = datetime.now()

    if is_warn == 1: st.markdown(f"<div class='cyber-warning-banner'>⚠️ SYSTEM NOTICE: {warn_msg}</div>", unsafe_allow_html=True)

    col_logo, col_logout = st.columns([8, 1])
    with col_logo: 
        st.markdown('<p class="app-title-small">NEURAL // JOBS</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: #00ffcc; font-family: \'Share Tech Mono\', monospace; margin-top: -5px;">> Uplink established. Operator: {st.session_state["user_name"]}</p>', unsafe_allow_html=True)
    with col_logout:
        st.write("") 
        if st.button("DISCONNECT", use_container_width=True):
            st.session_state.update({'logged_in': False, 'user_role': None, 'user_name': "", "user_email": ""})
            st.rerun()

    # --- ADMIN VIEW ---
    if st.session_state['user_role'] == "admin":
        st.markdown("### [ GRID METRICS ]")
        
        # SQL Optimization: Use database aggregate queries instead of pulling the entire table
        thirty_days_str = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        df_counts = execute_query(
            "SELECT COUNT(*) as total, SUM(CASE WHEN date_added >= %s THEN 1 ELSE 0 END) as active FROM jobs", 
            (thirty_days_str,), 
            fetch=True
        )
        total_nodes = int(df_counts.iloc[0]['total']) if not df_counts.empty else 0
        active_nodes = int(df_counts.iloc[0]['active']) if not df_counts.empty and pd.notna(df_counts.iloc[0]['active']) else 0
        expired_nodes = total_nodes - active_nodes
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("TOTAL DATANODES", total_nodes)
        m2.metric("ACTIVE NODES (30D)", active_nodes)
        m3.metric("EXPIRED NODES", expired_nodes)
        m4.metric("SYSTEM STATUS", "MAINTENANCE" if is_maint == 1 else "WARNING ACTIVE" if is_warn == 1 else "ONLINE")
            
        st.write("---")

        if GEMINI_API_KEY: tab1, tab_ai, tab2, tab_cand, tab_analytics, tab3 = st.tabs(["[ ➕ INJECT ]", "[ 🧠 AI IMPORT ]", "[ 📋 NODES ]", "[ 📄 CANDIDATES ]", "[ 📈 ANALYTICS ]", "[ ⚙️ SYS ]"])
        else:
            tab1, tab2, tab_cand, tab_analytics, tab3 = st.tabs(["[ ➕ INJECT ]", "[ 📋 NODES ]", "[ 📄 CANDIDATES ]", "[ 📈 ANALYTICS ]", "[ ⚙️ SYS ]"])
            tab_ai = None
            
        with tab_analytics:
            st.markdown("#### Real-Time User Telemetry")
            df_users = execute_query("SELECT email, name, role, total_logins, last_active FROM users ORDER BY last_active DESC", fetch=True)
            if not df_users.empty:
                df_users['last_active'] = pd.to_datetime(df_users['last_active'], errors='coerce')
                five_mins_ago = pd.to_datetime('today') - timedelta(minutes=5)
                
                col_a1, col_a2, col_a3 = st.columns(3)
                col_a1.metric("👥 TOTAL USERS", len(df_users))
                col_a2.metric("🟢 CURRENTLY ONLINE", len(df_users[df_users['last_active'] >= five_mins_ago]))
                col_a3.metric("🔄 TOTAL NETWORK LOGINS", df_users['total_logins'].sum())
                
                st.write("---")
                df_display = df_users.copy()
                df_display['Status'] = df_display['last_active'].apply(lambda x: "🟢 Online" if x >= five_mins_ago else "🔴 Offline")
                df_display['Last Seen'] = df_display['last_active'].dt.strftime('%Y-%m-%d %H:%M:%S')
                st.dataframe(df_display[['Status', 'name', 'email', 'total_logins', 'Last Seen']], use_container_width=True, hide_index=True)
            else: st.info("No user telemetry data found.")

        with tab3:
            st.markdown("#### Stage 1: Global Broadcast (Warning)")
            if is_warn == 0:
                with st.form("warn_form"):
                    w_msg = st.text_input("Warning Message", value="System maintenance will begin in 15 minutes.")
                    if st.form_submit_button("📢 BROADCAST WARNING"):
                        execute_query("UPDATE sys_settings SET is_warning=1, warning_msg=%s WHERE id=1", (w_msg,))
                        st.rerun()
            else:
                if st.button("🔇 CLEAR WARNING"):
                    execute_query("UPDATE sys_settings SET is_warning=0, warning_msg='' WHERE id=1")
                    st.rerun()

            st.write("---")
            st.markdown("#### Stage 2: System Lockdown (Maintenance)")
            if is_maint == 0:
                with st.form("maint_form"):
                    downtime_hours = st.number_input("Hours of Downtime", min_value=1, max_value=48, value=2)
                    m_msg = st.text_input("Lockdown Message", value="Upgrading core neural network. Stand by.")
                    if st.form_submit_button("🚨 INITIATE LOCKDOWN", type="primary"):
                        resume_calc = (datetime.now() + timedelta(hours=downtime_hours)).strftime("%Y-%m-%d %H:%M:%S")
                        execute_query("UPDATE sys_settings SET is_maintenance=1, resume_time=%s, message=%s WHERE id=1", (resume_calc, m_msg))
                        st.rerun()
            else:
                if st.button("✅ DEACTIVATE LOCKDOWN"):
                    execute_query("UPDATE sys_settings SET is_maintenance=0 WHERE id=1")
                    st.rerun()

        with tab1:
            with st.container(border=True):
                st.markdown("#### INJECT MANUAL NODE")
                for k in ['m_title', 'm_company', 'm_location', 'm_sal_amount', 'manual_url', 'manual_desc']:
                    if k not in st.session_state: st.session_state[k] = ""
                
                def sync_url():
                    u = st.session_state['manual_url']
                    if u and "Apply :-" not in st.session_state['manual_desc']: st.session_state['manual_desc'] = f"Apply :- {u}\n\n" + st.session_state['manual_desc']
                def clear_manual():
                    for k in ['m_title', 'm_company', 'm_location', 'm_sal_amount', 'manual_url', 'manual_desc']: st.session_state[k] = ""
                def inject_man():
                    if st.session_state.m_title and st.session_state.m_company and st.session_state.manual_url:
                        loc = st.session_state.get('m_location', 'Remote') if st.session_state.get('m_is_remote') == 'No' else 'Remote'
                        execute_query("INSERT INTO jobs (id, title, company, location, url, source, description, salary_amount, salary_type, date_added) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                  ("MAN_"+str(uuid.uuid4())[:8], st.session_state.m_title, st.session_state.m_company, loc, st.session_state.manual_url, "Manual", st.session_state.manual_desc or "No desc", st.session_state.m_sal_amount or "N/A", st.session_state.get('m_sal_type', 'Unspecified'), datetime.now().strftime("%Y-%m-%d")))
                        clear_manual()
                        st.session_state['inject_msg'] = "success"
                    else: st.session_state['inject_msg'] = "error"

                if st.session_state.get('inject_msg') == "success":
                    st.success("Injection Successful! Form reset.")
                    st.session_state['inject_msg'] = None
                elif st.session_state.get('inject_msg') == "error":
                    st.error("SYSTEM ERROR: Title, Company, and URL are required.")
                    st.session_state['inject_msg'] = None
                
                st.text_input("Job Title", key="m_title")
                st.text_input("Entity / Company", key="m_company")
                m_is_remote = st.radio("Is this a Remote position?", ["Yes", "No"], horizontal=True, key="m_is_remote")
                if m_is_remote == "No": st.text_input("Specify Location", key="m_location")
                
                c1, c2 = st.columns(2)
                with c1: st.text_input("Compensation (in USD $)", key="m_sal_amount")
                with c2: st.selectbox("Cycle", ["Yearly", "Monthly", "Hourly", "Unspecified"], key="m_sal_type")
                
                st.text_input("Uplink URL", key="manual_url", on_change=sync_url)
                st.text_area("File Contents", key="manual_desc", height=150)
                
                cb1, cb2 = st.columns([4, 1])
                with cb1: st.button("🚀 INJECT NODE", type="primary", use_container_width=True, on_click=inject_man)
                with cb2: st.button("🧹 CLEAR ALL", use_container_width=True, on_click=clear_manual)

        # 🧠 NEW: AUTO-URL IMPORTER (Bypasses bot blocks via Jina AI)
        if tab_ai:
            with tab_ai:
                st.markdown("#### 🧠 Auto-URL Importer (Gemini AI)")
                if st.session_state['draft_job'] is None:
                    st.write("Paste the job URL below. The system will automatically bypass bot-protections, read the page, and decipher the job details.")
                    ai_target_url = st.text_input("Target Apply URL", placeholder="https://work.mercor.com/explore?...")
                    raw_messy_text = st.text_area("Fallback: Paste raw text here ONLY if the URL fetch fails", height=100)
                    
                    if st.button("🧠 FETCH & DECIPHER", type="primary", use_container_width=True):
                        if ai_target_url or raw_messy_text:
                            with st.spinner("Initiating sequence..."):
                                text_to_analyze = raw_messy_text
                                
                                # Fetch from URL if text box is empty
                                if not text_to_analyze and ai_target_url:
                                    st.toast("🌐 Fetching URL via Jina AI Reader...")
                                    try:
                                        res = requests.get(f"https://r.jina.ai/{ai_target_url}")
                                        if res.status_code == 200:
                                            text_to_analyze = res.text
                                        else:
                                            st.error(f"Firewall Blocked URL (Error {res.status_code}). Please copy-paste the text manually.")
                                    except Exception as e:
                                        st.error(f"Fetch failed: {e}")
                                
                                if text_to_analyze:
                                    st.toast("🧠 Gemini 1.5 Flash processing data...")
                                    try:
                                        model = genai.GenerativeModel("gemini-1.5-flash")
                                        prompt = f"""
                                        Analyze this webpage text:
                                        {text_to_analyze[:4000]}
                                        Extract and format exactly into JSON. Return ONLY raw JSON text:
                                        {{ "title": "Job Title", "company": "Company", "location": "City or 'Remote'", "description": "4-sentence professional summary.", "salary_amount": "Amount or 'N/A'", "salary_type": "Yearly/Monthly/Hourly/Unspecified" }}
                                        """
                                        response = model.generate_content(prompt)
                                        ai_output = response.text.strip().replace('```json', '').replace('```', '')
                                        parsed = json.loads(ai_output.strip())
                                        parsed['url'] = ai_target_url
                                        st.session_state['draft_job'] = parsed
                                        st.rerun()
                                    except Exception as e: st.error(f"Decipher failed: {e}")
                        else: st.warning("Paste a URL or raw text.")
                else:
                    st.warning("⚠️ DRAFT DECIPHERED. Edit and confirm below.")
                    with st.container(border=True):
                        c1, c2 = st.columns(2)
                        with c1: dt = st.text_input("Title", value=st.session_state['draft_job'].get('title', ''))
                        with c2: dc = st.text_input("Company", value=st.session_state['draft_job'].get('company', ''))
                        c3, c4, c5 = st.columns([2, 2, 1])
                        with c3: dl = st.text_input("Location", value=st.session_state['draft_job'].get('location', ''))
                        with c4: dsa = st.text_input("Compensation", value=st.session_state['draft_job'].get('salary_amount', ''))
                        with c5:
                            opts = ["Yearly", "Monthly", "Hourly", "Unspecified"]
                            def_opt = st.session_state['draft_job'].get('salary_type', 'Unspecified')
                            dst = st.selectbox("Cycle", opts, index=opts.index(def_opt) if def_opt in opts else 3)
                        du = st.text_input("URL", value=st.session_state['draft_job'].get('url', ''))
                        dd = st.text_area("Description", value=st.session_state['draft_job'].get('description', ''), height=150)
                        
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("🚀 CONFIRM & INJECT", type="primary", use_container_width=True):
                                execute_query("INSERT INTO jobs (id, title, company, location, url, source, description, salary_amount, salary_type, date_added) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                              ("AI_"+str(uuid.uuid4())[:8], dt, dc, dl, du, "Gemini AI", dd, dsa, dst, datetime.now().strftime("%Y-%m-%d")))
                                st.session_state['draft_job'] = None
                                st.success("Injected!"); st.rerun()
                        with b2:
                            if st.button("❌ CANCEL", use_container_width=True):
                                st.session_state['draft_job'] = None; st.rerun()

        with tab_cand:
            st.markdown("#### Registered Candidate Mainframe")
            df_cands = execute_query("SELECT user_email, skills_text, date_uploaded, resume_data FROM user_resumes ORDER BY date_uploaded DESC", fetch=True)
            if not df_cands.empty:
                active_resumes = df_cands.dropna(subset=['resume_data'])
                if not active_resumes.empty:
                    st.markdown("### 📦 Bulk Datapack Extraction")
                    zip_data = generate_zip_datapack(active_resumes)
                    def trig_purge(): st.session_state['show_bulk_purge'] = True
                    st.download_button(label=f"💾 DOWNLOAD ALL ({len(active_resumes)} .ZIP)", data=zip_data, file_name=f"resumes_{datetime.now().strftime('%Y-%m-%d')}.zip", mime="application/zip", use_container_width=True, on_click=trig_purge)
                    
                    if st.session_state['show_bulk_purge']:
                        st.warning("⚠️ DECRYPTION COMPLETE. Purge raw PDFs to reclaim space?")
                        cy, cn = st.columns(2)
                        with cy:
                            if st.button("🚨 YES, PURGE", type="primary", use_container_width=True):
                                execute_query("UPDATE user_resumes SET resume_data = NULL WHERE resume_data IS NOT NULL")
                                st.session_state['show_bulk_purge'] = False; st.rerun()
                        with cn:
                            if st.button("❌ NO, KEEP", use_container_width=True):
                                st.session_state['show_bulk_purge'] = False; st.rerun()
                
                st.write("---")
                st.markdown("### 👤 Candidate Profiles")
                for _, cand in df_cands.iterrows():
                    with st.container(border=True):
                        cinfo, cdl = st.columns([4, 1])
                        with cinfo:
                            st.subheader(cand['user_email'])
                            st.markdown(f"**Tech Stack:** {cand['skills_text']}")
                            st.caption(f"Date: {cand['date_uploaded']}")
                        with cdl:
                            if cand['resume_data'] is not None:
                                def purgesngl(e=cand['user_email']): execute_query("UPDATE user_resumes SET resume_data=NULL WHERE user_email=%s", (e,))
                                st.download_button(label="💾 PDF", data=bytes(cand['resume_data']), file_name=f"resume.pdf", mime="application/pdf", use_container_width=True, on_click=purgesngl)
                            else: st.button("🧹 PURGED", disabled=True, use_container_width=True, key=f"p_{cand['user_email']}")
            else: st.info("No candidates yet.")

        with tab2:
            # Query-Optimized Admin List: Show latest 100 job nodes
            df_admin_jobs = execute_query("SELECT * FROM jobs ORDER BY date_added DESC LIMIT 100", fetch=True)
            if df_admin_jobs.empty: st.info("Grid empty.")
            else:
                for _, row in df_admin_jobs.iterrows(): display_job_card(row, is_admin=True)

    # --- SEEKER VIEW ---
    elif st.session_state['user_role'] == "seeker":
        ue = st.session_state['user_email']
        
        # SQL Optimization: Filter outdated nodes directly inside SQL instead of Pandas
        thirty_days_str = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        df_seeker = execute_query("SELECT * FROM jobs WHERE date_added >= %s", (thirty_days_str,), fetch=True)

        df_saved = execute_query("SELECT job_id FROM saved_jobs WHERE user_email=%s", (ue,), fetch=True)
        saved_ids = df_saved['job_id'].tolist() if not df_saved.empty else []

        tab_browse, tab_saved, tab_match = st.tabs(["[ GRID SEARCH ]", "[ ⭐ SAVED NODES ]", "[ AI OVERRIDE ]"])
        with tab_browse:
            cs, ct = st.columns([3, 1])
            with cs: search = st.text_input("QUERY DATABASE...", placeholder="Python, OpenAI...")
            with ct: t_filter = st.selectbox("TIME RANGE", ["All Active", "Past 24 Hours", "Past 7 Days"])
            st.write("---")
            
            # FIXED: Variable updated from time_filter -> t_filter to correct Seeker tab crash
            if t_filter == "Past 24 Hours": 
                t_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                df_seeker = df_seeker[df_seeker['date_added'] >= t_str]
            elif t_filter == "Past 7 Days": 
                t_str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                df_seeker = df_seeker[df_seeker['date_added'] >= t_str]
                
            if search: df_seeker = df_seeker[df_seeker['title'].str.contains(search, case=False) | df_seeker['company'].str.contains(search, case=False)]
            
            if df_seeker.empty: st.info("No nodes match.")
            else:
                for _, row in df_seeker.sort_values(by='date_added', ascending=False).iterrows(): display_job_card(row, user_email=ue, is_saved=(row['id'] in saved_ids))
        
        with tab_saved:
            ds = df_seeker[df_seeker['id'].isin(saved_ids)]
            if ds.empty: st.info("No saved datanodes.")
            else:
                for _, row in ds.iterrows(): display_job_card(row, user_email=ue, is_saved=True)

        with tab_match:
            with st.container(border=True):
                upl = st.file_uploader("UPLOAD DATAPACK (PDF)", type="pdf")
            if upl:
                with st.spinner("Running neural analysis..."):
                    rt = extract_text_from_pdf(upl)
                    if GEMINI_API_KEY:
                        try:
                            model = genai.GenerativeModel("gemini-1.5-flash")
                            jc = "".join([f"ID:{r['id']} | Title:{r['title']} | Desc:{str(r['description'])[:150]}\n" for _, r in df_seeker.iterrows()])
                            prompt = f"Resume:\n{rt[:2500]}\nJobs:\n{jc}\nFind top 3 best matching Job IDs. Return ONLY comma-separated IDs."
                            resp = model.generate_content(prompt)
                            m_ids = [i.strip() for i in resp.text.replace('`','').split(',')]
                            matched = df_seeker[df_seeker['id'].isin(m_ids)]
                            
                            sk_prompt = f"Resume:\n{rt[:2000]}\nReturn a clean, comma-separated list of the top 5 technical skills found. Return ONLY the skills."
                            sk_str = model.generate_content(sk_prompt).text.replace('`','').strip()
                            
                            execute_query("INSERT INTO user_resumes (user_email, resume_data, skills_text, date_uploaded) VALUES (%s, %s, %s, %s) ON CONFLICT (user_email) DO UPDATE SET resume_data = EXCLUDED.resume_data, skills_text = EXCLUDED.skills_text, date_uploaded = EXCLUDED.date_uploaded",
                                          (ue, psycopg2.Binary(upl.getvalue()), sk_str, datetime.now().strftime("%Y-%m-%d")))
                            st.toast("⚡ Resume secure-uplinked to Databank!")
                            
                            if not matched.empty:
                                st.success("🟢 AI Analysis Complete.")
                                for _, row in matched.iterrows(): display_job_card(row, user_email=ue, is_saved=(row['id'] in saved_ids))
                            else: st.info("No perfect matches found.")
                        except Exception as e: st.error(f"AI Error: {e}")
                    else:
                        st.warning("⚠️ Gemini API Key not found. Falling back to Keyword Heuristics.")
                        skills = [s for s in ['python', 'sql', 'react', 'java', 'ai', 'data', 'llm', 'machine learning', 'pytorch', 'prompt engineering'] if s in rt]
                        if skills:
                            matched = df_seeker[df_seeker['title'].str.lower().str.contains('|'.join(skills))]
                            if not matched.empty:
                                for _, row in matched.head(10).iterrows(): display_job_card(row, user_email=ue, is_saved=(row['id'] in saved_ids))
                            else: st.info("No matching nodes.")
                        else: st.warning("Analysis failed.")
