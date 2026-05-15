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
    "Burning through neural patterns... 🔥",
    "Just warming up, calculating the odds! 🧠",
    "Searching the Cricket Encyclopedia... 📚",
    "Checking the pacer's speed! ⚡",
    "Watching IPL highlights in the neural network... 📺",
    "Looking for a spin wizard! 🪄",
    "Checking for stat-padders... 🧐",
    "Shaun Pollock level precision in the death overs! 🏏",
    "Digging through IPL history, hang on! 🏏",
    "Patience, data crunching in progress! 🧠",
    "Taking a catch at the boundary, wait! 🏃‍♂️",
]
WELCOME_LINES = [
    "Think of an IPL cricketer, I'll find them! 🏏",
    "Mind reader mode active! Think of a special player! 🧠",
    "Think of any player, my mind is faster than Google! ⚡",
    "I am OMNISCIENT, don't forget it! 😎",
    "Pick a tough player! A dark horse perhaps? 🏇",
    "I am the cricket encyclopedia, try me! 📖",
]
WRONG_GUESS_LINES = [
    "Wait, that's wrong? You actually got me out! 💪",
    "Let's try again... I was just warming up anyway! 🔥",
    "Wrong guess? Impossible... you must have given me the wrong info! 😤",
    "You just bowled a perfect googly! Let's reset the field. 🔄",
    "A swing and a miss! Let's go for another round. 🏏",
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
    
    # Final enforcement of 170 players as requested
    return players[:170]

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
    st.session_state.remaining_players = list(st.session_state.all_players)
# Force reload if pool size exceeds 170 (enforcing user constraint)
elif len(st.session_state.all_players) > 170:
    st.session_state.all_players = st.session_state.all_players[:170]
    st.session_state.remaining_players = [p for p in st.session_state.remaining_players if p in st.session_state.all_players]

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

    # 1. Try Cerebras (Optimized for speed)
    if current_key.startswith("csk-"):
        if not HAS_CEREBRAS:
            st.error("⚠️ Cerebras module not installed. Please run: pip install cerebras-cloud-sdk")
            return None
        import time
        for attempt in range(3):
            try:
                client = Cerebras(api_key=current_key)
                response = client.chat.completions.create(
                    model="llama3.1-8b",
                    messages=[
                        {"role": "system", "content": "You are OMNISCIENT AGENT - CRICKET MIND READER 🧠🏏. MISSION: Identify player using career FACTS ONLY. BANNED: No future predictions or opinions. No specific names unless pool < 3. Output ONLY JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1500,
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content.strip()
                if "```json" in content: content = content.split("```json")[1].split("```")[0]
                elif "```" in content: content = content.split("```")[1].split("```")[0]
                return json.loads(content.strip())
            except Exception as e:
                err_msg = str(e).lower()
                if ("rate" in err_msg or "queue" in err_msg or "traffic" in err_msg) and attempt < 2:
                    time.sleep(2)
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
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash-latest",
                system_instruction="You are OMNISCIENT AGENT - CRICKET MIND READER 🧠🏏. MISSION: Identify player using career FACTS ONLY. BANNED: No future predictions or opinions. Output ONLY JSON."
            )
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
                    model=model_name if model_name else "llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are OMNISCIENT AGENT - CRICKET MIND READER 🧠🏏. MISSION: Identify player using career FACTS ONLY. BANNED: No predictions or opinions. HUMOR: Use savage Hinglish humor in the ai_personality_comment. Output ONLY JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0,
                    max_tokens=1500,
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content.strip()
                # Fallback for unexpected markdown
                if "```json" in content: content = content.split("```json")[1].split("```")[0]
                elif "```" in content: content = content.split("```")[1].split("```")[0]
                return json.loads(content.strip())
            except Exception as e:
                err_msg = str(e).lower()
                if ("rate" in err_msg or "429" in err_msg) and attempt < 2:
                    time.sleep(5)
                    continue
                st.error(f"⚠️ Groq API Error: {str(e)}")
                return None

    # 4. Try OpenRouter (Kimi K2.6 Support)
    if current_key.startswith("sk-or-"):
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {current_key}",
                "HTTP-Referer": "https://github.com/omniscient-agent", # Required by OpenRouter
                "X-Title": "Omniscient Agent",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_name if model_name else "moonshotai/kimi-k2.6",
                "messages": [
                    {"role": "system", "content": "You are OMNISCIENT AGENT - CRICKET MIND READER 🧠🏏. MISSION: Identify player using career FACTS ONLY. BANNED: No predictions or opinions. HUMOR: Use savage Hinglish humor in the ai_personality_comment. Output ONLY JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.0,
                "max_tokens": 1500,
                "response_format": {"type": "json_object"}
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content'].strip()
            if "```json" in content: content = content.split("```json")[1].split("```")[0]
            elif "```" in content: content = content.split("```")[1].split("```")[0]
            return json.loads(content.strip())
        except Exception as e:
            st.error(f"⚠️ OpenRouter Error: {str(e)}")
            return None

    st.error("Unrecognized API Key format. Use Cerebras (csk-), Gemini (AIza), Groq (gsk), or OpenRouter (sk-or-).")
    return None

def get_next_question():
    remaining = st.session_state.remaining_players
    if len(remaining) <= 1 or st.session_state.count >= 8:
        return make_guess()

    # Token-efficient indexing with Metadata for 100% AI accuracy
    pool_data = "| ".join([f"{i}:{p['Name']}({p.get('Team','?')},{p.get('Role','?')})" for i, p in enumerate(remaining)])
    past_questions = [h['q'] for h in st.session_state.history]
    history_str = ", ".join([f"{h['q']}={h['a']}" for h in st.session_state.history])
    
    prompt = f"""
POOL: {pool_data}
HISTORY: {history_str}
BANNED QUESTIONS: {past_questions}

TASK: Generate ONE smart Yes/No fact question to split the POOL 50/50.
STRICT RULES:
1. NEVER ask a question from BANNED list.
2. Use Team/Role from POOL to ensure 100% accuracy in yes_indices.
3. Savage Hinglish humor in comments.

JSON:
{{
  "thought": "Why is this not a repeat?",
  "question": "English Question",
  "ai_personality_comment": "Savage Hinglish Roast",
  "yes_indices": []
}}"""
    with st.spinner(random.choice(LOADING_LINES)):
        for attempt in range(3):
            res = call_ai(prompt)
            if res:
                q_text = res.get("question", "").lower()
                banned = ["will ", "next match", "score a", "hit a", "century in", "tomorrow", "tonight"]
                # Reject if prediction or name-dropping in large pool
                if any(b in q_text for b in banned) or (len(remaining) > 5 and any(p['Name'].lower() in q_text for p in remaining[:3])):
                    continue
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
    
    # Identify winner using metadata (Cap at 20 to avoid token limit explosions)
    candidates_data = "; ".join([f"{p['Name']} ({p.get('Team')}, {p.get('Role')}, {p.get('FunnyName')})" for p in remaining[:20]])
    
    prompt = f"""
OMNISCIENT AGENT - ANTI-GRAVITY FINAL VERDICT MODE 🎯

Game History:
{history_lines}

Remaining Candidates:
{candidates_data}

🔍 CRITICAL TASK:
1. Analyze EVERY yes/no answer in history
2. Identify which 2-3 SPECIFIC answers were GAME-CHANGERS (narrowed pool most)
3. Use "anti-gravity detection" - highlight unique characteristics that stood out
4. Name the ONE player who matches ALL conditions

📝 REASONING RULES:
- Write reasoning as ONE flowing paragraph (NO lists/JSON formatting inside reasoning)
- Mention 2-3 KEY answers that led to the player
- Use Hinglish language naturally
- Example: "Bhai, dekho logic. Aapne kaha opening batsman hai, right-hander, aur overseas... Virat Kohli toh RCB mein khelta hai, left-hander bhi nahi. Toh obviously ye Faf du Plessis hona chahiye!"
- Highlight ANTI-GRAVITY traits: overseas vs domestic, big hitter vs accumulator, etc.

🎉 CELEBRATION:
- Short, witty, confident one-liner
- Use cricket slang: "Chakka maara!", "Six aya!", "Boundary nikala!", "Wicket gira!", "Googly daal di!", "Neural network ne catch pakad liya!" etc.

JSON OUTPUT (MANDATORY):
{{
  "guess": "EXACT Player Name",
  "confidence": "92%",
  "reasoning": "Full paragraph explaining 2-3 key answers that confirm this player",
  "celebration": "One-liner witty remark about the victory"
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
        for k in ["GEMINI_API_KEY", "CEREBRAS_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY"]:
            if k in os.environ: del os.environ[k]
        if "api_key" in st.session_state:
            del st.session_state["api_key"]
        st.session_state.game_state = "start"
        st.rerun()
    st.markdown("### 💡 API Key Help")
    st.info("""
    **New Flagship Model Active:**
    Use an **OpenRouter Key** to try the agentic **Kimi K2.6** model!
    """)
    st.markdown("[Get OpenRouter Key](https://openrouter.ai/keys)")
    st.markdown("[Get Groq Key](https://console.groq.com/keys)")
    st.markdown("[Get Gemini Key](https://aistudio.google.com/app/apikey)")
    
    st.markdown("---")
    st.caption("OMNISCIENT v2.8 | Llama 3.1 8B Optimized")

st.markdown("<h1 class='main-title'>OMNISCIENT AGENT</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline'>🧠 CRICKET MIND READER MODE | The Invisible Mind of IPL 🏏</p>", unsafe_allow_html=True)

    if st.session_state.game_state == "start":
    env_key = os.getenv("OPENROUTER_API_KEY", os.getenv("CEREBRAS_API_KEY", os.getenv("GEMINI_API_KEY", os.getenv("GROQ_API_KEY", ""))))
    
    with st.container():
        st.markdown("<div class='glass-card'></div>", unsafe_allow_html=True)
        st.markdown(f"### {random.choice(WELCOME_LINES)}")
        st.write("")
        
        if env_key:
            if env_key.startswith("sk-or-"): provider = "OpenRouter (Kimi K2.6)"
            elif env_key.startswith("csk-"): provider = "Cerebras"
            elif env_key.startswith("AIza"): provider = "Gemini"
            else: provider = "Groq"
            
            st.success(f"✅ Active Provider: **{provider}**")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🚀 Start Guessing!", type="primary", use_container_width=True):
                    st.session_state.api_key = env_key
                    st.session_state.game_state = "playing"
                    get_next_question()
            with c2:
                if st.button("🔑 Switch Key", use_container_width=True):
                    if os.path.exists(".env"): os.remove(".env")
                    for k in ["GEMINI_API_KEY", "CEREBRAS_API_KEY", "GROQ_API_KEY"]:
                        if k in os.environ: del os.environ[k]
                    if "api_key" in st.session_state: del st.session_state["api_key"]
                    st.session_state.game_state = "start"
                    st.rerun()
        else:
            st.info("Paste your API key below to connect to the Neural Network.")
            api_key_input = st.text_input("🔑 API Key", type="password", placeholder="Paste Groq, Gemini, or Cerebras key here...")
            
            col1, col2 = st.columns(2)
            with col1:
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
            
            comment = q.get('ai_personality_comment', 'Hmm... thinking...')
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
                
                # Filter pool based on indices (Robust integer conversion)
                yes_indices = set(int(i) for i in q.get("yes_indices", []))
                
                if ans == "Yes":
                    st.session_state.remaining_players = [
                        p for i, p in enumerate(st.session_state.remaining_players)
                        if i in yes_indices
                    ]
                elif ans == "No":
                    st.session_state.remaining_players = [
                        p for i, p in enumerate(st.session_state.remaining_players)
                        if i not in yes_indices
                    ]
                # If "Maybe", we don't filter the pool at all, just proceed to next question.
                
                if len(st.session_state.remaining_players) == 0:
                    st.session_state.remaining_players = prev_pool
                    
                st.session_state.count += 1
                st.session_state.current_q = None
                st.rerun()

            with c1: 
                if st.button("✅ Yes", type="primary", use_container_width=True): handle_ans("Yes")
                if st.button("🤷 Maybe", use_container_width=True): handle_ans("Maybe")
            with c2: 
                if st.button("❌ No", use_container_width=True): handle_ans("No")
                if st.button("↩️ Undo", use_container_width=True, disabled=not st.session_state.undo_stack):
                    last = st.session_state.undo_stack.pop()
                    st.session_state.remaining_players = last["remaining_players"]
                    st.session_state.history = last["history"]
                    st.session_state.count = last["count"]
                    st.session_state.current_q = last["current_q"]
                    st.rerun()
            
            st.markdown("---")
            if st.button("🔑 Change API Key", use_container_width=True):
                if os.path.exists(".env"): os.remove(".env")
                for k in ["GEMINI_API_KEY", "CEREBRAS_API_KEY", "GROQ_API_KEY"]:
                    if k in os.environ: del os.environ[k]
                if "api_key" in st.session_state: del st.session_state["api_key"]
                st.session_state.game_state = "start"
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
        reasoning_text = res.get('reasoning', 'Pure calculation and data analysis.')
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
        
        st.markdown("---")
        if st.button("🔑 Change API Key", use_container_width=True):
            if os.path.exists(".env"): os.remove(".env")
            for k in ["GEMINI_API_KEY", "CEREBRAS_API_KEY", "GROQ_API_KEY"]:
                if k in os.environ: del os.environ[k]
            if "api_key" in st.session_state: del st.session_state["api_key"]
            st.session_state.game_state = "start"
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
        
        st.markdown("---")
        if st.button("🔑 Change API Key", use_container_width=True):
            if os.path.exists(".env"): os.remove(".env")
            for k in ["GEMINI_API_KEY", "CEREBRAS_API_KEY", "GROQ_API_KEY"]:
                if k in os.environ: del os.environ[k]
            if "api_key" in st.session_state: del st.session_state["api_key"]
            st.session_state.game_state = "start"
            st.rerun()
