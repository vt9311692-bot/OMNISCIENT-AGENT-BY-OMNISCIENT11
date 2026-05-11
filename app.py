import streamlit as st
import csv
import json
import os
import random
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
def save_key_to_env(key):
    with open(".env", "w") as f:
        f.write(f"GROQ_API_KEY={key}\n")
    os.environ["GROQ_API_KEY"] = key

# --- APP CONFIG ---
st.set_page_config(page_title="OMNISCIENT AGENT | IPL Akinator", page_icon="🧠", layout="centered")

# --- HINGLISH HUMOR LINES ---
LOADING_LINES = [
    "Dimaag ke neurons jala raha hoon... 🔥",
    "Cricket ka Wikipedia kholke padh raha hoon... 📚",
    "Apna AI wala dimag ghuma raha hoon... 🌀",
    "Bhai sahab, thoda wait karo... soch raha hoon 🤔",
    "Neural network mein IPL highlights dekh raha hoon... 📺",
]
WELCOME_LINES = [
    "Ek IPL cricketer socho, main pakad lunga! 🏏",
    "Bhai kisi bhi IPL player ko soch, mera dimaag bhot tez hai! 🧠",
    "Socho koi bhi cricketer... main OMNISCIENT hoon, yaad rakhna 😎",
]
WRONG_GUESS_LINES = [
    "Yaar galat? Koi nahi, agli baar pakad lunga! 💪",
    "Arey yaar, chalo aur try karte hain... abhi toh main garam ho raha hoon 🔥",
    "Galat guess? Impossible... chalo ek aur chance do 😤",
]

