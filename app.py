import streamlit as st
import csv
import json
import os
import random
import urllib.parse
import requests
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
    # Clear all potential keys
    for k in ["GEMINI_API_KEY", "CEREBRAS_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY", "SAMBANOVA_API_KEY"]:
        if k in os.environ: del os.environ[k]
    
    if key.startswith("gsk_"): key_name = "GROQ_API_KEY"
    elif key.startswith("csk-"): key_name = "CEREBRAS_API_KEY"
    elif key.startswith("sk-"): key_name = "OPENAI_API_KEY"
    else: key_name = "GROQ_API_KEY" # Fallback to Groq
    
    with open(".env", "w") as f:
        f.write(f"{key_name}={key}\n")
    os.environ[key_name] = key

# --- APP CONFIG ---
st.set_page_config(page_title="OMNISCIENT AGENT | IPL Akinator", page_icon="🧠", layout="centered")

# --- HINGLISH HUMOR LINES ---
LOADING_LINES = [
    "Dimaag ke ghode dauda raha hoon... 🔥",
    "Bas thoda wait, calculation chal rahi hai! 🧠",
    "Cricket encyclopedia scan kar raha hoon... 📚",
    "Pacer ki speed check ho rahi hai! ⚡",
    "Neural network mein IPL highlights dekh raha hoon... 📺",
    "Spin wizard ko search kar raha hoon! 🪄",
    "Stat-padders ko filter kar raha hoon... 🧐",
    "Shaun Pollock level precision death overs mein! 🏏",
    "IPL history check kar raha hoon, ruko zara! 🏏",
    "Patience rakho, data crunch ho raha hai! 🧠",
    "Boundary pe catch pakad raha hoon, wait! 🏃‍♂️",
]
WELCOME_LINES = [
    "Kisi bhi IPL cricketer ke baare mein socho, main pehchan lunga! 🏏",
    "Mind reader mode active! Ek special player socho! 🧠",
    "Koi bhi player socho, mera dimaag Google se bhi fast hai! ⚡",
    "I am OMNISCIENT, bhulna mat! 😎",
    "Koi tough player pick karo! Chhupa rustam hai kya? 🏇",
    "Main cricket ka encyclopedia hoon, try me! 📖",
]
WRONG_GUESS_LINES = [
    "Wait, galat hai? Aapne toh mujhe out kar diya! 💪",
    "Chalo phir se try karte hain... main toh bas warm-up kar raha tha! 🔥",
    "Wrong guess? Impossible... aapne hi galat info di hogi! 😤",
    "Aapne toh perfect googly daal di! Field reset karte hain. 🔄",
    "Swing and a miss! Chalo ek aur round. 🏏",
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
    
    def add_player(name, team="", role="", nationality="", nickname="", funny="", tag="", batting="", bowling="", captain="", keeper="", overseas=""):
        name = name.strip()
        if name and name.lower() not in seen_names:
            # Normalize attributes for logic
            is_overseas = "Yes" if (overseas and str(overseas).lower() == "yes") or (nationality and "indian" not in str(nationality).lower()) else "No"
            players.append({
                "Name": name, "Team": str(team or ""), "Role": str(role or ""),
                "Nationality": str(nationality or ""), "Nickname": str(nickname or ""),
                "FunnyName": str(funny or ""), "Tag": str(tag or ""),
                "Batting": str(batting or ""), "Bowling": str(bowling or ""),
                "Captain": str(captain or ""), "Keeper": str(keeper or ""),
                "Overseas": is_overseas
            })
            seen_names.add(name.lower())
    
    # Source 1: IPL_Players_Dataset.xlsx
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
                    batting=str(d.get("Batting", "") or ""),
                    bowling=str(d.get("Bowling", "") or ""),
                    captain=str(d.get("Captain", "") or ""),
                    keeper=str(d.get("Keeper", "") or ""),
                    overseas=str(d.get("Overseas", "") or "")
                )
            wb.close()
    except Exception: pass
    
    # Source 2: all_ipl_players_200plus.xlsx
    try:
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
                    batting=str(d.get("Batting", "") or ""),
                    bowling=str(d.get("Bowling", "") or ""),
                    overseas=str(d.get("Overseas", "") or "")
                )
            wb.close()
    except Exception: pass
    
    # Source 3: CSV fallback (Highest quality metadata)
    try:
        if os.path.exists("top_100_ipl_players.csv"):
            with open("top_100_ipl_players.csv", mode='r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    add_player(
                        name=row.get("Name", ""),
                        team=row.get("IPL Team", row.get("Team", "")),
                        role=row.get("Role", ""),
                        nationality=row.get("Nationality", ""),
                        batting=row.get("Batting", ""),
                        bowling=row.get("Bowling", ""),
                        captain=row.get("Captain", ""),
                        keeper=row.get("Keeper", ""),
                        overseas=row.get("Overseas", "")
                    )
    except Exception: pass
    
    return players

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

