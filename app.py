import streamlit as st
import requests
import psycopg2
import os
import pandas as pd
import PyPDF2
import uuid
import json
import zipfile
import io
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
DB_URL = st.secrets["SUPABASE_URL"]
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
    .login-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 10vh; animation: float 6s ease-in-out infinite; }
    @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }
    .login-card { background: linear-gradient(145deg, rgba(15, 23, 42, 0.7) 0%, rgba(20, 20, 30, 0.5) 100%); border: 1px solid rgba(0, 242, 254, 0.3); border-radius: 20px; padding: 50px 40px; box-shadow: 0 0 40px rgba(0, 242, 254, 0.1); text-align: center; backdrop-filter: blur(16px); width: 100%; max-width: 500px; transition: all 0.5s ease;}
    .maintenance-card { border: 1px solid rgba(255, 71, 87, 0.5) !important; box-shadow: 0 0 50px rgba(255, 71, 87, 0.2) !important; }
    .app-title-large { font-size: 4rem; font-weight: 900; background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #b06ab3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0px 0px 25px rgba(0, 242, 254, 0.5); letter-spacing: -2px; margin-bottom: 5px; line-height: 1.1; }
    .app-title-maintenance { color: #ff4757 !important; background: none !important; -webkit-text-fill-color: #ff4757 !important; text-shadow: 0px 0px 25px rgba(255, 71, 87, 0.8) !important;}
    .system-status { font-family: 'Share Tech Mono', monospace; color: #00ffcc; font-size: 0.9rem; margin-bottom: 25px; animation: blink 2s linear infinite; }
    .system-status-offline { color: #ff4757 !important; text-shadow: 0 0 10px #ff4757 !important; }
    @keyframes blink { 0%, 100% { opacity: 1; text-shadow: 0 0 10px #00ffcc; } 50% { opacity: 0.4; text-shadow: none; } }
    .cyber-btn { display: inline-block; margin-top: 20px; padding: 15px 40px; background: rgba(0, 242, 254, 0.1); color: #00f2fe !important; font-family: 'Share Tech Mono', monospace; font-size: 1.2rem; font-weight: bold; text-decoration: none; border: 1px solid #00f2fe; border-radius: 4px; text-transform: uppercase; letter-spacing: 2px; transition: all 0.3s ease; box-shadow: inset 0 0 10px rgba(0, 242, 254, 0.1), 0 0 15px rgba(0, 242, 254, 0.2); }
    .cyber-btn:hover { background: #00f2fe; color: #050810 !important; box-shadow: 0 0 30px rgba(0, 242, 254, 0.8); transform: scale(1.05); }
    .admin-bypass-btn { margin-top: 15px; font-size: 0.8rem !important; border: 1px solid #ff4757 !important; color: #ff4757 !important; background: transparent !important; box-shadow: none !important;}
    .admin-bypass-btn:hover { background: #ff4757 !important; color: white !important; box-shadow: 0 0 20px #ff4757 !important; }
    .app-title-small { font-size: 2.5rem; font-weight: 900; background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #b06ab3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0px 0px 15px rgba(0, 242, 254, 0.3); margin-bottom: 0px; text-transform: uppercase; }
    .cyber-warning-banner { background: rgba(255, 165, 2, 0.1); border: 1px solid #ffa502; color: #ffa502; padding: 12px; border-radius: 5px; text-align: center; font-family: 'Share Tech Mono', monospace; font-weight: bold; margin-bottom: 20px; box-shadow: 0 0 10px rgba(255, 165, 2, 0.2); animation: pulse-warn 2s infinite; letter-spacing: 1px;}
    @keyframes pulse-warn { 0% { box-shadow: 0 0 10px rgba(255, 165, 2, 0.2); } 50% { box-shadow: 0 0 20px rgba(255, 165, 2, 0.5); } 100% { box-shadow: 0 0 10px rgba(255, 165, 2, 0.2); } }
    [data-testid="stVerticalBlockBorderWrapper"] { border-radius: 12px !important; border: 1px solid rgba(0, 242, 254, 0.15) !important; background: rgba(15, 23, 42, 0.4) !important; backdrop-filter: blur(10px) !important; transition: all 0.2s ease-in-out; }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { border: 1px solid rgba(0, 242, 254, 0.5) !important; box-shadow: 0 0 20px rgba(0, 242, 254, 0.15); }
    .tech-tag { background: rgba(0, 242, 254, 0.1); color: #00f2fe; padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: 700; border: 1px solid rgba(0, 242, 254, 0.3); margin-right: 8px; font-family: 'Share Tech Mono', monospace;}
    .company-avatar { width: 60px; height: 60px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 2px solid #b06ab3; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; font-weight: bold; color: #b06ab3; box-shadow: 0 0 15px rgba(176, 106, 179, 0.4); margin: auto; }
    .stTabs [data-baseweb="tab-list"] { gap: 30px; }
    .stTabs [data-baseweb="tab"] { font-size: 1.1rem; font-weight: 700; color: #8892b0; }
    .stTabs [aria-selected="true"] { color: #00f2fe !important; border-bottom: 2px solid #00f2fe !important; text-shadow: 0 0 10px rgba(0, 242, 254, 0.5); }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

apply_futuristic_css()

# ==========================================
# 3. DATABASE SETUP 
# ==========================================
def init_db():
    conn = psycopg2.connect(DB_URL)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, title TEXT, company TEXT, location TEXT, url TEXT, source TEXT, description TEXT, salary_amount TEXT, salary_type TEXT, date_added TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sys_settings (id INTEGER PRIMARY KEY, is_maintenance INTEGER, resume_time TEXT, message TEXT, is_warning INTEGER DEFAULT 0, warning_msg TEXT DEFAULT '')''')
    c.execute('''CREATE TABLE IF NOT EXISTS saved_jobs (user_email TEXT, job_id TEXT, PRIMARY KEY (user_email, job_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_resumes (user_email TEXT PRIMARY KEY, resume_data BYTEA, skills_text TEXT, date_uploaded TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, name TEXT, role TEXT, last_active TEXT, total_logins INTEGER DEFAULT 0)''')
    c.execute("INSERT INTO sys_settings (id, is_maintenance, resume_time, message, is_warning, warning_msg) VALUES (1, 0, '', '', 0, '') ON CONFLICT (id) DO NOTHING")
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================
def get_sys_status():
    conn = psycopg2.connect(DB_URL)
    c = conn.cursor()
    c.execute("SELECT is_maintenance, resume_time, message, is_warning, warning_msg FROM sys_settings WHERE id=1")
    row = c.fetchone()
    conn.close()
    is_maint, res_time, msg, is_warn, warn_msg = row[0], row[1], row[2], row[3], row[4]
    
    if is_maint == 1 and res_time:
        if datetime.now() > datetime.strptime(res_time, "%Y-%m-%d %H:%M:%S"):
            conn = psycopg2.connect(DB_URL)
            c = conn.cursor()
            c.execute("UPDATE sys_settings SET is_maintenance=0, is_warning=0 WHERE id=1")
            conn.commit()
            conn.close()
            return (0, "", "", 0, "")
    return (is_maint, res_time, msg, is_warn, warn_msg)

def purge_resume_data(email):
    try:
        conn = psycopg2.connect(DB_URL)
        c = conn.cursor()
        c.execute("UPDATE user_resumes SET resume_data = NULL WHERE user_email = %s", (email,))
        conn.commit()
        conn.close()
        st.toast(f"🧹 Database purged for {email}. Space saved!")
    except Exception as e: st.error(f"Purge failed: {e}")

def generate_zip_datapack(active_resumes):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for email, data in active_resumes:
            zip_file.writestr(f"{email.split('@')[0]}_resume.pdf", bytes(data))
    return zip_buffer.getvalue()

def extract_text_from_pdf(uploaded_file):
    try: return "".join([page.extract_text() + " " for page in PyPDF2.PdfReader(uploaded_file).pages]).lower()
    except: return ""

def display_job_card(row, is_admin=False, user_email=None, is_saved=False):
    is_expired = False
    if is_admin and pd.to_datetime(row['date_added']) < (pd.to_datetime('today') - timedelta(days=30)): is_expired = True

    with st.container(border=True):
        col_icon, col_details, col_action = st.columns([1, 7, 2])
        with col_icon:
            st.markdown(f"<div class='company-avatar'>{row['company'][0].upper() if row['company'] else 'X'}</div>", unsafe_allow_html=True)
        with col_details:
            title_html = f"<h3 style='margin-bottom:0px; color:#ffffff;'>{row['title']}</h3>"
            if is_expired: title_html = f"<h3 style='margin-bottom:0px; color:#ff4757;'>[EXPIRED] {row['title']}</h3>"
            st.markdown(title_html, unsafe_allow_html=True)
            st.markdown(f"<p style='color:#8892b0; font-size: 1.1rem; margin-top: 5px;'>{row['company']}</p>", unsafe_allow_html=True)
            
            sal_val = str(row['salary_amount']).strip()
            if sal_val and sal_val.lower() not in ["n/a", ""]:
                if not sal_val.startswith("$"): sal_val = "$" + sal_val
                sal = f"{sal_val} / {row['salary_type']}"
            else: sal = "Unlisted"
            
            date_str = str(row['date_added'])[:10]
            st.markdown(f"<span class='tech-tag'>LOC: {row['location']}</span> <span class='tech-tag'>PAY: {sal}</span> <span class='tech-tag'>DATE: {date_str}</span>", unsafe_allow_html=True)
        with col_action:
            st.write("")
            st.link_button("INITIATE UPLINK", row['url'], use_container_width=True, type="primary")
            
            if not is_admin and user_email:
                if is_saved:
                    if st.button("❌ REMOVE", key=f"unsave_{row['id']}", use_container_width=True):
                        conn = psycopg2.connect(DB_URL)
                        c = conn.cursor()
                        c.execute("DELETE FROM saved_jobs WHERE user_email=%s AND job_id=%s", (user_email, row['id']))
                        conn.commit()
                        conn.close()
                        st.rerun()
                else:
                    if st.button("⭐ SAVE NODE", key=f"save_{row['id']}", use_container_width=True):
                        conn = psycopg2.connect(DB_URL)
                        c = conn.cursor()
                        c.execute("INSERT INTO saved_jobs (user_email, job_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (user_email, row['id']))
                        conn.commit()
                        conn.close()
                        st.rerun()

        with st.expander("DECRYPT DATAFILE (View Description)"):
            st.write(row['description'])

# ==========================================
# 5. LOGIN SYSTEM & MAINTENANCE CHECK
# ==========================================
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_role' not in st.session_state: st.session_state['user_role'] = None
if 'user_name' not in st.session_state: st.session_state['user_name'] = ""
if 'user_email' not in st.session_state: st.session_state['user_email'] = "" 
if 'show_bulk_purge' not in st.session_state: st.session_state['show_bulk_purge'] = False
if 'draft_job' not in st.session_state: st.session_state['draft_job'] = None
if 'last_heartbeat' not in st.session_state: st.session_state['last_heartbeat'] = datetime.min

if not st.session_state['logged_in'] and 'code' in st.query_params:
    with st.spinner("Decrypting neural pathways..."):
        code = st.query_params['code']
        res = requests.post("https://oauth2.googleapis.com/token", data={"code": code, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "redirect_uri": REDIRECT_URI, "grant_type": "authorization_code"})
        if res.status_code == 200:
            user_data = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {res.json().get('access_token')}"}).json()
            email = user_data.get("email")
            role = "admin" if email in ADMIN_EMAILS else "seeker"
            name = user_data.get("name")
            
            st.session_state.update({'logged_in': True, 'user_name': name, 'user_email': email, 'user_role': role})
            st.query_params.clear()
            
            conn = psycopg2.connect(DB_URL)
            c = conn.cursor()
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("""
                INSERT INTO users (email, name, role, last_active, total_logins) 
                VALUES (%s, %s, %s, %s, 1) 
                ON CONFLICT (email) 
                DO UPDATE SET last_active = EXCLUDED.last_active, name = EXCLUDED.name, total_logins = users.total_logins + 1
            """, (email, name, role, now_str))
            conn.commit()
            conn.close()
            st.rerun()
        else: 
            st.error("Access Denied. Invalid authorization protocols.")

is_maint, res_time, maint_msg, is_warn, warn_msg = get_sys_status()

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
            st.write("")
            if st.button("RETREAT (Disconnect)", use_container_width=True):
                st.session_state.update({'logged_in': False, 'user_role': None, 'user_name': "", 'user_email': ""})
                st.rerun()
        st.stop()
    else:
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=openid%20email%20profile"
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
                    <a href="{auth_url}" class="cyber-btn admin-bypass-btn" target="_blank">STAFF LOGIN</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.stop() 

if not st.session_state['logged_in']:
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=openid%20email%20profile"
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="login-wrapper">
            <div class="login-card">
                <p class="system-status">[ SYSTEM STATUS: SECURE & ONLINE ]</p>
                <div class="app-title-large">NEURAL</div>
                <div class="app-title-large" style="font-size: 2.5rem; margin-bottom: 20px;">// TALENT GRID</div>
                <p style="color: #8892b0; font-size: 1.1rem; line-height: 1.5; margin-bottom: 30px;">The premier decentralized manual hub for Artificial Intelligence, Large Language Models, and Data Science operatives.</p>
                <a href="{auth_url}" class="cyber-btn" target="_blank">CONNECT DATASTREAM</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. MAIN APP DASHBOARDS
# ==========================================
else:
    if (datetime.now() - st.session_state['last_heartbeat']).total_seconds() > 60:
        conn = psycopg2.connect(DB_URL)
        c = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE users SET last_active = %s WHERE email = %s", (now_str, st.session_state['user_email']))
        conn.commit()
        conn.close()
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

    conn = psycopg2.connect(DB_URL)
    df = pd.read_sql_query("SELECT * FROM jobs", conn)
    conn.close()
    if 'date_added' in df.columns: df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce').fillna(pd.to_datetime('today'))
    else: df['date_added'] = pd.to_datetime('today')

    # --- ADMIN VIEW ---
    if st.session_state['user_role'] == "admin":
        st.markdown("### [ GRID METRICS ]")
        thirty_days_ago = pd.to_datetime('today') - timedelta(days=30)
        active_nodes = len(df[df['date_added'] >= thirty_days_ago]) if not df.empty else 0
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("TOTAL DATANODES", len(df))
        m2.metric("ACTIVE NODES (30D)", active_nodes)
        m3.metric("EXPIRED NODES", len(df) - active_nodes)
        
        if is_maint == 1: m4.metric("SYSTEM STATUS", "MAINTENANCE")
        elif is_warn == 1: m4.metric("SYSTEM STATUS", "WARNING ACTIVE")
        else: m4.metric("SYSTEM STATUS", "ONLINE")
            
        st.write("---")

        if GEMINI_API_KEY:
            tab1, tab_ai, tab2, tab_cand, tab_analytics, tab3 = st.tabs(["[ ➕ INJECT ]", "[ 🧠 AI IMPORT ]", "[ 📋 NODES ]", "[ 📄 CANDIDATES ]", "[ 📈 ANALYTICS ]", "[ ⚙️ SYS ]"])
        else:
            tab1, tab2, tab_cand, tab_analytics, tab3 = st.tabs(["[ ➕ INJECT ]", "[ 📋 NODES ]", "[ 📄 CANDIDATES ]", "[ 📈 ANALYTICS ]", "[ ⚙️ SYS ]"])
            tab_ai = None
            
        with tab_analytics:
            st.markdown("#### Real-Time User Telemetry")
            st.write("Monitor network traffic, user engagement, and active sessions.")
            conn = psycopg2.connect(DB_URL)
            df_users = pd.read_sql_query("SELECT email, name, role, total_logins, last_active FROM users ORDER BY last_active DESC", conn)
            conn.close()
            
            if not df_users.empty:
                df_users['last_active'] = pd.to_datetime(df_users['last_active'], errors='coerce')
                five_mins_ago = pd.to_datetime('today') - timedelta(minutes=5)
                online_count = len(df_users[df_users['last_active'] >= five_mins_ago])
                
                col_a1, col_a2, col_a3 = st.columns(3)
                col_a1.metric("👥 TOTAL USERS", len(df_users))
                col_a2.metric("🟢 CURRENTLY ONLINE", online_count)
                col_a3.metric("🔄 TOTAL NETWORK LOGINS", df_users['total_logins'].sum())
                
                st.write("---")
                st.markdown("##### User Directory")
                df_display = df_users.copy()
                df_display['Status'] = df_display['last_active'].apply(lambda x: "🟢 Online" if x >= five_mins_ago else "🔴 Offline")
                df_display['Last Seen'] = df_display['last_active'].dt.strftime('%Y-%m-%d %H:%M:%S')
                df_display = df_display[['Status', 'name', 'email', 'total_logins', 'Last Seen']]
                df_display.columns = ['Status', 'Name', 'Email', 'Total Logins', 'Last Seen']
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else: st.info("No user telemetry data found. Users need to log in to generate data.")

        with tab3:
            st.markdown("#### Stage 1: Global Broadcast (Warning)")
            if is_warn == 0:
                with st.form("warn_form"):
                    w_msg = st.text_input("Warning Message", value="System maintenance will begin in 15 minutes.")
                    if st.form_submit_button("📢 BROADCAST WARNING"):
                        conn = psycopg2.connect(DB_URL)
                        c = conn.cursor()
                        c.execute("UPDATE sys_settings SET is_warning=%s, warning_msg=%s WHERE id=1", (1, w_msg))
                        conn.commit()
                        conn.close()
                        st.rerun()
            else:
                if st.button("🔇 CLEAR WARNING"):
                    conn = psycopg2.connect(DB_URL)
                    c = conn.cursor()
                    c.execute("UPDATE sys_settings SET is_warning=0, warning_msg='' WHERE id=1")
                    conn.commit()
                    conn.close()
                    st.rerun()

            st.write("---")
            st.markdown("#### Stage 2: System Lockdown (Maintenance)")
            if is_maint == 0:
                with st.form("maint_form"):
                    downtime_hours = st.number_input("Hours of Downtime", min_value=1, max_value=48, value=2)
                    m_msg = st.text_input("Lockdown Message", value="Upgrading core neural network. Stand by.")
                    if st.form_submit_button("🚨 INITIATE LOCKDOWN", type="primary"):
                        resume_calc = (datetime.now() + timedelta(hours=downtime_hours)).strftime("%Y-%m-%d %H:%M:%S")
                        conn = psycopg2.connect(DB_URL)
                        c = conn.cursor()
                        c.execute("UPDATE sys_settings SET is_maintenance=%s, resume_time=%s, message=%s WHERE id=1", (1, resume_calc, m_msg))
                        conn.commit()
                        conn.close()
                        st.rerun()
            else:
                if st.button("✅ DEACTIVATE LOCKDOWN"):
                    conn = psycopg2.connect(DB_URL)
                    c = conn.cursor()
                    c.execute("UPDATE sys_settings SET is_maintenance=0 WHERE id=1")
                    conn.commit()
                    conn.close()
                    st.rerun()

        with tab1:
            with st.container(border=True):
                st.markdown("#### INJECT MANUAL NODE")
                
                # --- STATE MANAGEMENT LOGIC & CALLBACKS ---
                if 'manual_url' not in st.session_state: st.session_state['manual_url'] = ""
                if 'manual_desc' not in st.session_state: st.session_state['manual_desc'] = ""
                if 'm_title' not in st.session_state: st.session_state['m_title'] = ""
                if 'm_company' not in st.session_state: st.session_state['m_company'] = ""
                if 'm_location' not in st.session_state: st.session_state['m_location'] = ""
                if 'm_sal_amount' not in st.session_state: st.session_state['m_sal_amount'] = ""
                if 'inject_status' not in st.session_state: st.session_state['inject_status'] = None
                
                def sync_url_to_desc():
                    url = st.session_state['manual_url']
                    if url and "Apply :-" not in st.session_state['manual_desc']:
                        st.session_state['manual_desc'] = f"Apply :- {url}\n\n" + st.session_state['manual_desc']
                
                def clear_form_cb():
                    for k in ['m_title', 'm_company', 'm_location', 'm_sal_amount', 'manual_url', 'manual_desc']: 
                        st.session_state[k] = ""
                
                def inject_node_cb():
                    t = st.session_state['m_title']
                    c = st.session_state['m_company']
                    u = st.session_state['manual_url']
                    if t and c and u:
                        loc = st.session_state.get('m_location', 'Remote') if st.session_state.get('m_is_remote') == 'No' else 'Remote'
                        conn = psycopg2.connect(DB_URL)
                        cur = conn.cursor()
                        today_str = datetime.now().strftime("%Y-%m-%d")
                        cur.execute("INSERT INTO jobs (id, title, company, location, url, source, description, salary_amount, salary_type, date_added) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                  ("MAN_"+str(uuid.uuid4())[:8], t, c, loc, u, "Manual", st.session_state['manual_desc'] or "No desc", st.session_state['m_sal_amount'] or "N/A", st.session_state.get('m_sal_type', 'Unspecified'), today_str))
                        conn.commit()
                        conn.close()
                        clear_form_cb()
                        st.session_state['inject_status'] = "success"
                    else:
                        st.session_state['inject_status'] = "error"

                if st.session_state['inject_status'] == "success":
                    st.success("Injection Successful! Form reset for next entry.")
                    st.session_state['inject_status'] = None
                elif st.session_state['inject_status'] == "error":
                    st.error("SYSTEM ERROR: Title, Company, and URL are required.")
                    st.session_state['inject_status'] = None
                
                st.text_input("Job Title", key="m_title")
                st.text_input("Entity / Company", key="m_company")
                m_is_remote = st.radio("Is this a Remote position?", ["Yes", "No"], horizontal=True, key="m_is_remote")
                if m_is_remote == "No":
                    st.text_input("Specify Location (e.g. San Francisco, CA / On-site)", key="m_location")
                
                c1, c2 = st.columns(2)
                with c1: st.text_input("Compensation (in USD $)", key="m_sal_amount")
                with c2: st.selectbox("Cycle", ["Yearly", "Monthly", "Hourly", "Unspecified"], key="m_sal_type")
                
                st.text_input("Uplink URL", key="manual_url", on_change=sync_url_to_desc)
                st.text_area("File Contents", key="manual_desc", height=150)
                
                col_btn1, col_btn2 = st.columns([4, 1])
                with col_btn1:
                    st.button("🚀 INJECT NODE", type="primary", use_container_width=True, on_click=inject_node_cb)
                with col_btn2:
                    st.button("🧹 CLEAR ALL", use_container_width=True, on_click=clear_form_cb)

        if tab_ai:
            with tab_ai:
                st.markdown("#### 🧠 Free Gemini AI Importer: Copy-Paste Any Webpage")
                if st.session_state['draft_job'] is None:
                    raw_messy_text = st.text_area("Paste Messy Webpage Text Here", height=200, placeholder="Pasted raw text from Mercor...")
                    ai_target_url = st.text_input("Target Apply URL", placeholder="https://work.mercor.com/explore?...")
                    if st.button("🧠 DECIPHER RAW DATA", type="primary", use_container_width=True):
                        if raw_messy_text and ai_target_url:
                            with st.spinner("Gemini 1.5 Flash Deciphering data..."):
                                try:
                                    model = genai.GenerativeModel("gemini-1.5-flash")
                                    prompt = f"""
                                    Analyze this raw, messy webpage text copied from a career website:
                                    {raw_messy_text[:4000]}
                                    
                                    Extract and format the information exactly into a JSON structure. 
                                    Do NOT include markdown formatting like ```json or ```. Return ONLY raw JSON text.
                                    {{
                                        "title": "Clean, professional Job Title",
                                        "company": "Company Name",
                                        "location": "Specific city/state or 'Remote'",
                                        "description": "Write a highly professional, formatted 4-sentence summary of the role, benefits, and requirements.",
                                        "salary_amount": "Estimate or amount (e.g. 150,000) or 'N/A'",
                                        "salary_type": "Yearly, Monthly, Hourly, or Unspecified"
                                    }}
                                    """
                                    response = model.generate_content(prompt)
                                    ai_output = response.text.strip()
                                    if ai_output.startswith('```json'): ai_output = ai_output[7:]
                                    if ai_output.startswith('```'): ai_output = ai_output[3:]
                                    if ai_output.endswith('```'): ai_output = ai_output[:-3]
                                    
                                    parsed_json = json.loads(ai_output.strip())
                                    parsed_json['url'] = ai_target_url
                                    st.session_state['draft_job'] = parsed_json
                                    st.rerun()
                                except Exception as e: st.error(f"Gemini Decipher failed: {e}")
                        else: st.warning("Please paste the messy webpage text and add the apply URL.")
                else:
                    st.warning("⚠️ DRAFT DECIPHERED. Please review, edit, and confirm the job details below before publishing.")
                    with st.container(border=True):
                        col_dt1, col_dt2 = st.columns(2)
                        with col_dt1: d_title = st.text_input("Job Title", value=st.session_state['draft_job'].get('title', ''))
                        with col_dt2: d_company = st.text_input("Entity / Company", value=st.session_state['draft_job'].get('company', ''))
                        col_dt3, col_dt4, col_dt5 = st.columns([2, 2, 1])
                        with col_dt3: d_location = st.text_input("Location", value=st.session_state['draft_job'].get('location', ''))
                        with col_dt4: d_sal_amount = st.text_input("Compensation", value=st.session_state['draft_job'].get('salary_amount', ''))
                        with col_dt5:
                            cycle_options = ["Yearly", "Monthly", "Hourly", "Unspecified"]
                            default_cycle = st.session_state['draft_job'].get('salary_type', 'Unspecified')
                            cycle_idx = cycle_options.index(default_cycle) if default_cycle in cycle_options else 3
                            d_sal_type = st.selectbox("Cycle", cycle_options, index=cycle_idx)
                            
                        d_url = st.text_input("Uplink URL", value=st.session_state['draft_job'].get('url', ''))
                        d_desc = st.text_area("Full Job Description", value=st.session_state['draft_job'].get('description', ''), height=150)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("🚀 CONFIRM & INJECT NODE", type="primary", use_container_width=True):
                                conn = psycopg2.connect(DB_URL)
                                c = conn.cursor()
                                today_str = datetime.now().strftime("%Y-%m-%d")
                                job_id = "AI_" + str(uuid.uuid4())[:8]
                                c.execute("""
                                    INSERT INTO jobs (id, title, company, location, url, source, description, salary_amount, salary_type, date_added)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, (job_id, d_title, d_company, d_location, d_url, "Gemini AI", d_desc, d_sal_amount, d_sal_type, today_str))
                                conn.commit()
                                conn.close()
                                st.session_state['draft_job'] = None
                                st.balloons()
                                st.success("🚀 Node Injected and Live on grid!")
                                st.rerun()
                        with col_btn2:
                            if st.button("❌ CANCEL DRAFT", use_container_width=True):
                                st.session_state['draft_job'] = None
                                st.rerun()

        with tab_cand:
            st.markdown("#### Registered Candidate Mainframe")
            st.write("Browse candidates. Download raw resumes individually or compress them into a bulk ZIP package.")
            st.write("---")
            conn = psycopg2.connect(DB_URL)
            c = conn.cursor()
            c.execute("SELECT user_email, skills_text, date_uploaded, resume_data FROM user_resumes ORDER BY date_uploaded DESC")
            candidates = c.fetchall()
            conn.close()
            active_resumes = [cand for cand in candidates if cand[3] is not None and len(cand[3]) > 0]
            
            if active_resumes:
                st.markdown("### 📦 Bulk Datapack Extraction")
                zip_data = generate_zip_datapack(active_resumes)
                def trigger_bulk_purge_confirmation(): st.session_state['show_bulk_purge'] = True
                st.download_button(label=f"💾 DOWNLOAD ALL RESUMES ({len(active_resumes)} FILES .ZIP)", data=zip_data, file_name=f"neural_grid_resumes_{datetime.now().strftime('%Y-%m-%d')}.zip", mime="application/zip", use_container_width=True, on_click=trigger_bulk_purge_confirmation, key="bulk_zip_dl")
                
                if st.session_state['show_bulk_purge']:
                    st.write("")
                    st.warning("⚠️ DECRYPTION COMPLETE. Do you want to purge these raw PDF files from the cloud database now to reclaim storage space?")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("🚨 YES, PURGE CLOUD STORAGE", type="primary", use_container_width=True):
                            conn = psycopg2.connect(DB_URL)
                            c = conn.cursor()
                            c.execute("UPDATE user_resumes SET resume_data = NULL WHERE resume_data IS NOT NULL")
                            conn.commit()
                            conn.close()
                            st.session_state['show_bulk_purge'] = False
                            st.toast("🧹 Cloud storage successfully purged! Space reclaimed.")
                            st.rerun()
                    with col_no:
                        if st.button("❌ NO, KEEP CLOUD COPIES", use_container_width=True):
                            st.session_state['show_bulk_purge'] = False
                            st.rerun()
                st.write("---")
            
            st.markdown("### 👤 Candidate Profiles")
            if not candidates: st.info("No candidates have uploaded their resumes to the neural grid yet.")
            else:
                for cand in candidates:
                    email, skills_text, date_uploaded, resume_data = cand
                    with st.container(border=True):
                        col_info, col_dl = st.columns([4, 1])
                        with col_info:
                            st.subheader(email)
                            st.markdown(f"**Detected Tech Stack:** {skills_text}")
                            st.caption(f"Secure Uplink Date: {date_uploaded}")
                        with col_dl:
                            st.write("") 
                            if resume_data is not None and len(resume_data) > 0:
                                st.download_button(label="DOWNLOAD PDF 💾", data=bytes(resume_data), file_name=f"{email.split('@')[0]}_resume.pdf", mime="application/pdf", use_container_width=True, key=f"dl_{email}", on_click=purge_resume_data, args=(email,))
                            else: st.button("🧹 PURGED / SECURED", key=f"purged_{email}", disabled=True, use_container_width=True)

        with tab2:
            if df.empty: st.info("Grid empty. Inject new nodes.")
            else:
                df = df.sort_values(by='date_added', ascending=False)
                for _, row in df.iterrows(): display_job_card(row, is_admin=True)

    # --- SEEKER VIEW ---
    elif st.session_state['user_role'] == "seeker":
        user_email = st.session_state['user_email']
        thirty_days_ago = pd.to_datetime('today') - timedelta(days=30)
        df_seeker = df[df['date_added'] >= thirty_days_ago].copy()

        conn = psycopg2.connect(DB_URL)
        c = conn.cursor()
        c.execute("SELECT job_id FROM saved_jobs WHERE user_email=%s", (user_email,))
        saved_job_ids = [r[0] for r in c.fetchall()]
        conn.close()

        tab_browse, tab_saved, tab_match = st.tabs(["[ GRID SEARCH ]", "[ ⭐ SAVED NODES ]", "[ AI OVERRIDE ]"])
        with tab_browse:
            col_search, col_time = st.columns([3, 1])
            with col_search: search = st.text_input("QUERY DATABASE...", placeholder="Parameters: Python, OpenAI, Remote...")
            with col_time: time_filter = st.selectbox("TIME RANGE", ["All Active", "Past 24 Hours", "Past 7 Days"])
            st.write("---")
            if time_filter == "Past 24 Hours": df_seeker = df_seeker[df_seeker['date_added'] >= (pd.to_datetime('today') - timedelta(days=1))]
            elif time_filter == "Past 7 Days": df_seeker = df_seeker[df_seeker['date_added'] >= (pd.to_datetime('today') - timedelta(days=7))]
            if search: df_seeker = df_seeker[df_seeker['title'].str.contains(search, case=False) | df_seeker['company'].str.contains(search, case=False)]
            
            df_seeker = df_seeker.sort_values(by='date_added', ascending=False)
            if df_seeker.empty: st.info("No nodes match parameters.")
            else:
                for _, row in df_seeker.iterrows(): display_job_card(row, is_admin=False, user_email=user_email, is_saved=(row['id'] in saved_job_ids))
        
        with tab_saved:
            st.markdown("#### YOUR ENCRYPTED FAVORITES")
            df_saved = df_seeker[df_seeker['id'].isin(saved_job_ids)]
            if df_saved.empty: st.info("You have not saved any datanodes yet. Click ⭐ SAVE NODE on the main grid.")
            else:
                for _, row in df_saved.iterrows(): display_job_card(row, is_admin=False, user_email=user_email, is_saved=True)

        with tab_match:
            with st.container(border=True):
                uploaded_file = st.file_uploader("UPLOAD DATAPACK (PDF)", type="pdf")
            if uploaded_file:
                with st.spinner("Running neural analysis..."):
                    resume_text = extract_text_from_pdf(uploaded_file)
                    
                    if GEMINI_API_KEY:
                        try:
                            model = genai.GenerativeModel("gemini-1.5-flash")
                            job_context = ""
                            for _, r in df_seeker.iterrows(): job_context += f"ID:{r['id']} | Title:{r['title']} | Company:{r['company']} | Desc:{str(r['description'])[:200]}\n"
                            
                            prompt = f"""
                            Candidate Resume Text:
                            {resume_text[:2500]}
                            
                            Active Jobs List:
                            {job_context}
                            
                            Evaluate the candidate's exact experience level and technical skills. 
                            Find the top 3 best matching Job IDs from the list.
                            Return ONLY a comma-separated list of the Job IDs. Do not include any other text or formatting.
                            """
                            response = model.generate_content(prompt)
                            ai_output = response.text.replace('```', '').strip()
                            
                            matched_ids = [i.strip() for i in ai_output.split(',')]
                            matched = df_seeker[df_seeker['id'].isin(matched_ids)]
                            
                            conn = psycopg2.connect(DB_URL)
                            c = conn.cursor()
                            today_str = datetime.now().strftime("%Y-%m-%d")
                            pdf_bytes = uploaded_file.getvalue()
                            
                            skills_prompt = f"Read this resume:\n{resume_text[:2000]}\n\nReturn a clean, comma-separated list of the top 5 technical skills found. Return ONLY the skills, nothing else."
                            skills_response = model.generate_content(skills_prompt)
                            skills_str = skills_response.text.replace('```', '').strip()
                            
                            c.execute("""
                                INSERT INTO user_resumes (user_email, resume_data, skills_text, date_uploaded)
                                VALUES (%s, %s, %s, %s)
                                ON CONFLICT (user_email) 
                                DO UPDATE SET resume_data = EXCLUDED.resume_data, skills_text = EXCLUDED.skills_text, date_uploaded = EXCLUDED.date_uploaded
                            """, (user_email, psycopg2.Binary(pdf_bytes), skills_str, today_str))
                            conn.commit()
                            conn.close()
                            st.toast("⚡ Resume secure-uplinked to Neural Databank!")
                            
                            if not matched.empty:
                                st.success("🟢 Google Gemini Deep-Neural Analysis Complete.")
                                st.markdown(f"#### >>> TOP MATCHES ({len(matched)}):")
                                for _, row in matched.iterrows(): display_job_card(row, is_admin=False, user_email=user_email, is_saved=(row['id'] in saved_job_ids))
                            else: st.info("Gemini analysis complete. No perfect matches found right now.")
                            
                        except Exception as e: st.error(f"Gemini Analysis failed: {e}")
                    else:
                        st.warning("⚠️ Gemini API Key not found. Falling back to Keyword Heuristics.")
                        skills = [s for s in ['python', 'sql', 'react', 'java', 'ai', 'data', 'llm', 'machine learning', 'pytorch', 'prompt engineering'] if s in resume_text]
                        if skills:
                            matched = df_seeker[df_seeker['title'].str.lower().str.contains('|'.join(skills))]
                            if not matched.empty:
                                st.markdown(f"#### >>> MATCHES FOUND ({len(matched)}):")
                                for _, row in matched.head(10).iterrows(): display_job_card(row, is_admin=False, user_email=user_email, is_saved=(row['id'] in saved_job_ids))
                            else: st.info("No matching active nodes currently active.")
                        else: st.warning("Analysis failed. No valid parameters detected.")
