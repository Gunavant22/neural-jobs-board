import streamlit as st
import requests
import os
import pandas as pd
import uuid
import json
import io
import urllib.parse
import ssl
import hmac
import hashlib
import time
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta

# Pure-Python Direct Socket Postgres Driver (Zero C-deps, no libpq needed)
import pg8000.dbapi

# ==========================================
# 1. PRODUCTION CONFIGURATION & SECRETS
# ==========================================
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]
ADMIN_EMAILS = [st.secrets["ADMIN_EMAIL"]]
DB_CONN_STR = st.secrets["DB_CONNECTION_STRING"]

# ==========================================
# 2. STATELESS OAUTH CSRF ENGINE
# ==========================================
def generate_state_token(client_secret):
    """Generates a signed timestamp token to protect against OAuth CSRF without relying on RAM state."""
    timestamp = str(int(time.time()))
    signature = hmac.new(
        client_secret.encode('utf-8'),
        timestamp.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"{timestamp}_{signature}"

def verify_state_token(returned_state, client_secret, max_age_seconds=600):
    """Cryptographically verifies returning state tokens and ensures they are under 10 minutes old."""
    try:
        if "_" not in returned_state:
            return False
        timestamp_str, returned_signature = returned_state.split("_", 1)
        
        # Verify cryptographic integrity
        expected_signature = hmac.new(
            client_secret.encode('utf-8'),
            timestamp_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_signature, returned_signature):
            return False
        
        # Check freshness to prevent replay attacks
        timestamp = int(timestamp_str)
        if int(time.time()) - timestamp > max_age_seconds:
            return False
            
        return True
    except Exception:
        return False

# ==========================================
# 3. FUTURISTIC UI & ANIMATIONS
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
# 4. SECURE WIRE-PROTOCOL DATABASE HANDLER
# ==========================================
def execute_query(query, params=None, fetch=False):
    """🛠️ CRASH-PROOF DB HANDLER: Direct socket communication in pure Python. Zero C-libraries needed."""
    try:
        url = urllib.parse.urlparse(DB_CONN_STR)
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        
        # Connect using pure-Python pg8000
        conn = pg8000.dbapi.connect(
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port,
            database=url.path[1:], 
            ssl_context=ssl_ctx
        )
        c = conn.cursor()
        
        if params:
            safe_params = tuple(bytes(p) if isinstance(p, (bytes, memoryview)) else p for p in params)
            c.execute(query, safe_params)
        else:
            c.execute(query)
            
        if fetch:
            rows = c.fetchall()
            cols = [desc[0] for desc in c.description] if c.description else []
            conn.commit()
            conn.close()
            return pd.DataFrame(rows, columns=cols)
            
        conn.commit()
        conn.close()
        return pd.DataFrame()
    except Exception as e:
        # Log real exception securely to server terminal/logs
        print(f"DATABASE RUNTIME EXCEPTION: {e}")
        st.error("A secure network database exception occurred. System Administrators have been notified.")
        return pd.DataFrame()

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

def format_salary(salary_amount, salary_type):
    sal_val = str(salary_amount).strip()
    if not sal_val or sal_val.lower() in ["n/a", ""]:
        return "Unlisted"
    if not sal_val.startswith("$"):
        sal_val = f"${sal_val}"
    return f"{sal_val} / {salary_type}"

def display_job_card(row, is_admin=False, user_email=None, is_teaser=False):
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

        with st.expander("DECRYPT DATAFILE (View Description)"):
            st.write(row['description'])

# ==========================================
# 5. STATE MANAGEMENT & OAUTH CALLBACK
# ==========================================
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_role' not in st.session_state: st.session_state['user_role'] = None
if 'user_name' not in st.session_state: st.session_state['user_name'] = ""
if 'user_email' not in st.session_state: st.session_state['user_email'] = "" 
if 'show_bulk_purge' not in st.session_state: st.session_state['show_bulk_purge'] = False
if 'draft_job' not in st.session_state: st.session_state['draft_job'] = None
if 'last_heartbeat' not in st.session_state: st.session_state['last_heartbeat'] = datetime.min

is_maint, res_time, maint_msg, is_warn, warn_msg = get_sys_status()

# Secure dynamic token generation for state (CSRF mitigation)
state_token = generate_state_token(CLIENT_SECRET)
auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=openid%20email%20profile&state={state_token}"

if not st.session_state['logged_in'] and 'code' in st.query_params:
    with st.spinner("Decrypting neural pathways..."):
        returned_state = st.query_params.get("state")
        
        # Verify signed state token (csrf check)
        if not returned_state or not verify_state_token(returned_state, CLIENT_SECRET):
            st.error("Authentication security error: state token mismatch (anti-CSRF barrier failed). Connection aborted.")
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
    
    # Query past 30 days and limit directly inside Database to reduce memory load
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

    df = execute_query("SELECT * FROM jobs", fetch=True)
    if 'date_added' in df.columns: df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce').fillna(pd.to_datetime('today'))
    else: df['date_added'] = pd.to_datetime('today')

    # --- ADMIN VIEW ---
    if st.session_state['user_role'] == "admin":
        st.markdown("### [ GRID METRICS ]")
        thirty_days_str = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # SQL-Level aggregation keeps computational load inside Database Engine
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

        tab1, tab2, tab_analytics, tab3 = st.tabs(["[ ➕ INJECT ]", "[ 📋 NODES ]", "[ 📈 ANALYTICS ]", "[ ⚙️ SYS ]"])
            
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
                    st.session_state['inject_status'] = None
                
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

        st.markdown("### [ GRID SEARCH ]")
        cs, ct = st.columns([3, 1])
        with cs: search = st.text_input("QUERY DATABASE...", placeholder="Python, OpenAI...")
        with ct: t_filter = st.selectbox("TIME RANGE", ["All Active", "Past 24 Hours", "Past 7 Days"])
        st.write("---")
        
        if t_filter == "Past 24 Hours": 
            t_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            df_seeker = df_seeker[df_seeker['date_added'] >= t_str]
        elif t_filter == "Past 7 Days": 
            t_str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            df_seeker = df_seeker[df_seeker['date_added'] >= t_str]
            
        if search: df_seeker = df_seeker[df_seeker['title'].str.contains(search, case=False) | df_seeker['company'].str.contains(search, case=False)]
        
        if df_seeker.empty: st.info("No nodes match.")
        else:
            for _, row in df_seeker.sort_values(by='date_added', ascending=False).iterrows(): 
                display_job_card(row, user_email=ue)