if st.session_state.game_state == "start":
    reset_game_state()

# Ensure keys exist even if not in start state
for key, default in [("history", []), ("count", 0), ("undo_stack", []), ("current_q", None), ("final_guess", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

def call_ai(prompt, model_name=None):
    current_key = st.session_state.get("api_key", os.getenv("GROQ_API_KEY", os.getenv("CEREBRAS_API_KEY", os.getenv("OPENAI_API_KEY", os.getenv("SAMBANOVA_API_KEY", os.getenv("GEMINI_API_KEY", ""))))))
    if not current_key: return None

    def clean_json(text):
        text = text.strip()
        if "```json" in text: text = text.split("```json")[1].split("```")[0]
        elif "```" in text: text = text.split("```")[1].split("```")[0]
        return text.strip()

    # 1. CEREBRAS (THE LATENCY KING - ~1000 tokens/sec)
    if current_key.startswith("csk-"):
        try:
            from cerebras.cloud.sdk import Cerebras
            client = Cerebras(api_key=current_key)
            response = client.chat.completions.create(
                model="llama3.1-8b", 
                messages=[{"role": "system", "content": "You are OMNISCIENT AGENT. MISSION: Factual JSON only."}, {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(clean_json(response.choices[0].message.content))
        except Exception: pass

    # 2. GROQ (ULTRA FAST)
    if current_key.startswith("gsk_"):
        try:
            client = Groq(api_key=current_key)
            response = client.chat.completions.create(
                model=model_name if model_name else "llama-3.1-8b-instant",
                messages=[{"role": "system", "content": "You are OMNISCIENT AGENT. MISSION: Factual JSON only."}, {"role": "user", "content": prompt}],
                temperature=0.0, max_tokens=1000, response_format={"type": "json_object"}
            )
            return json.loads(clean_json(response.choices[0].message.content))
        except Exception: pass

    # 3. GEMINI (FASTEST FROM GOOGLE)
    if current_key.startswith("AIza"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(clean_json(response.text))
        except Exception: pass

    # 4. SAMBANOVA / OPENROUTER (FALLBACK SPEED)
    if len(current_key) > 30: 
        try:
            import requests
            url = "https://api.sambanova.ai/v1/chat/completions" if not current_key.startswith("sk-or-") else "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {current_key}", "Content-Type": "application/json"}
            payload = {
                "model": "Meta-Llama-3.1-8B-Instruct" if "sambanova" in url else "meta-llama/llama-3.1-8b-instruct",
                "messages": [{"role": "system", "content": "You are OMNISCIENT AGENT. MISSION: Factual JSON only."}, {"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
                "temperature": 0.0
            }
            res = requests.post(url, headers=headers, json=payload, timeout=12)
            return json.loads(clean_json(res.json()['choices'][0]['message']['content']))
        except Exception: pass

    # 5. OPENAI / GENERIC
    if current_key.startswith("sk-"):
        try:
            import requests
            headers = {"Authorization": f"Bearer {current_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "system", "content": "You are OMNISCIENT AGENT. MISSION: Factual JSON only."}, {"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }
            res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=12)
            return json.loads(clean_json(res.json()['choices'][0]['message']['content']))
        except Exception: pass

    return None

def get_player_image_url(player_name):
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(player_name)}&prop=pageimages&format=json&pithumbsize=500"
        response = requests.get(url, timeout=5)
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_info in pages.items():
            if "thumbnail" in page_info:
                return page_info["thumbnail"]["source"]
    except Exception:
        pass
    return f"https://ui-avatars.com/api/?name={urllib.parse.quote(player_name)}&background=random&color=fff&size=500"

def get_next_question():
    remaining = st.session_state.remaining_players
    if st.session_state.count >= 12 or (len(remaining) <= 3 and st.session_state.count >= 8):
        return make_guess()

    # Phase 1: Local Statistical Filtering (FAST)
    # Phase 2: Full Neural Filtering (ACCURATE)
    use_local = len(remaining) > 12

    stats = {
        "Overseas": {"Yes": 0, "No": 0},
        "Role": {},
        "Team": {},
        "Batting": {"Right": 0, "Left": 0},
        "Captain": {"Yes": 0, "No": 0},
        "Keeper": {"Yes": 0, "No": 0}
    }
    for p in remaining:
        stats["Overseas"][p.get("Overseas", "No")] = stats["Overseas"].get(p.get("Overseas", "No"), 0) + 1
        r = p.get("Role", "Unknown")
        stats["Role"][r] = stats["Role"].get(r, 0) + 1
        t = p.get("Team", "Unknown")
        stats["Team"][t] = stats["Team"].get(t, 0) + 1
        b = "Left" if "Left" in str(p.get("Batting", "")) else "Right"
        stats["Batting"][b] += 1
        stats["Captain"]["Yes" if "Yes" in str(p.get("Captain", "")) else "No"] += 1
        stats["Keeper"]["Yes" if "Yes" in str(p.get("Keeper", "")) else "No"] += 1

    past_questions = [h['q'] for h in st.session_state.history]
    q_count = st.session_state.count + 1

    with st.spinner(random.choice(LOADING_LINES)):
        # Triple-Lock: Track used logic, categories, and values
        used_logic = [f"{h.get('cat')}:{h.get('val')}" for h in st.session_state.history if 'cat' in h]
        used_cats = [str(h.get('cat')) for h in st.session_state.history if 'cat' in h]
        
        for attempt in range(5): 
            if use_local:
                prompt = f"""
STATS: {stats}
BANNED_LOGIC: {used_logic}
TURN: {q_count}/12
TASK: Pick a TECHNICAL CATEGORY and VALUE from STATS to split the pool 50/50. 
REFINEMENT: Use "Deep Context" for better questions. 
CRITICAL RULE: NEVER use ANY player's actual name in the question. Focus on traits only.
Hints: CSK=Yellow/Thala, RCB=Red/King, MI=Blue/Hitman, KKR=Purple, GT=Titan/Hardik, RR=Pink.
Logic: You can combine traits (e.g. "Kya wo player ek Blue jersey team ka All-rounder hai?")
JSON: {{"category": "...", "value": "...", "question": "Fine Hinglish question", "ai_personality_comment": "Witty roast"}}"""
            else:
                # Show samples to help AI differentiate
                samples = "|".join([f"{p['Name']}({p.get('Team')},{p.get('Role')})" for p in remaining[:5]])
                history_short = [f"Q:{h['q']}|A:{h['a']}" for h in st.session_state.history]
                prompt = f"""
POOL: {samples} ({len(remaining)} total)
HISTORY: {history_short}
TASK: Unique YES/NO question using Deep Context (Rivalries/Traits).
CRITICAL RULE: NEVER use ANY player's actual name in the question! Ask about their traits/stats.
JSON: {{"question": "...", "ai_personality_comment": "...", "yes_indices": [IDs]}}"""

            res = call_ai(prompt)
            if res:
                q_text = res.get("question", "").strip()
                cat = res.get("category")
                val = res.get("value")
                
                # Check for duplicates (Relaxed on last attempt)
                is_dup = any(h['q'].lower().strip() == q_text.lower().strip() for h in st.session_state.history)
                if attempt < 4 and use_local and f"{cat}:{val}" in used_logic: is_dup = True
                
                if is_dup: continue

                if use_local:
                    yes_indices = [i for i, p in enumerate(remaining) if (
                        (cat == "Overseas" and p.get("Overseas") == val) or
                        (cat == "Role" and p.get("Role") == val) or
                        (cat == "Team" and p.get("Team") == val) or
                        (cat == "Batting" and val in str(p.get("Batting", ""))) or
                        (cat == "Captain" and (("Yes" in str(p.get("Captain", ""))) if val == "Yes" else ("Yes" not in str(p.get("Captain", ""))))) or
                        (cat == "Keeper" and (("Yes" in str(p.get("Keeper", ""))) if val == "Yes" else ("Yes" not in str(p.get("Keeper", "")))))
                    )]
                    
                    if not yes_indices or len(yes_indices) == len(remaining): continue
                    res["yes_indices"] = yes_indices
                    res["cat"], res["val"] = cat, val
                
                if not res.get("yes_indices") and not use_local: continue
                
                st.session_state.current_q = res
                st.rerun()
        else:
            # EMERGENCY FALLBACK: Pick a category that hasn't been used much
            templates = {
                "Role": "primarily ek {} hai?",
                "Team": "{} ke liye khelta hai?",
                "Overseas": "ek Overseas player hai?",
                "Batting": "ek {} batsman hai?",
                "Captain": "apni team ka Captain hai?",
                "Keeper": "ek Wicket-keeper hai?"
            }
            for cat, temp in templates.items():
                if cat not in used_cats:
                    vals = [p.get(cat) for p in remaining if p.get(cat)]
                    if vals:
                        val = vals[0]
                        # Special handling for boolean-style values
                        q_text = f"Kya wo player {temp.format(val)}" if "{}" in temp else f"Kya wo player {temp}"
                        if cat == "Overseas" and val == "No": continue # Skip Indian fallback
                        
                        yes_indices = [i for i, p in enumerate(remaining) if (
                            (cat == "Overseas" and p.get("Overseas") == val) or
                            (cat == "Role" and p.get("Role") == val) or
                            (cat == "Team" and p.get("Team") == val) or
                            (cat == "Batting" and val in str(p.get("Batting", ""))) or
                            (cat == "Captain" and (("Yes" in str(p.get("Captain", ""))) if val == "Yes" else ("Yes" not in str(p.get("Captain", ""))))) or
                            (cat == "Keeper" and (("Yes" in str(p.get("Keeper", ""))) if val == "Yes" else ("Yes" not in str(p.get("Keeper", "")))))
                        )]
                        
                        if 0 < len(yes_indices) < len(remaining):
                            st.session_state.current_q = {
                                "question": q_text,
                                "ai_personality_comment": "Neural link stable, just keeping it simple! 😎",
                                "yes_indices": yes_indices,
                                "cat": cat, "val": val
                            }
                            st.rerun()
            
            # FINAL FALLBACK: Ask a generic team question to keep it moving
            if remaining:
                p = remaining[0]
                st.session_state.current_q = {
                    "question": f"Kya wo player {p.get('Team', 'ek special team')} ke liye khelta hai?",
                    "ai_personality_comment": "Hmm, lagta hai aap mujhe fasa rahe ho... 👀",
                    "yes_indices": [i for i, pl in enumerate(remaining) if pl.get('Team') == p.get('Team')],
                    "cat": "Team", "val": p.get("Team")
                }
                st.rerun()
            
            st.session_state.game_state = "error"
            st.session_state.last_error = "Neural Bridge is jammed. Please refresh and try a different player!"
            st.rerun()

def make_guess():
    remaining = st.session_state.remaining_players
    candidates = [p["Name"] for p in remaining]
    
    # Format history for the AI to understand it as a conversation
    history_lines = " | ".join([f"Q:{h['q']}-A:{h['a']}" for h in st.session_state.history])
    
    # Identify winner using metadata (Cap at 10 to avoid token limit explosions)
    candidates_data = "; ".join([f"{p['Name']} ({p.get('Team')}, {p.get('Role')})" for p in remaining[:10]])
    
    prompt = f"""
FINAL VERDICT MODE 🎯
History: {history_lines}
Candidates: {candidates_data}

TASK: 
1. Identify the ONE player matching the answers.
2. Write 1 Hinglish paragraph reasoning matching 2-3 key answers.
3. Witty 1-liner celebration.

JSON:
{{
  "guess": "EXACT Name",
  "confidence": "90%",
  "reasoning": "Hinglish paragraph explaining key answers",
  "celebration": "Witty 1-liner"
}}"""
    
    with st.spinner("Locking in final answer... 🎯"):
        # Strategy: Use a more accurate model (70B) for the final guess if possible
        # We try 8B first for speed, then 70B for precision if it fails
        res = call_ai(prompt)
        if not res:
            # Fallback to a larger model or retry
            res = call_ai(prompt, model_name="llama-3.1-70b-versatile")
            
        if res:
            st.session_state.final_guess = res
            st.session_state.game_state = "result"
            st.rerun()
        else:
            st.session_state.game_state = "error"
            st.session_state.last_error = "Bhai, prediction logic crash ho gayi! Pool might be too fragmented. Please restart!"
            st.rerun()

# --- UI RENDERING ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    if st.button("🔑 Change API Key"):
        if os.path.exists(".env"):
            os.remove(".env")
        for k in ["GEMINI_API_KEY", "CEREBRAS_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY", "SAMBANOVA_API_KEY", "OPENAI_API_KEY"]:
            if k in os.environ: del os.environ[k]
        if "api_key" in st.session_state:
            del st.session_state["api_key"]
        st.session_state.game_state = "start"
        st.rerun()
    st.info("""
    **Premium OpenAI Mode:**
    Using **GPT-4o** for the most accurate mind-reading experience!
    """)
    st.markdown("[Get OpenAI Key](https://platform.openai.com/api-keys)")
    
# --- HINGLISH SLOGANS & WELCOME ---
WELCOME_LINES = [
    "Swagat hai, let me read your mind! 🧠🏏",
    "IPL Expert ho? Chalo dekhte hain kitna dimaag hai! 😎",
    "Mind reading shuru karein? Taiyaar ho jao roast ke liye! 🔥",
    "Player socho, main pehchanunga. Challenge accepted? 🎯",
    "Dhoni, Kohli ya Rohit? Kiski yaad aa rahi hai? 🤔"
]

st.markdown("<h1 class='main-title'>OMNISCIENT AGENT 🧠</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline'>🔥 ANTARYAMI MODE: Dimaag Padha Jaayega, Roast Kiya Jaayega! 🏏</p>", unsafe_allow_html=True)

if st.session_state.game_state == "start":
    env_key = os.getenv("OPENROUTER_API_KEY", os.getenv("CEREBRAS_API_KEY", os.getenv("GEMINI_API_KEY", os.getenv("GROQ_API_KEY", ""))))
    
    with st.container():
        st.markdown(f"### {random.choice(WELCOME_LINES)}")
        st.write("Think of any IPL player (Past or Present) and I will identify them in just 8 questions!")
        
        if env_key:
            if env_key.startswith("gsk"): provider = "Groq (Lightning Fast)"
            elif env_key.startswith("csk"): provider = "Cerebras (Atomic Speed)"
            else: provider = "OpenAI (Premium)"
            st.success(f"✅ Active Provider: **{provider}**")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🚀 Dimaag Padho!", type="primary", use_container_width=True):
                    st.session_state.api_key = env_key
                    st.session_state.game_state = "playing"
                    get_next_question()
            with c2:
                if st.button("🔑 Chabi Badlo", use_container_width=True):
                    if os.path.exists(".env"): os.remove(".env")
                    for k in ["GEMINI_API_KEY", "CEREBRAS_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY", "SAMBANOVA_API_KEY", "OPENAI_API_KEY"]:
                        if k in os.environ: del os.environ[k]
                    if "api_key" in st.session_state: del st.session_state["api_key"]
                    st.session_state.game_state = "start"
                    st.rerun()
        else:
            st.info("Bhai pehle apni API key daalo connection banane ke liye!")
            api_key_input = st.text_input("🔑 API Key Daalo", type="password", placeholder="Groq (gsk_...), Cerebras (csk-), or OpenAI key...")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Shuru Karein?", type="primary", use_container_width=True):
                    if api_key_input:
                        st.session_state.api_key = api_key_input
                        save_key_to_env(api_key_input)
                        st.session_state.game_state = "playing"
                        get_next_question()
                    else:
                        st.error("Bhai pehle key toh do! 🔑")

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
                st.markdown(f"<div><span class='probe-label'>SAWAAL</span><br><span class='probe-count'>{st.session_state.count + 1} / 12</span></div>", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"<div style='text-align:right'><span class='probe-label'>CANDIDATES</span><br><span class='candidates-count'>{len(st.session_state.remaining_players)}</span></div>", unsafe_allow_html=True)
            
            st.progress(min(st.session_state.count / 12.0, 1.0))
            
            comment = q.get('ai_personality_comment', 'Hmm... thinking...')
            st.markdown(f"<div class='ai-bubble'>💬 {comment}</div>", unsafe_allow_html=True)
            st.subheader(q.get('question', 'Scanning neural patterns...'))
            
            c1, c2 = st.columns(2)
            c3, c4 = st.columns(2)
            
            def handle_ans(ans):
                st.session_state.undo_stack.append({
                    "remaining_players": list(st.session_state.remaining_players),
                    "history": list(st.session_state.history),
                    "count": st.session_state.count,
                    "current_q": st.session_state.current_q
                })
                st.session_state.history.append({"q": q["question"], "a": ans, "cat": q.get("cat"), "val": q.get("val")})
                
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
                # If "Maybe" or "Don't Know", we don't filter the pool at all, just proceed to next question.
                
                if len(st.session_state.remaining_players) == 0:
                    st.session_state.remaining_players = prev_pool
                    
                st.session_state.count += 1
                st.session_state.current_q = None
                st.rerun()

            with c1: 
                if st.button("✅ Yes", type="primary", use_container_width=True): handle_ans("Yes")
            with c2: 
                if st.button("❌ No", use_container_width=True): handle_ans("No")
            with c3:
                if st.button("🤷 Maybe", use_container_width=True): handle_ans("Maybe")
            with c4:
                if st.button("❓ Don't Know", use_container_width=True): handle_ans("Don't Know")
            
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
    guess_name = res.get("guess", "Unknown Player")
    confidence = res.get("confidence", "90%")
    celebration = res.get("celebration", "Bhai main toh genius hoon! 😎")
    
    with st.container():
        st.markdown("<div class='glass-card'></div>", unsafe_allow_html=True)
        
        # THE BIG REVEAL
        st.markdown("<div class='sahi-pakde'>🎯 SAHI PAKDE HAI! 🎯</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-name'>{guess_name}</div>", unsafe_allow_html=True)
        
        image_url = get_player_image_url(guess_name)
        st.markdown(f"<div style='display: flex; justify-content: center; margin-bottom: 20px;'><img src='{image_url}' style='border-radius: 50%; width: 250px; height: 250px; object-fit: cover; border: 4px solid #fc3c44; box-shadow: 0 0 20px rgba(252,60,68,0.5);'></div>", unsafe_allow_html=True)
        
        # Celebration line from AI
        st.markdown(f"<div class='ai-bubble'>🎉 {celebration}</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<span class='result-badge'>🎯 {confidence}</span>", unsafe_allow_html=True)
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
                st.session_state.remaining_players = [p for p in st.session_state.remaining_players if p["Name"] != guess_name]
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
        st.info("💡 **Possible Fixes:**\n1. Wait 10s and retry (Rate limits).\n2. Refresh the page.\n3. Check if your API Key is valid and has credits.")
        
        if st.button("🔄 Retry Neural Link", type="primary", use_container_width=True):
            st.session_state.game_state = "playing"
            st.session_state.current_q = None
            st.rerun()
            
        if st.button("🔑 Change API Key", use_container_width=True):
            if os.path.exists(".env"): os.remove(".env")
            for k in ["GEMINI_API_KEY", "CEREBRAS_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY", "SAMBANOVA_API_KEY", "OPENAI_API_KEY"]:
                if k in os.environ: del os.environ[k]
            if "api_key" in st.session_state: del st.session_state["api_key"]
            st.session_state.game_state = "start"
            st.rerun()
