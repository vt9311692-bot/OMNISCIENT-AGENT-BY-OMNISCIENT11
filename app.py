import streamlit as st
import csv
import json
import os
import random
from groq import Groq
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    from cerebras.cloud.sdk import Cerebras
    HAS_CEREBRAS = True
except ImportError:
    HAS_CEREBRAS = False
from dotenv import load_dotenv

load_dotenv()
def save_key_to_env(key):
    # Clear all potential keys from current environment first
    for k in ["GEMINI_API_KEY", "CEREBRAS_API_KEY", "GROQ_API_KEY"]:
        if k in os.environ: del os.environ[k]
        
    # Detect key type
    if key.startswith("AIza"): key_name = "GEMINI_API_KEY"
    elif key.startswith("csk-"): key_name = "CEREBRAS_API_KEY"
    else: key_name = "GROQ_API_KEY"
    
    with open(".env", "w") as f:
        f.write(f"{key_name}={key}\n")
    os.environ[key_name] = key

# --- APP CONFIG ---
st.set_page_config(page_title="OMNISCIENT AGENT | IPL Akinator", page_icon="🧠", layout="centered")

# --- HINGLISH HUMOR LINES ---
LOADING_LINES = [
    "Dimaag ke neurons jala raha hoon... 🔥",
    "Abhi warm-up kar raha hoon, calculation ka chakkar! 🧠",
    "Cricket ka Wikipedia kholke padh raha hoon... 📚",
    "Pacer ki speed check karunga! ⚡",
    "Neural network mein IPL highlights dekh raha hoon... 📺",
    "Spinner ka wizard dhoond raha hoon! 🪄",
    "Stat padder hai kya? Ruk check karne de... 🧐",
    "Death overs mein ye toh Shaun Pollock level! 🏏",
    "IPL ki history khangal raha hoon, wait kar! 🏏",
    "Bhai sahab, thoda sabar karo... data crunch ho raha hai! 🧠",
    "Boundary pe catch pakad raha hoon, thoda wait! 🏃‍♂️",
]
WELCOME_LINES = [
    "Ek IPL cricketer socho, main uska career nikaal dunga! 🏏",
    "Mind reader mode activate! Koi special player socho! 🧠",
    "Bhai koi bhi player socho, mera dimaag Google se tez hai! ⚡",
    "Socho koi bhi cricketer... main OMNISCIENT hoon, bhulna mat 😎",
    "Arey bhai, koi tough player socho! Yeh toh dark horse player lag raha hai. 🏇",
    "Cricket ka encyclopedia hoon main, try me! 📖",
]
WRONG_GUESS_LINES = [
    "Yaar galat? Beta tumne toh out kar diya! 💪",
    "Arey yaar, chalo aur try karte hain... abhi toh main warm-up kar raha hoon 🔥",
    "Galat guess? Impossible... shayad tumne galat info di! 😤",
    "Bhai, tumne toh googly daal di! Chalo phir se field set karte hain. 🔄",
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
        padding: 12px 20px;
        border-radius: 20px 20px 20px 4px;
        font-size: 0.95rem;
        line-height: 1.4;
        color: rgba(255,255,255,0.85);
        margin-bottom: 1.5rem;
        display: block;
        border: 1px solid rgba(255,255,255,0.1);
        animation: fadeSlideUp 0.5s ease-out;
        max-width: 90%;
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
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 100px;
        padding: 8px 20px;
        font-size: 0.9rem;
        font-weight: 600;
        color: #ffffff;
        display: inline-block;
        margin: 4px;
        backdrop-filter: blur(10px);
    }

    .probe-label, .suspects-label {
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        color: rgba(255,255,255,0.4);
        text-transform: uppercase;
    }

    .probe-count, .candidates-count {
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.2;
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

    /* === INSIGHT BOX === */
    .insight-box {
        background: rgba(255, 255, 255, 0.03);
        border-left: 3px solid #fc3c44;
        padding: 15px 20px;
        border-radius: 4px 16px 16px 4px;
        font-size: 0.95rem;
        line-height: 1.5;
        color: rgba(255,255,255,0.8);
        margin: 1rem 0;
    }
    .insight-label {
        color: #fc3c44;
        font-weight: 700;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
        display: block;
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
    
    return players[:250]

# --- INITIALIZE SESSION STATE (always reload fresh data) ---
# Centralized session state reset
if "game_state" not in st.session_state:
    st.session_state.game_state = "start"

def reset_game_state():
    st.session_state.remaining_players = list(st.session_state.all_players)
    st.session_state.history = []
    st.session_state.count = 0
    st.session_state.undo_stack = []
    st.session_state.current_q = None
    st.session_state.final_guess = None

# Initialize players list if not present
if "all_players" not in st.session_state:
    st.session_state.all_players = load_data()

if st.session_state.game_state == "start":
    reset_game_state()

# Ensure keys exist even if not in start state
for key, default in [("history", []), ("count", 0), ("undo_stack", []), ("current_q", None), ("final_guess", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- AI LOGIC ---
def call_ai(prompt, model_name=None):
    # Determine which key to use (Session state takes priority over .env)
    current_key = st.session_state.get("api_key", os.getenv("CEREBRAS_API_KEY", os.getenv("GEMINI_API_KEY", os.getenv("GROQ_API_KEY", ""))))
    
    if not current_key:
        st.error("No API Key detected. Please enter a key on the start screen.")
        return None

    # 1. Try Cerebras (with auto-retry for queue_exceeded)
    if current_key.startswith("csk-"):
        if not HAS_CEREBRAS:
            st.error("⚠️ Cerebras module not installed on this server. Please update requirements.txt on GitHub.")
            return None
        import time
        for attempt in range(3):
            try:
                client = Cerebras(api_key=current_key)
                response = client.chat.completions.create(
                    model="llama3.1-8b",
                    messages=[
                        {"role": "system", "content": "You are OMNISCIENT AGENT CRICKET MIND READER MODE 🧠🏏. You are a savage IPL expert using Hinglish humor. Always refer to the player as a singular individual. Output STRICTLY valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                if "```json" in content: content = content.split("```json")[1].split("```")[0]
                elif "```" in content: content = content.split("```")[1].split("```")[0]
                return json.loads(content.strip())
            except Exception as e:
                err_msg = str(e).lower()
                if ("rate" in err_msg or "queue" in err_msg or "traffic" in err_msg) and attempt < 2:
                    time.sleep(1.5 * (attempt + 1)) # Wait and retry
                    continue
                st.error(f"⚠️ Cerebras API Error: {str(e)}")
                return None
    
    # 2. Try Gemini
    if current_key.startswith("AIza"):
        if not HAS_GEMINI:
            st.error("⚠️ Gemini module not installed on this server. Please update requirements.txt on GitHub.")
            return None
        try:
            genai.configure(api_key=current_key)
            # Use 'gemini-1.5-flash-latest' to avoid 404 on some regions
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            content = response.text
            if "```json" in content: content = content.split("```json")[1].split("```")[0]
            elif "```" in content: content = content.split("```")[1].split("```")[0]
            return json.loads(content.strip())
        except Exception as e:
            st.error(f"⚠️ Gemini API Error: {str(e)}")
            return None
    
    # 3. Try Groq
    if current_key.startswith("gsk"):
        import time
        for attempt in range(3):
            try:
                client = Groq(api_key=current_key)
                response = client.chat.completions.create(
                    model=model_name if model_name else "llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are OMNISCIENT AGENT CRICKET MIND READER MODE 🧠🏏. You are a savage IPL expert using Hinglish humor. Always refer to the player as a singular individual. Output ONLY strictly valid JSON. Do not include any preamble or postscript."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2048,
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                # Robust JSON extraction
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                return json.loads(content.strip())
            except Exception as e:
                err_msg = str(e).lower()
                # Groq 429 often contains "rate limit" or "wait"
                if ("rate_limit" in err_msg or "rate limit" in err_msg or "429" in err_msg) and attempt < 2:
                    wait_time = 7.0 if "6.72s" in err_msg or "try again" in err_msg else (attempt + 1) * 3
                    time.sleep(wait_time)
                    continue
                st.error(f"⚠️ Groq API Error: {str(e)}")
                return None
    
    st.error("Unrecognized API Key format. Please use a Cerebras (csk-), Gemini (AIza), or Groq (gsk) key.")
    return None

def get_next_question():
    remaining = st.session_state.remaining_players
    if len(remaining) <= 1 or st.session_state.count >= 8:
        return make_guess()

    # Provide ALL names in the pool to ensure 100% coverage in categorization
    all_names = [p['Name'] for p in remaining]
    pool_data = ", ".join(all_names)
    
    # Provide detailed metadata for a sample to help the AI understand the context
    pool_sample = remaining[:60]
    sample_metadata = "; ".join([f"{p['Name']} ({p.get('Team','?')}, {p.get('Role','?')}, {p.get('Nationality','?')})" for p in pool_sample])
    
    asked = [h["q"] for h in st.session_state.history]
    asked_str = ", ".join(asked) if asked else "None"
    
    prompt = f"""
OMNISCIENT AGENT CRICKET MIND READER MODE 🧠🏏

PLAYER POOL TO CATEGORIZE: {pool_data}

CONTEXT SAMPLE (Stats/Teams): {sample_metadata}

Asked Questions: {asked_str}

🎯 MISSION: Generate ONE laser-focused Yes/No question in HINGLISH that splits the PLAYER POOL 50/50.

📋 CARDINAL RULES (NON-NEGOTIABLE):
1. LANGUAGE: Pure HINGLISH only!
2. PRECISION: EVERY SINGLE PLAYER listed in the "PLAYER POOL TO CATEGORIZE" above MUST be placed in either "yes_players" OR "no_players" (100% coverage mandatory).
3. IMPACT: Question must eliminate minimum 40% of pool, maximum 60% (50/50 ideal).
4. RELEVANCE: Only IPL/Cricket facts - Team, Role, Batting/Bowling Style, Awards, Strike Rate, Age Range.
5. NO OVERLAP: Never repeat asked questions.

🔍 MIND READER STRATEGY:
- Use the "CONTEXT SAMPLE" to identify dividing traits (Overseas vs Domestic, Spinner vs Pacer, etc.).
- Categorize every player from the pool based on your expert cricket knowledge.

💬 AI PERSONALITY (SAVAGE MODE):
Your comment must be funny, roasting, using cricket slang:
- "Yeh toh boundary line par dance karega!" (boundary hitter)
- "Death overs mein ye toh Shaun Pollock level!" (death bowler)
- "Abhi warm-up kar raha hoon, calculation ka chakkar!"
- "Mind reader mode activate! Ye player special hai!" (unique trait)
- "Bhai, ye toh All-rounder hai ya specialist?"
- "Chakka maara ja raha hoga is se!" (big hitter)
- "Spinner ka wizard!" (spin bowler)
- "Pacer ki speed check karunga!" (fast bowler)
- "Opening batsman ka DNA!" (aggressive opener)
- "All-rounder magic!" (bats and bowls)
- "Ye toh dark horse player hai!" (underrated)
- "Cricket ka encyclopedia is player!" (veteran)

JSON FORMAT (STRICT):
{{
  "question": "Hinglish Yes/No Question",
  "ai_personality_comment": "Funny Roasting Remark with Cricket Slang",
  "yes_players": ["Full Name 1", "Full Name 2", ...],
  "no_players": ["Full Name 3", "Full Name 4", ...]
}}

⚡ SMART HACK: Categorize names exactly as they appear in the pool list!"""
    with st.spinner(random.choice(LOADING_LINES)):
        res = call_ai(prompt)
        if res:
            st.session_state.current_q = res
            st.rerun()
        else:
            st.session_state.game_state = "error"
            st.session_state.last_error = "Neural Bridge disconnected. Possible traffic jam in AI sectors."

def make_guess():
    remaining = st.session_state.remaining_players
    candidates = [p["Name"] for p in remaining]
    
    # Format history for the AI to understand it as a conversation
    history_lines = "\n".join([f"Q: {h['q']} | A: {h['a']}" for h in st.session_state.history])
    
    # Identify winner using metadata
    candidates_data = "; ".join([f"{p['Name']} ({p.get('Team')}, {p.get('Role')}, {p.get('FunnyName')})" for p in remaining])
    
    prompt = f"""
OMNISCIENT AGENT CRICKET MIND READER MODE 🧠🏏

Game History: {history_lines}
Candidates: {candidates_data}

🎯 MISSION: Identify the winner with 100% precision.

📋 FINAL GUESS RULES:
1. REASONING: Provide a sharp, detective-style paragraph in HINGLISH. Explain exactly which 2-3 specific answers from the history locked in this player.
2. PERSONALITY: Use 'SAVAGE MODE' humor. Roas the user slightly for how easy or hard they made it.
3. CELEBRATION: A confident, witty Hinglish roasting line that proves you are OMNISCIENT.

JSON FORMAT:
{{
  "guess": "Player Name",
  "confidence": "95-100%",
  "reasoning": "Bhai, simple logic hai! Aapne bola wo overseas hai, SRH ke liye khelta hai, aur left-handed opener hai... toh Travis Head ke alawa aur kaun ho sakta hai? Itna easy mat pucho!",
  "celebration": "Neural Network ne stadium ke bahar chakka maar diya! 😎🏆"
}}"""
    
    with st.spinner("Locking in final answer... 🔒"):
        # Use llama-3.1-8b-instant for the final guess to save cost and increase speed
        res = call_ai(prompt, model_name="llama-3.1-8b-instant")
        if res:
            st.session_state.final_guess = res
            st.session_state.game_state = "result"
            st.rerun()
        else:
            st.session_state.game_state = "error"
            st.session_state.last_error = "Bhai, prediction logic crash ho gayi! Neural feedback loop broke."
            st.rerun()

# --- UI RENDERING ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    if st.button("🔑 Change API Key"):
        if os.path.exists(".env"):
            os.remove(".env")
        # Deep clear all potential keys
        for k in ["GEMINI_API_KEY", "CEREBRAS_API_KEY", "GROQ_API_KEY"]:
            if k in os.environ: del os.environ[k]
        if "api_key" in st.session_state:
            del st.session_state["api_key"]
        st.session_state.game_state = "start"
        st.rerun()
    st.markdown("---")
    st.caption("OMNISCIENT v2.7 | Cerebras Ultra-Fast")

st.markdown("<h1 class='main-title'>OMNISCIENT AGENT</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline'>🧠 CRICKET MIND READER MODE | The Invisible Mind of IPL 🏏</p>", unsafe_allow_html=True)

if st.session_state.game_state == "start":
    env_key = os.getenv("CEREBRAS_API_KEY", os.getenv("GEMINI_API_KEY", os.getenv("GROQ_API_KEY", "")))
    
    with st.container():
        st.markdown("<div class='glass-card'></div>", unsafe_allow_html=True)
        st.markdown(f"### {random.choice(WELCOME_LINES)}")
        st.write("")
        
        if env_key:
            if env_key.startswith("csk-"): provider = "Cerebras"
            elif env_key.startswith("AIza"): provider = "Gemini"
            else: provider = "Groq"
            st.success(f"✅ Neural Connection Established ({provider} Active)")
            if st.button("🚀 Start Guessing!", type="primary", use_container_width=True):
                st.session_state.api_key = env_key
                st.session_state.game_state = "playing"
                get_next_question()
        else:
            api_key_input = st.text_input("🔑 API Key (Cerebras, Gemini, or Groq)", type="password", value=st.session_state.get("api_key", ""))
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
        # Neural Link status indicator
        st.markdown("<div style='text-align: center; margin-bottom: 1rem;'><span class='probe-label' style='color: #fc3c44; animation: pulse 2s infinite;'>● NEURAL LINK ACTIVE</span></div>", unsafe_allow_html=True)
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
                    name_str = ""
                    if isinstance(n, dict):
                        name_str = str(n.get("name", n.get("Name", "")))
                    else:
                        name_str = str(n)
                    # Normalize: lowercase and remove dots/special chars for better matching
                    return name_str.strip().lower().replace(".", "").replace(" ", "")
                
                yes_set = set(extract_name(n) for n in q.get("yes_players", []))
                no_set = set(extract_name(n) for n in q.get("no_players", []))
                
                if ans == "Yes":
                    st.session_state.remaining_players = [
                        p for p in st.session_state.remaining_players 
                        if extract_name(p["Name"]) in yes_set
                    ]
                elif ans == "No":
                    st.session_state.remaining_players = [
                        p for p in st.session_state.remaining_players 
                        if extract_name(p["Name"]) in no_set
                    ]
                # If "Maybe", we don't filter the pool at all, just proceed to next question.
                
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
        reasoning_text = res.get('reasoning', 'Bhai, bas intuition hai! Data toh wahi bol raha hai.')
        st.markdown(f"""
        <div class='insight-box'>
            <span class='insight-label'>🧠 NEURAL INSIGHT</span>
            {reasoning_text}
        </div>
        """, unsafe_allow_html=True)
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
elif st.session_state.game_state == "error":
    with st.container():
        st.markdown("<div class='glass-card'></div>", unsafe_allow_html=True)
        st.error(f"🚨 AGENT ERROR: {st.session_state.get('last_error', 'Unknown breakdown')}")
        st.write("Cerebras, Gemini, or Groq might be hitting rate limits. Wait 10-15 seconds and try again.")
        if st.button("🔄 Retry Connection", type="primary", use_container_width=True):
            st.session_state.game_state = "playing"
            st.session_state.current_q = None
            st.rerun()
        if st.button("🏠 Back to Start"):
            st.session_state.game_state = "start"
            st.rerun()
