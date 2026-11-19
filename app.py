import json
import random
from datetime import datetime
from pathlib import Path

import streamlit as st


# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="Mind Reader",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Save files next to app.py, no matter where you launch Streamlit from
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "mindreader_data.json"
LEGACY_FILE = BASE_DIR / "highscores.json"


# ============================================================
# DIFFICULTY LEVELS
# ============================================================

LEVELS = {
    "Easy": {"attempts": 10, "max": 50, "mult": 1, "icon": "🟢"},
    "Medium": {"attempts": 7, "max": 100, "mult": 2, "icon": "🟡"},
    "Hard": {"attempts": 9, "max": 500, "mult": 4, "icon": "🔴"},
    "Insane": {"attempts": 10, "max": 1000, "mult": 7, "icon": "💀"},
}


# ============================================================
# ACHIEVEMENTS
# ============================================================

ACHIEVEMENTS = {
    "first_win": ("🌱 First Blood", "Win your first game"),
    "psychic": ("🔮 Psychic", "Win in 3 attempts or fewer"),
    "lucky": ("🍀 Lucky Strike", "Guess it on your very first try"),
    "streak3": ("🔥 On Fire", "Win 3 games in a row"),
    "hard_win": ("💪 Hard Hitter", "Win on Hard or Insane"),
    "no_hint": ("🧘 Pure Mind", "Win on Medium+ without using a hint"),
    "veteran": ("🎖️ Veteran", "Play 10 games"),
}


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: radial-gradient(
        circle at 20% 10%,
        #2b1055 0%,
        #12082b 45%,
        #07030f 100%
    );
    color: #F5F0FF;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding-top: 2rem;
    max-width: 780px;
}

/* General text */

.stApp p,
.stApp li,
.stApp label,
.stApp .stMarkdown,
[data-testid="stMarkdownContainer"] p,
[data-testid="stCaptionContainer"] {
    color: #F0EAFF;
}

/* Headings */

h1, h2, h3, h4 {
    color: #FFFFFF !important;
    font-weight: 800 !important;
}

/* Hero section */

.hero {
    text-align: center;
    padding: 1.2rem 0 0.4rem 0;
}

.hero h1 {
    font-size: 3.1rem;
    font-weight: 800;
    margin: 0;
    background: linear-gradient(90deg, #ff6ec7, #8e7cff, #4de1ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    color: #E0D7FF !important;
    margin-top: 0.3rem;
    font-size: 1.05rem;
}

/* Cards */

.card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 18px;
    padding: 1.1rem 1.3rem;
    margin: 0.7rem 0;
    backdrop-filter: blur(8px);
    color: #FFFFFF;
}

/* Pills */

.pill {
    display: inline-block;
    padding: 0.25rem 0.8rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 0 0.35rem 0.35rem 0;
    color: #FFFFFF;
    background: rgba(142,124,255,0.30);
    border: 1px solid rgba(142,124,255,0.7);
}

/* Guess history */

.chip {
    display: inline-block;
    padding: 0.3rem 0.75rem;
    border-radius: 12px;
    margin: 0.2rem 0.25rem;
    font-weight: 600;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.20);
}