# --- APPLE MUSIC DARK GLASSMORPHISM CSS ---
def inject_apple_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* === DARK APPLE MUSIC BASE === */
    .stApp {
        background: #0a0a0a !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #ffffff !important;
    }

    /* Animated gradient orbs */
    .stApp::before {
        content: "";
        position: fixed;
        top: -20%; left: -10%;
        width: 50vw; height: 50vw;
        background: radial-gradient(circle, rgba(252, 60, 68, 0.15), rgba(252, 60, 68, 0.05) 40%, transparent 70%);
        z-index: 0;
        filter: blur(80px);
        pointer-events: none;
        animation: orb1 8s ease-in-out infinite alternate;
    }

    .stApp::after {
        content: "";
        position: fixed;
        bottom: -20%; right: -15%;
        width: 60vw; height: 60vw;
        background: radial-gradient(circle, rgba(175, 82, 222, 0.12), rgba(90, 200, 250, 0.06) 40%, transparent 70%);
        z-index: 0;
        filter: blur(100px);
        pointer-events: none;
        animation: orb2 10s ease-in-out infinite alternate;
    }

    @keyframes orb1 {
        0% { transform: translate(0, 0) scale(1); }
        100% { transform: translate(5vw, 3vh) scale(1.15); }
    }
    @keyframes orb2 {
        0% { transform: translate(0, 0) scale(1); }
        100% { transform: translate(-4vw, -5vh) scale(1.1); }
    }

    /* Hide Streamlit chrome */
    header { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    .main .block-container {
        padding-top: 4rem !important;
        max-width: 580px !important;
        position: relative;
        z-index: 1;
    }

    /* === GLASS CARD === */
    [data-testid="stVerticalBlock"] > div:has(div.glass-card) {
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(40px) saturate(150%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(150%) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 24px !important;
        padding: 2rem 2.2rem !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05) !important;
        margin-bottom: 1.5rem !important;
    }

    /* Fallback: style ALL container blocks */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(40px) saturate(150%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(150%) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 24px !important;
        padding: 2rem 2.2rem !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05) !important;
        margin-bottom: 1.5rem !important;
    }

    /* === TYPOGRAPHY === */
    .main-title {
        font-size: 2.6rem !important;
        font-weight: 900 !important;
        text-align: center !important;
        letter-spacing: -1.5px !important;
        background: linear-gradient(135deg, #fc3c44, #af52de, #5ac8fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0 !important;
        animation: titleGlow 3s ease-in-out infinite alternate;
    }

    @keyframes titleGlow {
        0% { filter: brightness(1); }
        100% { filter: brightness(1.2); }
    }

    .tagline {
        text-align: center !important;
        color: rgba(255,255,255,0.45) !important;
        font-size: 0.95rem !important;
        font-weight: 400 !important;
        letter-spacing: 0.5px;
        margin-bottom: 2.5rem !important;
    }

    /* All text white */
    .stMarkdown, .stMarkdown p, .stMarkdown span, label, .stTextInput label {
        color: rgba(255,255,255,0.85) !important;
    }
    h1, h2, h3, h4 {
        color: #ffffff !important;
    }

    /* === BUTTONS === */
    .stButton > button {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important;
        padding: 0.8rem 0.5rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px) !important;
        width: 100% !important;
        white-space: nowrap !important;
    }

    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(252, 60, 68, 0.4) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(252, 60, 68, 0.15) !important;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #fc3c44, #d63384) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 20px rgba(252, 60, 68, 0.3) !important;
    }

    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 30px rgba(252, 60, 68, 0.4) !important;
    }

    /* === INPUT FIELD === */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.7rem 1rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #fc3c44 !important;
        box-shadow: 0 0 0 2px rgba(252, 60, 68, 0.2) !important;
    }

    /* === PROGRESS BAR === */
    div[data-testid="stProgress"] > div > div > div > div {
        background: linear-gradient(90deg, #fc3c44, #af52de, #5ac8fa) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stProgress"] > div > div > div {
        background: rgba(255,255,255,0.05) !important;
    }

    /* === AI COMMENT BUBBLE === */
    .ai-bubble {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        padding: 10px 20px;
        border-radius: 20px 20px 20px 4px;
        font-style: italic;
        font-size: 0.88rem;
        color: rgba(255,255,255,0.6);
        margin-bottom: 1.5rem;
        display: inline-block;
        border: 1px solid rgba(255,255,255,0.06);
        animation: fadeSlideUp 0.5s ease-out;
    }

    /* === SAHI PAKDE HAI RESULT === */
    .sahi-pakde {
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        text-align: center;
        color: #34d399;
        margin-bottom: 0.5rem;
        animation: bounceIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        text-shadow: 0 0 30px rgba(52, 211, 153, 0.3);
    }

    .result-name {
        font-size: 3rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #fc3c44, #af52de, #5ac8fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin: 0.5rem 0 1rem;
        animation: fadeSlideUp 0.8s ease-out;
    }

    .result-badge {
        background: rgba(252, 60, 68, 0.1);
        border: 1px solid rgba(252, 60, 68, 0.2);
        border-radius: 100px;
        padding: 6px 18px;
        font-size: 0.85rem;
        color: #fc3c44;
        display: inline-block;
        margin: 4px;
    }

    /* === ANIMATIONS === */
    @keyframes fadeSlideUp {
        0% { opacity: 0; transform: translateY(15px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    @keyframes bounceIn {
        0% { opacity: 0; transform: scale(0.3); }
        50% { transform: scale(1.1); }
        100% { opacity: 1; transform: scale(1); }
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    .probe-label {
        color: rgba(255,255,255,0.4);
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .probe-count {
        color: #fc3c44;
        font-size: 1.3rem;
        font-weight: 800;
    }
    .candidates-count {
        color: #5ac8fa;
        font-size: 1.3rem;
        font-weight: 800;
    }

    /* Spinner override */
    .stSpinner > div > div {
        border-top-color: #fc3c44 !important;
    }
    </style>
    """, unsafe_allow_html=True)

inject_apple_css()

# --- DATA LOADING (merges ALL datasets) ---
@st.cache_data
def load_data():
    players = []
    seen_names = set()
    
    def add_player(name, team="", role="", nationality="", nickname="", funny="", tag=""):
        name = name.strip()
        if name and name.lower() not in seen_names:
            players.append({
                "Name": name, "Team": team, "Role": role,
                "Nationality": nationality, "Nickname": nickname,
                "FunnyName": funny, "Tag": tag,
            })
            seen_names.add(name.lower())
    
    # Source 1: IPL_Players_Dataset.xlsx (primary, has funny names)
    try:
        import openpyxl
        xlsx1 = os.path.join("src", "IPL_Players_Dataset.xlsx")
        if os.path.exists(xlsx1):
            wb = openpyxl.load_workbook(xlsx1, read_only=True)
            ws = wb.active
            headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
            for row in ws.iter_rows(min_row=2, values_only=True):
                d = {headers[i]: (row[i] if i < len(row) else "") for i in range(len(headers))}
                add_player(
                    name=str(d.get("Player Name", "") or ""),
                    team=str(d.get("Team", "") or ""),
                    role=str(d.get("Role", "") or ""),
                    nationality=str(d.get("Nationality", "") or ""),
                    nickname=str(d.get("Nickname", "") or ""),
                    funny=str(d.get("Funny Name / Description", "") or ""),
                    tag=str(d.get("Special Tag", "") or ""),
                )
            wb.close()
    except Exception as e:
        st.error(f"Dataset 1 error: {e}")
    
    # Source 2: all_ipl_players_200plus.xlsx
    try:
        import openpyxl
        xlsx2 = os.path.join("src", "all_ipl_players_200plus.xlsx")
        if os.path.exists(xlsx2):
            wb = openpyxl.load_workbook(xlsx2, read_only=True)
            ws = wb.active
            headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
            name_col = "Player Name" if "Player Name" in headers else "Name"
            for row in ws.iter_rows(min_row=2, values_only=True):
                d = {headers[i]: (row[i] if i < len(row) else "") for i in range(len(headers))}
                add_player(
                    name=str(d.get(name_col, "") or ""),
                    team=str(d.get("Team", d.get("IPL Team", "")) or ""),
                    role=str(d.get("Role", "") or ""),
                    nationality=str(d.get("Nationality", "") or ""),
                )
            wb.close()
    except Exception as e:
        st.error(f"Dataset 2 error: {e}")
    
    # Source 3: CSV fallback
    try:
        if os.path.exists("top_100_ipl_players.csv"):
            with open("top_100_ipl_players.csv", mode='r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    add_player(
                        name=row.get("Name", ""),
                        team=row.get("Team", row.get("IPL Team", "")),
                        role=row.get("Role", ""),
                        nationality=row.get("Nationality", ""),
                    )
    except Exception:
        pass
    
    if not players:
        players = [{"Name": "MS Dhoni", "Team": "CSK"}, {"Name": "Virat Kohli", "Team": "RCB"}]
    
    return players[:170]

# --- INITIALIZE SESSION STATE (always reload fresh data) ---
if "game_state" not in st.session_state:
    st.session_state.game_state = "start"

# Initialize players list if not present
if "all_players" not in st.session_state:
    st.session_state.all_players = load_data()

if "remaining_players" not in st.session_state or st.session_state.game_state == "start":
    # If starting fresh, we might want to reload if the files changed, 
    # but for speed during play, we use the cached version.
    if st.session_state.game_state == "start":
        st.session_state.all_players = load_data()
    st.session_state.remaining_players = list(st.session_state.all_players)
if "history" not in st.session_state:
    st.session_state.history = []
if "count" not in st.session_state:
    st.session_state.count = 0
if "undo_stack" not in st.session_state:
    st.session_state.undo_stack = []
if "current_q" not in st.session_state:
    st.session_state.current_q = None
if "final_guess" not in st.session_state:
    st.session_state.final_guess = None

# --- GROQ LOGIC ---
def get_client():
    api_key = os.getenv("GROQ_API_KEY", st.session_state.get("api_key", ""))
    if not api_key: return None
    try:
        return Groq(api_key=api_key)
    except: return None

def call_groq(prompt):
    client = get_client()
    if not client: return None
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are OMNISCIENT AGENT, an IPL cricket expert. Always refer to the player as a singular individual (use 'Is he...', 'Does he...', 'Is the player...'). Never use plural 'they' or 'are' for the individual. ALL questions and comments must be in ENGLISH ONLY. No Hindi. Use fun team nicknames: CSK=Whistle Podu Gang, MI=Paltan, RCB=Royal Chokers, KKR=Shah Rukh XI, SRH=Orange Army, DC=Capital Punishers, RR=Royals, PBKS=Punjab Kings, GT=Titans, LSG=Nawabs. Output STRICTLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2048,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"⚠️ Groq API Error: {str(e)}")
        return None

def get_next_question():
    remaining = st.session_state.remaining_players
    if len(remaining) <= 1 or st.session_state.count >= 8:
        return make_guess()

    # Limit the pool info sent to AI to save tokens and improve split accuracy
    # Limit the pool info to 20 players for ultra-fast response times.
    pool_sample = remaining[:20]
    pool = [{"name": p["Name"], "team": p.get("Team",""), "role": p.get("Role",""), "nat": p.get("Nationality","")} for p in pool_sample]
    
    # Build list of already-asked questions to prevent repeats
    asked = [h["q"] for h in st.session_state.history]
    asked_str = "\n".join(f"- {q}" for q in asked) if asked else "None yet"
    
    topics = ["nationality", "playing role", "IPL team", "batting hand", "bowling type", "captaincy", "era", "wicketkeeper"]
    remaining_topics = [t for t in topics if not any(t.lower() in q.lower() for q in asked)]
    
    prompt = f"""Players with their data: {pool}

ALREADY ASKED (DO NOT repeat):
{asked_str}

Suggested NEW topics: {remaining_topics}
Questions left: {8 - st.session_state.count}

STRICT RULES:
1. Ask ONE NEW cricket Yes/No question DIFFERENT from all above.
2. REFER TO THE PLAYER AS AN INDIVIDUAL (use 'Is he...', 'Does he...'). Do NOT use 'they' or 'are'.
3. Use the player data (team, role, nationality) to classify ACCURATELY.
4. ONLY ask about: nationality, role, team, batting hand, bowling style, captaincy, era, wicketkeeper.
5. NEVER ask about names, letters, alphabets. BANNED.
6. EVERY player MUST be in yes_players or no_players. No missing players.
7. Split into TWO roughly EQUAL halves.
8. Short witty English comment. No Hindi.

Return JSON: {{"question": "...", "ai_personality_comment": "...", "yes_players": [...], "no_players": [...]}}"""
    with st.spinner(random.choice(LOADING_LINES)):
        res = call_groq(prompt)
        if res:
            st.session_state.current_q = res
            st.rerun()
        else:
            st.error("Neural sectors are unresponsive (AI error). Try clicking again or check your API key.")

def make_guess():
    remaining = st.session_state.remaining_players
    candidates = [p["Name"] for p in remaining]
    prompt = f"""Answers so far: {st.session_state.history}
Remaining: {candidates}

Pick the BEST match. Add a fun English celebration line.
Return JSON: {{"guess": "...", "confidence": "...", "reasoning": "...", "celebration": "..."}}"""
    
    with st.spinner("Locking in final answer... 🔒"):
        res = call_groq(prompt)
        if res:
            st.session_state.final_guess = res
            st.session_state.game_state = "result"
            st.rerun()
        else:
            st.error("Failed to finalize prediction. Neural feedback loop broken.")

# --- UI RENDERING ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    if st.button("🔑 Change API Key"):
        if os.path.exists(".env"):
            os.remove(".env")
        # Clear env var for current session
        if "GROQ_API_KEY" in os.environ:
            del os.environ["GROQ_API_KEY"]
        st.session_state.game_state = "start"
        st.rerun()
    st.markdown("---")
    st.caption("OMNISCIENT v2.3 | 8B Ultra-Fast")

st.markdown("<h1 class='main-title'>OMNISCIENT AGENT</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline'>The Invisible Mind of IPL Cricket 🧠🏏</p>", unsafe_allow_html=True)

if st.session_state.game_state == "start":
    # Auto-detect key from environment or secrets
    env_key = os.getenv("GROQ_API_KEY", "")
    
    with st.container():
        st.markdown("<div class='glass-card'></div>", unsafe_allow_html=True)
        st.markdown(f"### {random.choice(WELCOME_LINES)}")
        st.write("")
        
        if env_key:
            st.success("✅ Neural Connection Established (API Key Active)")
            if st.button("🚀 Start Guessing!", type="primary", use_container_width=True):
                st.session_state.api_key = env_key
                st.session_state.game_state = "playing"
                get_next_question()
        else:
            api_key_input = st.text_input("🔑 Groq API Key (Neural Access)", type="password", value=st.session_state.get("api_key", ""))
            st.write("")
            if st.button("🚀 Shuru Karo!", type="primary", use_container_width=True):
                if api_key_input:
                    st.session_state.api_key = api_key_input
                    save_key_to_env(api_key_input)
                    st.session_state.game_state = "playing"
                    get_next_question()
                else:
                    st.error("Bhai pehle API key toh daal! 🔑")

elif st.session_state.game_state == "playing":
    q = st.session_state.current_q
    if not q:
        get_next_question()
    else:
        with st.container():
            st.markdown("<div class='glass-card'></div>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns([1,1])
            with col_a:
                st.markdown(f"<div><span class='probe-label'>PROBE</span><br><span class='probe-count'>{st.session_state.count + 1} / 8</span></div>", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"<div style='text-align:right'><span class='probe-label'>SUSPECTS</span><br><span class='candidates-count'>{len(st.session_state.remaining_players)}</span></div>", unsafe_allow_html=True)
            
            st.progress(st.session_state.count / 8.0)
            
            comment = q.get('ai_personality_comment', 'Hmm... soch raha hoon...')
            st.markdown(f"<div class='ai-bubble'>💬 {comment}</div>", unsafe_allow_html=True)
            st.subheader(q.get('question', 'Scanning neural patterns...'))
            
            c1, c2 = st.columns(2)
            
            def handle_ans(ans):
                st.session_state.undo_stack.append({
                    "remaining_players": list(st.session_state.remaining_players),
                    "history": list(st.session_state.history),
                    "count": st.session_state.count,
                    "current_q": st.session_state.current_q
                })
                st.session_state.history.append({"q": q["question"], "a": ans})
                
                prev_pool = list(st.session_state.remaining_players)
                
                def extract_name(n):
                    if isinstance(n, dict):
                        return str(n.get("name", n.get("Name", ""))).strip().lower()
                    return str(n).strip().lower()
                
                yes_set = set(extract_name(n) for n in q.get("yes_players", []))
                no_set = set(extract_name(n) for n in q.get("no_players", []))
                
                if ans == "Yes":
                    st.session_state.remaining_players = [
                        p for p in st.session_state.remaining_players 
                        if p["Name"].strip().lower() in yes_set or p["Name"].strip().lower() not in no_set
                    ]
                elif ans == "No":
                    st.session_state.remaining_players = [
                        p for p in st.session_state.remaining_players 
                        if p["Name"].strip().lower() in no_set or p["Name"].strip().lower() not in yes_set
                    ]
                
                if len(st.session_state.remaining_players) == 0:
                    st.session_state.remaining_players = prev_pool
                    
                st.session_state.count += 1
                st.session_state.current_q = None
                st.rerun()

            with c1: 
                if st.button("✅ Haan", type="primary", use_container_width=True): handle_ans("Yes")
                if st.button("🤷 Shayad", use_container_width=True): handle_ans("Maybe")
            with c2: 
                if st.button("❌ Nahi", use_container_width=True): handle_ans("No")
                if st.button("↩️ Undo", use_container_width=True, disabled=not st.session_state.undo_stack):
                    last = st.session_state.undo_stack.pop()
                    st.session_state.remaining_players = last["remaining_players"]
                    st.session_state.history = last["history"]
                    st.session_state.count = last["count"]
                    st.session_state.current_q = last["current_q"]
                    st.rerun()

elif st.session_state.game_state == "result":
    res = st.session_state.final_guess
    with st.container():
        st.markdown("<div class='glass-card'></div>", unsafe_allow_html=True)
        
        # THE BIG REVEAL
        st.markdown("<div class='sahi-pakde'>🎯 SAHI PAKDE HAI! 🎯</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-name'>{res['guess']}</div>", unsafe_allow_html=True)
        
        # Celebration line from AI
        celebration = res.get('celebration', 'Bhai main toh genius hoon! 😎')
        st.markdown(f"<div class='ai-bubble'>🎉 {celebration}</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<span class='result-badge'>🎯 {res['confidence']}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<span class='result-badge'>🧠 {st.session_state.count} probes</span>", unsafe_allow_html=True)
        
        st.write("")
        st.write(f"**Reasoning:** {res['reasoning']}")
        st.write("")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 Naya Game!", type="primary", use_container_width=True):
                st.session_state.game_state = "start"
                st.session_state.remaining_players = list(st.session_state.all_players)
                st.session_state.history = []
                st.session_state.count = 0
                st.session_state.current_q = None
                st.session_state.final_guess = None
                st.rerun()
        with col_b:
            if st.button("😤 Galat Hai!", use_container_width=True):
                st.session_state.remaining_players = [p for p in st.session_state.remaining_players if p["Name"] != res["guess"]]
                if len(st.session_state.remaining_players) == 0:
                    st.error("Database khatam ho gaya bhai! 😅")
                    st.session_state.game_state = "start"
                else:
                    st.session_state.game_state = "playing"
                    st.session_state.current_q = None
                st.rerun()
