import streamlit as st
import requests
import sqlite3
import pandas as pd
import os
import PyPDF2
import uuid
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta

# ==========================================
# 1. PRODUCTION CONFIGURATION & SECRETS
# ==========================================
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]
ADMIN_EMAILS = [st.secrets["ADMIN_EMAIL"]]

# ==========================================
# 2. FUTURISTIC UI & ANIMATIONS (V2.0)
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
    .app-title-maintenance { background: linear-gradient(90deg, #ff4757 0%, #ff6b81 100%) !important; -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0px 0px 25px rgba(255, 71, 87, 0.5) !important;}
    .system-status { font-family: 'Share Tech Mono', monospace; color: #00ffcc; font-size: 0.9rem; margin-bottom: 25px; animation: blink 2s linear infinite; }
    .system-status-offline { color: #ff4757 !important; text-shadow: 0 0 10px #ff4757 !important; }
    @keyframes blink { 0%, 100% { opacity: 1; text-shadow: 0 0 10px #00ffcc; } 50% { opacity: 0.4; text-shadow: none; } }
    .cyber-btn { display: inline-block; margin-top: 20px; padding: 15px 40px; background: rgba(0, 242, 254, 0.1); color: #00f2fe !important; font-family: 'Share Tech Mono', monospace; font-size: 1.2rem; font-weight: bold; text-decoration: none; border: 1px solid #00f2fe; border-radius: 4px; text-transform: uppercase; letter-spacing: 2px; transition: all 0.3s ease; box-shadow: inset 0 0 10px rgba(0, 242, 254, 0.1), 0 0 15px rgba(0, 242, 254, 0.2); }
    .cyber-btn:hover { background: #00f2fe; color: #050810 !important; box-shadow: 0 0 30px rgba(0, 242, 254, 0.8); transform: scale(1.05); }
    .admin-bypass-btn { margin-top: 15px; font-size: 0.8rem !important; border: 1px solid #ff4757 !important; color: #ff4757 !important; background: transparent !important; box-shadow: none !important;}
    .admin-bypass-btn:hover { background: #ff4757 !important; color: white !important; box-shadow: 0 0 20px #ff4757 !important; }
    .app-title-small { font-size: 2.5rem; font-weight: 900; background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #b06ab3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0px 0px 15px rgba(0, 242, 254, 0.3); margin-bottom: 0px; text-transform: uppercase; }
    
    /* NEW: CYBER WARNING BANNER */
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
    """, unsafe_allow_html=True)

apply_futuristic_css()

# ==========================================
# 3. DATABASE SETUP (With Warning Columns)
# ==========================================
USER_HOME = os.path.expanduser("~") 
DB_PATH = os.path.join(USER_HOME, 'ai_jobs_production.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, title TEXT, company TEXT, location TEXT, url TEXT, source TEXT, description TEXT, salary_amount TEXT, salary_type TEXT)''')
    try: c.execute("ALTER TABLE jobs ADD COLUMN date_added TEXT")
    except sqlite3.OperationalError: pass
    
    c.execute('''CREATE TABLE IF NOT EXISTS sys_settings (id INTEGER PRIMARY KEY, is_maintenance INTEGER, resume_time TEXT, message TEXT)''')
    c.execute("INSERT OR IGNORE INTO sys_settings (id, is_maintenance, resume_time, message) VALUES (1, 0, '', '')")
    
    # Auto-upgrade DB for warning messages
    try: c.execute("ALTER TABLE sys_settings ADD COLUMN is_warning INTEGER DEFAULT 0")
    except sqlite3.OperationalError: pass
    try: c.execute("ALTER TABLE sys_settings ADD COLUMN warning_msg TEXT DEFAULT ''")
    except sqlite3.OperationalError: pass

    conn.commit()
    conn.close()

init_db()

# ==========================================
# 4. ENGINE & HELPER FUNCTIONS
# ==========================================
def get_sys_status():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT is_maintenance, resume_time, message, is_warning, warning_msg FROM sys_settings WHERE id=1")
    row = c.fetchone()
    conn.close()
    
    is_maint, res_time, msg, is_warn, warn_msg = row[0], row[1], row[2], row[3], row[4]
    
    if is_maint == 1 and res_time:
        if datetime.now() > datetime.strptime(res_time, "%Y-%m-%d %H:%M:%S"):
            conn = sqlite3.connect(DB_PATH)
            conn.cursor().execute("UPDATE sys_settings SET is_maintenance=0, is_warning=0 WHERE id=1")
            conn.commit()
            conn.close()
            return (0, "", "", 0, "")
    return (is_maint, res_time, msg, is_warn, warn_msg)

def clean_html(raw_html):
    if not raw_html: return "No details."
    return BeautifulSoup(raw_html, "html.parser").get_text(separator="\n").strip()

def run_auto_job_engine():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    new_count = 0
    today_str = datetime.now().strftime("%Y-%m-%d")
    keywords = ['ai', 'machine learning', 'data', 'llm', 'python', 'artificial intelligence', 'prompt', 'deep learning', 'nlp', 'openai', 'pytorch']
    
    api_urls = ["https://remotive.com/api/remote-jobs?category=data", "https://remotive.com/api/remote-jobs?category=software-dev"]
    for url in api_urls:
        try:
            req = requests.get(url)
            for job in req.json().get('jobs', []):
                if any(word in job.get('title', '').lower() for word in keywords):
                    try:
                        c.execute("""INSERT INTO jobs (id, title, company, location, url, source, description, salary_amount, salary_type, date_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                  (str(job['id']), job['title'], job['company_name'], job['candidate_required_location'], job['url'], 'Remotive API', clean_html(job.get('description', ''))[:1500] + "...", job.get('salary', 'N/A') or 'N/A', 'Yearly', today_str))
                        new_count += 1
                    except sqlite3.IntegrityError: pass
        except: pass

    try:
        feed = feedparser.parse("https://weworkremotely.com/categories/remote-programming-jobs.rss")
        for entry in feed.entries:
            title = entry.title
            if any(word in title.lower() for word in keywords):
                try:
                    job_id = "WWR_" + str(uuid.uuid5(uuid.NAMESPACE_URL, entry.link))[:8]
                    company = title.split(":")[0] if ":" in title else "Unknown"
                    job_title = title.split(":")[1] if ":" in title else title
                    c.execute("""INSERT INTO jobs (id, title, company, location, url, source, description, salary_amount, salary_type, date_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                              (job_id, job_title.strip(), company.strip(), "Remote", entry.link, 'WWR RSS', clean_html(entry.description)[:1500] + "...", 'N/A', 'Unspecified', today_str))
                    new_count += 1
                except sqlite3.IntegrityError: pass
    except: pass

    conn.commit()
    conn.close()
    return new_count

def extract_text_from_pdf(uploaded_file):
    try: return "".join([page.extract_text() + " " for page in PyPDF2.PdfReader(uploaded_file).pages]).lower()
    except: return ""

def display_job_card(row, is_admin=False):
    is_expired = False
    if is_admin and row['date_added'] < str(datetime.now() - timedelta(days=30))[:10]:
        is_expired = True

    with st.container(border=True):
        col_icon, col_details, col_action = st.columns([1, 7, 2])
        with col_icon:
            st.markdown(f"<div class='company-avatar'>{row['company'][0].upper() if row['company'] else 'X'}</div>", unsafe_allow_html=True)
        with col_details:
            title_html = f"<h3 style='margin-bottom:0px; color:#ffffff;'>{row['title']}</h3>"
            if is_expired: title_html = f"<h3 style='margin-bottom:0px; color:#ff4757;'>[EXPIRED] {row['title']}</h3>"
            st.markdown(title_html, unsafe_allow_html=True)
            st.markdown(f"<p style='color:#8892b0; font-size: 1.1rem; margin-top: 5px;'>{row['company']}</p>", unsafe_allow_html=True)
            sal = f"{row['salary_amount']} / {row['salary_type']}" if row['salary_amount'] != "N/A" else "Unlisted"
            date_str = str(row['date_added'])[:10]
            st.markdown(f"<span class='tech-tag'>LOC: {row['location']}</span> <span class='tech-tag'>PAY: {sal}</span> <span class='tech-tag'>DATE: {date_str}</span>", unsafe_allow_html=True)
        with col_action:
            st.write("")
            st.link_button("INITIATE UPLINK", row['url'], use_container_width=True, type="primary")
        with st.expander("DECRYPT DATAFILE (View Description)"):
            st.write(row['description'])

# ==========================================
# 5. LOGIN SYSTEM & MAINTENANCE CHECK
# ==========================================
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_role' not in st.session_state: st.session_state['user_role'] = None
if 'user_name' not in st.session_state: st.session_state['user_name'] = ""

is_maint, res_time, maint_msg, is_warn, warn_msg = get_sys_status()

if is_maint == 1 and st.session_state['user_role'] != "admin":
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
                <a href="{auth_url}" class="cyber-btn admin-bypass-btn" target="_blank">ADMIN OVERRIDE LOGIN</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.stop() 

if not st.session_state['logged_in']:
    if 'code' in st.query_params:
        with st.spinner("Decrypting neural pathways..."):
            code = st.query_params['code']
            res = requests.post("https://oauth2.googleapis.com/token", data={"code": code, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "redirect_uri": REDIRECT_URI, "grant_type": "authorization_code"})
            if res.status_code == 200:
                user_data = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {res.json().get('access_token')}"}).json()
                st.session_state.update({'logged_in': True, 'user_name': user_data.get("name"), 'user_role': "admin" if user_data.get("email") in ADMIN_EMAILS else "seeker"})
                st.query_params.clear()
                st.rerun()
            else: 
                st.error("Access Denied. Invalid authorization protocols.")
    else:
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=openid%20email%20profile"
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div class="login-wrapper">
                <div class="login-card">
                    <p class="system-status">[ SYSTEM STATUS: SECURE & ONLINE ]</p>
                    <div class="app-title-large">NEURAL</div>
                    <div class="app-title-large" style="font-size: 2.5rem; margin-bottom: 20px;">// TALENT GRID</div>
                    <p style="color: #8892b0; font-size: 1.1rem; line-height: 1.5; margin-bottom: 30px;">
                        The premier decentralized hub for Artificial Intelligence, Large Language Models, and Data Science operatives.
                    </p>
                    <a href="{auth_url}" class="cyber-btn" target="_blank">CONNECT DATASTREAM</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 6. MAIN APP DASHBOARDS
# ==========================================
else:
    # GLOBAL WARNING BANNER (Shows if Stage 1 is active)
    if is_warn == 1:
        st.markdown(f"<div class='cyber-warning-banner'>⚠️ SYSTEM NOTICE: {warn_msg}</div>", unsafe_allow_html=True)

    col_logo, col_logout = st.columns([8, 1])
    with col_logo: 
        st.markdown('<p class="app-title-small">NEURAL // JOBS</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: #00ffcc; font-family: \'Share Tech Mono\', monospace; margin-top: -5px;">> Uplink established. Operator: {st.session_state["user_name"]}</p>', unsafe_allow_html=True)
    with col_logout:
        st.write("") 
        if st.button("DISCONNECT"):
            st.session_state.update({'logged_in': False, 'user_role': None, 'user_name': ""})
            st.rerun()

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM jobs", conn)
    conn.close()
    if 'date_added' in df.columns: df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce').fillna(pd.to_datetime('today'))
    else: df['date_added'] = pd.to_datetime('today')

    # --- ADMIN VIEW ---
    if st.session_state['user_role'] == "admin":
        st.markdown("### [ GRID METRICS ]")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("TOTAL DATANODES", len(df))
        m2.metric("API FEEDS", len(df[df['source'] != 'Manual']) if not df.empty else 0)
        m3.metric("MANUAL INSERTS", len(df[df['source'] == 'Manual']) if not df.empty else 0)
        
        if is_maint == 1:
            m4.metric("SYSTEM STATUS", "MAINTENANCE")
            st.error(f"⚠️ SITE IS OFFLINE FOR USERS. Auto-resumes at: {res_time}")
        elif is_warn == 1:
            m4.metric("SYSTEM STATUS", "WARNING ACTIVE")
        else:
            m4.metric("SYSTEM STATUS", "ONLINE")
            
        st.write("---")

        tab1, tab2, tab3, tab4 = st.tabs(["[ RUN ENGINE ]", "[ INJECT DATA ]", "[ NODE LIST ]", "[ ⚙️ SYS CONTROLS ]"])
        
        with tab4:
            st.markdown("#### Stage 1: Global Broadcast (Warning)")
            st.write("Send a pulsing orange banner to all active users without turning the site off yet.")
            if is_warn == 0:
                with st.form("warn_form"):
                    w_msg = st.text_input("Warning Message", value="System maintenance will begin in 15 minutes. Please save your work.")
                    if st.form_submit_button("📢 BROADCAST WARNING"):
                        conn = sqlite3.connect(DB_PATH)
                        conn.cursor().execute("UPDATE sys_settings SET is_warning=?, warning_msg=? WHERE id=1", (1, w_msg))
                        conn.commit()
                        conn.close()
                        st.rerun()
            else:
                if st.button("🔇 CLEAR WARNING"):
                    conn = sqlite3.connect(DB_PATH)
                    conn.cursor().execute("UPDATE sys_settings SET is_warning=0, warning_msg='' WHERE id=1")
                    conn.commit()
                    conn.close()
                    st.rerun()

            st.write("---")
            st.markdown("#### Stage 2: System Lockdown (Maintenance)")
            st.write("Activate this to kick everyone off the grid. Only you can log in.")
            if is_maint == 0:
                with st.form("maint_form"):
                    downtime_hours = st.number_input("Hours of Downtime", min_value=1, max_value=48, value=2)
                    m_msg = st.text_input("Lockdown Message", value="We are upgrading the core neural network. Stand by.")
                    if st.form_submit_button("🚨 INITIATE LOCKDOWN", type="primary"):
                        resume_calc = (datetime.now() + timedelta(hours=downtime_hours)).strftime("%Y-%m-%d %H:%M:%S")
                        conn = sqlite3.connect(DB_PATH)
                        conn.cursor().execute("UPDATE sys_settings SET is_maintenance=?, resume_time=?, message=? WHERE id=1", (1, resume_calc, m_msg))
                        conn.commit()
                        conn.close()
                        st.rerun()
            else:
                if st.button("✅ DEACTIVATE LOCKDOWN"):
                    conn = sqlite3.connect(DB_PATH)
                    conn.cursor().execute("UPDATE sys_settings SET is_maintenance=0 WHERE id=1")
                    conn.commit()
                    conn.close()
                    st.rerun()

        with tab1:
            if st.button(">>> INITIATE GLOBAL SCRAPE", type="primary", use_container_width=True):
                with st.spinner("Extracting web data..."):
                    st.success(f"Successfully extracted {run_auto_job_engine()} new nodes!")
                    st.rerun()
        with tab2:
            with st.container(border=True):
                with st.form("manual"):
                    m_title = st.text_input("Job Title")
                    m_company = st.text_input("Entity / Company")
                    c1, c2 = st.columns(2)
                    with c1: m_sal_amount = st.text_input("Compensation")
                    with c2: m_sal_type = st.selectbox("Cycle", ["Yearly", "Monthly", "Hourly", "Unspecified"])
                    m_url = st.text_input("Uplink URL")
                    m_desc = st.text_area("File Contents")
                    if st.form_submit_button("INJECT NODE", type="primary"):
                        conn = sqlite3.connect(DB_PATH)
                        today_str = datetime.now().strftime("%Y-%m-%d")
                        conn.cursor().execute("INSERT INTO jobs (id, title, company, location, url, source, description, salary_amount, salary_type, date_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                              ("MAN_"+str(uuid.uuid4())[:8], m_title, m_company, "Remote", m_url, "Manual", m_desc or "No desc", m_sal_amount or "N/A", m_sal_type, today_str))
                        conn.commit()
                        conn.close()
                        st.success("Injection Successful.")
                        st.rerun()
        with tab3:
            if df.empty: st.info("Grid empty. Run global scrape.")
            else:
                df = df.sort_values(by='date_added', ascending=False)
                for _, row in df.iterrows(): display_job_card(row, is_admin=True)

    # --- SEEKER VIEW ---
    elif st.session_state['user_role'] == "seeker":
        thirty_days_ago = pd.to_datetime('today') - timedelta(days=30)
        df_seeker = df[df['date_added'] >= thirty_days_ago].copy()

        tab_browse, tab_match = st.tabs(["[ GRID SEARCH ]", "[ AI OVERRIDE ]"])
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
                for _, row in df_seeker.iterrows(): display_job_card(row, is_admin=False)
                
        with tab_match:
            with st.container(border=True):
                uploaded_file = st.file_uploader("UPLOAD DATAPACK (PDF)", type="pdf")
            if uploaded_file:
                with st.spinner("Running neural analysis..."):
                    skills = [s for s in ['python', 'sql', 'react', 'java', 'ai', 'data', 'llm', 'machine learning', 'pytorch'] if s in extract_text_from_pdf(uploaded_file)]
                    if skills:
                        st.success(f"**Parameters Found:** {', '.join(skills).title()}")
                        st.write("---")
                        matched = df_seeker[df_seeker['title'].str.lower().str.contains('|'.join(skills))]
                        if not matched.empty:
                            st.markdown(f"#### >>> MATCHES FOUND ({len(matched)}):")
                            for _, row in matched.head(10).iterrows(): display_job_card(row, is_admin=False)
                        else: st.info("No matching active nodes currently active.")
                    else: st.warning("Analysis failed. No valid parameters detected.")