.chip.up { border-color: #4de1ff; color: #4de1ff; }
.chip.down { border-color: #ff6ec7; color: #ff6ec7; }
.chip.win { border-color: #5dffa0; color: #5dffa0; }

/* Feedback messages */

.feedback {
    text-align: center;
    font-size: 1.5rem;
    font-weight: 800;
    padding: 0.9rem;
    border-radius: 16px;
    margin: 0.6rem 0;
    color: #FFFFFF;
}

.fb-up { background: rgba(77,225,255,0.18); border: 1px solid #4de1ff; }
.fb-down { background: rgba(255,110,199,0.18); border: 1px solid #ff6ec7; }
.fb-lose { background: rgba(255,90,90,0.18); border: 1px solid #ff5a5a; }

.temp {
    text-align: center;
    font-size: 1.05rem;
    color: #F0E8FF !important;
    margin-bottom: 0.4rem;
}

/* Number range bar */

.range-track {
    position: relative;
    height: 14px;
    border-radius: 99px;
    background: rgba(255,255,255,0.15);
    overflow: hidden;
    margin: 0.5rem 0 0.2rem 0;
}

.range-fill {
    position: absolute;
    top: 0;
    bottom: 0;
    border-radius: 99px;
    background: linear-gradient(90deg, #8e7cff, #4de1ff);
    box-shadow: 0 0 14px rgba(77,225,255,0.7);
    transition: all 0.4s ease;
}

.range-labels {
    display: flex;
    justify-content: space-between;
    color: #E0D7FF;
    font-size: 0.85rem;
}

/* Achievements */

.badge {
    border-radius: 14px;
    padding: 0.7rem 0.9rem;
    margin: 0.35rem 0;
    border: 1px solid rgba(255,255,255,0.20);
    color: #FFFFFF;
}

.badge.on {
    background: rgba(93,255,160,0.15);
    border-color: #5dffa0;
}

.badge.off {
    background: rgba(255,255,255,0.07);
    opacity: 0.85;
}

/* Buttons (full width, so no use_container_width needed) */

div.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    width: 100%;
    border-radius: 14px;
    border: none;
    padding: 0.65rem 1rem;
    font-weight: 700;
    color: #FFFFFF !important;
    background: linear-gradient(90deg, #8e7cff, #ff6ec7);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

div.stButton > button p,
div[data-testid="stFormSubmitButton"] > button p {
    color: #FFFFFF !important;
}

div.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(142,124,255,0.45);
    color: #FFFFFF !important;
}

/* Input fields */

.stTextInput input,
.stNumberInput input {
    background-color: #FFFFFF !important;
    color: #24133F !important;
    border: 2px solid #A78BFA !important;
    border-radius: 10px !important;
    font-weight: 600;
}

/* Dropdown */

.stSelectbox div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
    color: #24133F !important;
}

.stSelectbox div[data-baseweb="select"] * {
    color: #24133F !important;
}

[role="listbox"] {
    background-color: #FFFFFF !important;
}

[role="option"],
[role="option"] * {
    color: #24133F !important;
}

/* Tabs */

button[data-baseweb="tab"] p {
    color: #E8DEFF !important;
    font-weight: 600;
}

button[data-baseweb="tab"][aria-selected="true"] p {
    color: #4de1ff !important;
}

/* Metrics */

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 16px;
    padding: 0.8rem 1rem;
}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: #FFFFFF !important;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {
    color: #E0D7FF !important;
}

/* Sidebar */

[data-testid="stSidebar"] {
    background-color: #180D30 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #F5F0FF !important;
}

/* Footer */

.footer {
    text-align: center;
    color: #D0C4F5;
    font-size: 0.85rem;
    margin-top: 2rem;
}

/* ALL ALERTS (info, hint, error...) - dark background, white text */

[data-testid="stAlert"] {
    background-color: #2A1B55 !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 12px !important;
}

[data-testid="stAlert"] * {
    color: #FFFFFF !important;
}

[data-testid="stAlert"][kind="success"] {
    background-color: #123D32 !important;
    border: 1px solid #39D98A !important;
}

[data-testid="stAlert"][kind="warning"] {
    background-color: #493514 !important;
}

[data-testid="stAlert"][kind="error"] {
    background-color: #501D2A !important;
}

/* Toast pop-ups (achievements) */

[data-testid="stToast"] {
    background-color: #2A1B55 !important;
    border: 1px solid #8e7cff !important;
}

[data-testid="stToast"] * {
    color: #FFFFFF !important;
}

/* Expander (Danger Zone) */

[data-testid="stExpander"] {
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] summary p {
    color: #FFFFFF !important;
}

/* WINNING PANEL */

.win-panel {
    display: block;
    width: 100%;
    box-sizing: border-box;
    text-align: center;
    padding: 28px 18px;
    margin: 20px 0;
    border-radius: 22px;
    background: linear-gradient(135deg, #064e3b, #065f46, #047857);
    border: 2px solid #5dffa0;
    box-shadow: 0 0 25px rgba(93,255,160,0.30);
    color: #ffffff !important;
}

.win-panel h1 {
    color: #ffffff !important;
    font-size: 2.3rem !important;
    margin: 8px 0 15px 0;
    padding: 0;
    overflow-wrap: anywhere;
}

.win-panel p {
    color: #ffffff !important;
    font-size: 1.05rem;
    font-weight: 600;
    margin: 10px 0;
    overflow-wrap: anywhere;
}

.win-score {
    font-size: 2rem;
    font-weight: 800;
    color: #a7f3d0 !important;
    margin: 12px 0;
}

.win-record {
    display: block;
    background: rgba(255,255,255,0.15);
    padding: 12px;
    border-radius: 12px;
    margin-top: 15px;
    color: #ffffff !important;
    font-weight: 700;
}

/* Mobile responsiveness */

@media (max-width: 600px) {
    .hero h1 { font-size: 2.2rem; }
    .win-panel h1 { font-size: 1.8rem !important; }
    .win-score { font-size: 1.6rem; }
    .win-panel { padding: 22px 12px; }
}

</style>
""",
    unsafe_allow_html=True,
)


def render_html(markup):
    """Show an HTML snippet.

    Streamlit runs HTML through a Markdown parser first, and Markdown turns
    any indented line that follows a blank line into a code block (you would
    see raw <div> tags on the page). Flattening the snippet to one line
    avoids that.
    """
    flat = " ".join(line.strip() for line in markup.splitlines() if line.strip())
    st.markdown(flat, unsafe_allow_html=True)


# ============================================================
# DATA PERSISTENCE
# ============================================================

def default_data():
    return {
        "best": {name: None for name in LEVELS},
        "leaderboard": [],
        "stats": {
            "played": 0,
            "wins": 0,
            "streak": 0,
            "best_streak": 0,
            "total_points": 0,
        },
        "achievements": [],
    }


def load_data():
    data = default_data()

    if DATA_FILE.exists():
        try:
            saved = json.loads(DATA_FILE.read_text(encoding="utf-8"))

            if isinstance(saved, dict):
                if isinstance(saved.get("best"), dict):
                    data["best"].update(saved["best"])

                if isinstance(saved.get("leaderboard"), list):
                    data["leaderboard"] = saved["leaderboard"]

                if isinstance(saved.get("stats"), dict):
                    data["stats"].update(saved["stats"])

                if isinstance(saved.get("achievements"), list):
                    data["achievements"] = saved["achievements"]

        except (json.JSONDecodeError, OSError):
            pass

    elif LEGACY_FILE.exists():
        # Import best scores from the very first version of the game
        try:
            old = json.loads(LEGACY_FILE.read_text(encoding="utf-8"))

            if isinstance(old, dict):
                if "Easy" in old:
                    for key in ("Easy", "Medium", "Hard"):
                        data["best"][key] = old.get(key)
                else:
                    data["best"]["Easy"] = old.get("1")
                    data["best"]["Medium"] = old.get("2")
                    data["best"]["Hard"] = old.get("3")

        except (json.JSONDecodeError, OSError):
            pass

    return data


def save_data():
    try:
        DATA_FILE.write_text(
            json.dumps(st.session_state.data, indent=2),
            encoding="utf-8",
        )
    except OSError:
        st.error("Unable to save game data.")


# ============================================================
# SESSION STATE
# ============================================================

def init_state():
    defaults = {
        "data": load_data(),
        "active": False,
        "game_over": False,
        "won": False,
        "attempts": 0,
        "history": [],
        "feedback": None,
        "secret": None,
        "current_level": "Easy",
        "low": 1,
        "high": 1,
        "hint_used": False,
        "hint_text": "",
        "points": 0,
        "new_record": False,
        "celebrate": False,
        "new_badges": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()

S = st.session_state


# ============================================================
# GAME LOGIC
# ============================================================

def start_game(level):
    cfg = LEVELS[level]

    S.secret = random.randint(1, cfg["max"])
    S.current_level = level

    S.active = True
    S.game_over = False
    S.won = False

    S.attempts = 0
    S.history = []
    S.feedback = None

    S.low = 1
    S.high = cfg["max"]

    S.hint_used = False
    S.hint_text = ""

    S.points = 0
    S.new_record = False
    S.celebrate = False
    S.new_badges = []


def temperature(guess):
    cfg = LEVELS[S.current_level]
    ratio = abs(guess - S.secret) / cfg["max"]

    if ratio <= 0.02:
        return "🔥 Burning hot!"
    if ratio <= 0.05:
        return "🌶️ Hot"
    if ratio <= 0.12:
        return "☀️ Warm"
    if ratio <= 0.3:
        return "🌤️ Cool"
    return "❄️ Freezing cold"


def check_achievements(attempts):
    d = S.data
    stats = d["stats"]
    cfg = LEVELS[S.current_level]
    unlocked = []

    def grant(key):
        if key not in d["achievements"]:
            d["achievements"].append(key)
            unlocked.append(key)

    if S.won:
        grant("first_win")

        if attempts <= 3:
            grant("psychic")

        if attempts == 1:
            grant("lucky")

        if stats["streak"] >= 3:
            grant("streak3")

        if S.current_level in ("Hard", "Insane"):
            grant("hard_win")

        if cfg["mult"] >= 2 and not S.hint_used:
            grant("no_hint")

    if stats["played"] >= 10:
        grant("veteran")

    return unlocked


def finish_game(won):
    d = S.data
    stats = d["stats"]
    cfg = LEVELS[S.current_level]

    S.game_over = True
    S.won = won

    stats["played"] += 1

    if won:
        left = cfg["attempts"] - S.attempts
        points = (left + 1) * cfg["mult"] * 10

        if S.hint_used:
            points = int(points * 0.75)

        S.points = points

        stats["wins"] += 1
        stats["streak"] += 1
        stats["best_streak"] = max(stats["best_streak"], stats["streak"])
        stats["total_points"] += points

        best = d["best"].get(S.current_level)

        if best is None or S.attempts < best:
            d["best"][S.current_level] = S.attempts
            S.new_record = True
            S.celebrate = True

        player_name = st.session_state.get("player_name", "Player") or "Player"

        d["leaderboard"].append(
            {
                "player": player_name,
                "level": S.current_level,
                "attempts": S.attempts,
                "points": points,
                "date": datetime.now().strftime("%d %b %Y"),
            }
        )

        d["leaderboard"] = sorted(
            d["leaderboard"],
            key=lambda entry: entry["points"],
            reverse=True,
        )[:10]

    else:
        stats["streak"] = 0
        S.points = 0

    S.new_badges = check_achievements(S.attempts)

    save_data()


def process_guess(guess):
    cfg = LEVELS[S.current_level]

    S.attempts += 1
    S.history.append(guess)
    S.feedback = None

    if guess == S.secret:
        S.feedback = ("win", "🎉 You read my mind!", "")
        finish_game(True)
        return

    if guess < S.secret:
        S.low = max(S.low, guess + 1)
        S.feedback = ("up", "⬆️ Higher!", temperature(guess))
    else:
        S.high = min(S.high, guess - 1)
        S.feedback = ("down", "⬇️ Lower!", temperature(guess))

    if S.attempts >= cfg["attempts"]:
        S.feedback = ("lose", f"❌ Game over! It was {S.secret}", "")
        finish_game(False)


def use_hint():
    s = S.secret
    parity = "even" if s % 2 == 0 else "odd"
    div3 = "is" if s % 3 == 0 else "is not"

    S.hint_used = True
    S.hint_text = (
        f"💡 The number is **{parity}** and **{div3}** divisible by 3."
    )


def reset_all_data():
    S.data = default_data()
    save_data()


# ============================================================
# UI HELPERS
# ============================================================

def range_bar(low, high, max_number):
    left = (low - 1) / max_number * 100
    width = max((high - low + 1) / max_number * 100, 1.5)

    render_html(
        f"""
        <div class="card">
            <div style="font-weight:600; color:#FFFFFF;">
                🎯 The number is between
                <span style="color:#4de1ff">{low}</span>
                and
                <span style="color:#ff6ec7">{high}</span>
            </div>
            <div class="range-track">
                <div class="range-fill" style="left:{left}%; width:{width}%;"></div>
            </div>
            <div class="range-labels">
                <span>1</span>
                <span>{max_number}</span>
            </div>
        </div>
        """
    )


def history_chips():
    if not S.history:
        return

    chips = []

    for guess in S.history:
        if guess == S.secret and S.game_over and S.won:
            chips.append(f'<span class="chip win">{guess} ✓</span>')
        elif guess < S.secret:
            chips.append(f'<span class="chip up">{guess} ⬆️</span>')
        else:
            chips.append(f'<span class="chip down">{guess} ⬇️</span>')

    render_html(
        '<div class="card"><b>🕘 Your guesses</b><br>'
        + "".join(chips)
        + "</div>"
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.header("👤 Player")

    st.text_input(
        "Your name",
        value="Player",
        key="player_name",
        max_chars=16,
    )

    st.caption("Your name appears on the leaderboard when you win.")

    st.divider()

    st.metric("Total points", S.data["stats"]["total_points"])
    st.metric("Current streak", f'{S.data["stats"]["streak"]} 🔥')


# ============================================================
# HEADER
# ============================================================

render_html(
    """
    <div class="hero">
        <h1>🧠 Mind Reader</h1>
        <p>Can you read my mind? Pick a number, beat the odds, climb the leaderboard.</p>
    </div>
    """
)


# ============================================================
# TABS
# ============================================================

tab_play, tab_board, tab_stats, tab_help = st.tabs(
    ["🎮 Play", "🏆 Leaderboard", "📊 Stats & Badges", "❓ How to play"]
)


# ============================================================
# PLAY TAB
# ============================================================

with tab_play:

    # --------------------------------------------------------
    # START SCREEN
    # --------------------------------------------------------

    if not S.active:

        level = st.selectbox(
            "Choose your difficulty",
            list(LEVELS.keys()),
            format_func=lambda name: f"{LEVELS[name]['icon']} {name}",
        )

        cfg = LEVELS[level]
        best = S.data["best"].get(level)
        best_text = best if best is not None else "—"

        render_html(
            f"""
            <div class="card">
                <span class="pill">Range 1–{cfg['max']}</span>
                <span class="pill">{cfg['attempts']} attempts</span>
                <span class="pill">Score ×{cfg['mult']}</span>
                <span class="pill">Best: {best_text}</span>
            </div>
            """
        )

        if st.button("🚀 Start Game"):
            start_game(level)
            st.rerun()

    # --------------------------------------------------------
    # ACTIVE GAME
    # --------------------------------------------------------

    else:

        cfg = LEVELS[S.current_level]
        attempts_left = cfg["attempts"] - S.attempts

        render_html(
            f"""
            <div class="card">
                <span class="pill">{cfg['icon']} {S.current_level}</span>
                <span class="pill">Range 1–{cfg['max']}</span>
                <span class="pill">Attempts left: {attempts_left}</span>
                <span class="pill">Score ×{cfg['mult']}</span>
            </div>
            """
        )

        st.progress(min(S.attempts / cfg["attempts"], 1.0))

        # Feedback banner (the win message has its own panel below)

        if S.feedback and not (S.game_over and S.won):
            kind, message, temp = S.feedback

            render_html(f'<div class="feedback fb-{kind}">{message}</div>')

            if temp:
                render_html(f'<div class="temp">{temp}</div>')

        # Guess input

        if not S.game_over:

            range_bar(S.low, S.high, cfg["max"])

            with st.form("guess_form", clear_on_submit=True):

                guess = st.number_input(
                    f"Enter a number between 1 and {cfg['max']}",
                    min_value=1,
                    max_value=cfg["max"],
                    value=max(1, (S.low + S.high) // 2),
                    step=1,
                )

                submitted = st.form_submit_button("🔮 Submit Guess")

            if submitted:
                value = int(guess)

                if value in S.history:
                    # Don't waste an attempt on a repeated number
                    st.toast(
                        f"You already tried {value}. Pick a different number.",
                        icon="⚠️",
                    )
                else:
                    process_guess(value)
                    st.rerun()

            col1, col2 = st.columns(2)

            with col1:
                if st.button("💡 Use hint (−25% points)", disabled=S.hint_used):
                    use_hint()
                    st.rerun()

            with col2:
                if st.button("🏳️ Give up"):
                    S.attempts = cfg["attempts"]
                    S.feedback = ("lose", f"🏳️ You gave up! It was {S.secret}", "")
                    finish_game(False)
                    st.rerun()

            if S.hint_text:
                st.info(S.hint_text)

        # Guess history

        history_chips()

        # Game over / winning screen

        if S.game_over:

            if S.won:

                record_html = (
                    '<div class="win-record">🏆 NEW PERSONAL BEST!</div>'
                    if S.new_record
                    else ""
                )

                render_html(
                    f"""
                    <div class="win-panel">
                        <div style="font-size:55px;">🏆🎉🧠</div>
                        <h1>CONGRATULATIONS!</h1>
                        <p>You successfully read my mind!</p>
                        <p>You guessed the correct number in {S.attempts} attempts.</p>
                        <div class="win-score">⭐ {S.points} POINTS</div>
                        <p>Difficulty: {S.current_level}</p>
                        <p>Secret Number: {S.secret}</p>
                        {record_html}
                    </div>
                    """
                )

                if S.celebrate:
                    st.balloons()
                    S.celebrate = False

            else:
                st.error(f"❌ Game Over! The correct number was {S.secret}")

            # Achievement notifications

            for badge in S.new_badges:
                title, desc = ACHIEVEMENTS[badge]
                st.toast(f"Achievement unlocked: {title}", icon="🏅")

            S.new_badges = []

            st.divider()

            if st.button("🔄 Play Again"):
                S.active = False
                st.rerun()


# ============================================================
# LEADERBOARD TAB
# ============================================================

with tab_board:

    st.subheader("🏆 Top 10 Scores")

    board = S.data["leaderboard"]

    if not board:
        st.info("No scores yet. Win a game to claim the first spot!")

    else:
        medals = ["🥇", "🥈", "🥉"]
        widths = [0.7, 1.5, 1, 1, 1, 1.2]

        header = st.columns(widths)

        for col, title in zip(
            header, ["Rank", "Player", "Level", "Attempts", "Points", "Date"]
        ):
            col.markdown(f"**{title}**")

        for i, entry in enumerate(board):

            with st.container(border=True):

                cols = st.columns(widths)

                rank = medals[i] if i < 3 else f"#{i + 1}"

                cols[0].write(rank)
                cols[1].write(entry.get("player", "Player"))
                cols[2].write(entry.get("level", ""))
                cols[3].write(entry.get("attempts", ""))
                cols[4].write(entry.get("points", ""))
                cols[5].write(entry.get("date", ""))

    st.subheader("⭐ Personal Bests")

    cols = st.columns(len(LEVELS))

    for col, (name, cfg) in zip(cols, LEVELS.items()):
        best = S.data["best"].get(name)

        col.metric(
            f"{cfg['icon']} {name}",
            f"{best} tries" if best is not None else "—",
        )


# ============================================================
# STATS AND BADGES TAB
# ============================================================

with tab_stats:

    stats = S.data["stats"]

    win_rate = stats["wins"] / stats["played"] * 100 if stats["played"] else 0

    c1, c2, c3 = st.columns(3)

    c1.metric("Games played", stats["played"])
    c2.metric("Win rate", f"{win_rate:.0f}%")
    c3.metric("Total points", stats["total_points"])

    c4, c5 = st.columns(2)

    c4.metric("Current streak", stats["streak"])
    c5.metric("Best streak", stats["best_streak"])

    st.subheader("🏅 Achievements")

    for key, (title, desc) in ACHIEVEMENTS.items():

        unlocked = key in S.data["achievements"]
        state = "on" if unlocked else "off"
        mark = "✅" if unlocked else "🔒"

        render_html(
            f"""
            <div class="badge {state}">
                <b>{title}</b> {mark}
                <br>
                <span style="color:#E0D7FF">{desc}</span>
            </div>
            """
        )

    with st.expander("⚠️ Danger Zone"):

        confirm = st.checkbox(
            "I understand this deletes all my scores and stats"
        )

        if st.button("Reset all data", disabled=not confirm):
            reset_all_data()
            st.rerun()


# ============================================================
# HELP TAB
# ============================================================

with tab_help:

    st.markdown(
        """
### How to play

1. Pick a difficulty and press **Start Game**.
2. I'm thinking of a secret number. Guess it before your attempts run out.
3. After each guess, you get **Higher / Lower** feedback.
4. The temperature reading tells you how close you are.
5. The range bar shows where the number can be.
6. Win faster for more points.
7. Harder levels multiply your score.
8. Stuck? Use the **Hint** (costs 25% of your points).

### Pro tip

Always guess the middle of the remaining range.
This is called **Binary Search**, and it finds the number in the fewest guesses.
"""
    )


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="footer">Made with ❤️ using Python and Streamlit</div>
    """
)
