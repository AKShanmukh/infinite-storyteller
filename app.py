# app.py
from openai import OpenAI
from dotenv import load_dotenv
import os
import pyttsx3
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import streamlit as st
from io import BytesIO
from datetime import datetime
import sqlite3
import hashlib
import base64



def add_bg_local(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()

    st.markdown(
        f"""
        <style>

        /* REMOVE WHITE BAR / PADDING */
        .stApp {{
            background: none;
        }}

        /* FULL BACKGROUND IMAGE */
        body {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position:40% center;
        }}

        /* DARK OVERLAY */
        body::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.55); /* adjust darkness (0.4-0.7) */
            z-index: -1;
        }}

        /* LOGIN BOX IMPROVED */
        .login-box {{
            background: rgba(0, 0, 0, 0.55); 
            padding: 25px;
            border-radius: 15px;
            backdrop-filter: blur(8px);
            color: white !important;
        }}

        /* Make text inside login box white */
        .login-box label, .login-box h1, .login-box p {{
            color: white !important;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )
def add_story_bg(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()

    st.markdown(
        f"""
        <style>

        /* RESET PREVIOUS BACKGROUND */
        .stApp {{
            background: none !important;
        }}

        body {{
            background: none !important;
        }}

        body::before {{
            content: none !important;
            background: none !important;
        }}

        /* NEW BACKGROUND */
        body {{
            background-image: url("data:image/jpg;base64,{encoded}") !important;
            background-size: cover !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
            background-position: center !important;
        }}

        /* BLACK OVERLAY */
        body::after {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.55); /* Adjust opacity (0.3 - 0.8) */
            z-index: -1;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

# ------------------- CONFIG & SETUP -------------------
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
client = OpenAI(api_key=API_KEY)
st.set_page_config(page_title="Infinite Storyteller", page_icon="📖", layout="wide")

# ------------------- DATABASE (SQLite) -------------------
DB_PATH = "users.db"

def get_connection():
    # check_same_thread False so Streamlit threads won't complain
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(email: str, password: str) -> None:
    # ensure email stored lowercase
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email.strip().lower(), hash_password(password)))
    conn.commit()
    conn.close()

def verify_user(email: str, password: str) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE email = ?", (email.strip().lower(),))
    row = c.fetchone()
    conn.close()
    if row:
        stored_hash = row[0]
        return stored_hash == hash_password(password)
    return False

# initialize DB on app start
init_db()

# ------------------- SESSION STATE DEFAULTS -------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if "page" not in st.session_state:
    # pages: "login", "signup", "home"
    st.session_state["page"] = "login"
if "story" not in st.session_state:
    st.session_state.story = ""
if "meta" not in st.session_state:
    st.session_state.meta = {"genre": None, "tone": None, "length": None, "created_at": None}
if "story_data" not in st.session_state:
    st.session_state.story_data = None

# ------------------- CUSTOM CSS FOR ALIGNMENT -------------------
st.markdown("""
<style>
.block-container {
    padding-left: 5rem !important;
    padding-right: 5rem !important;
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
}
.sidebar .sidebar-content {
    padding: 2rem 1rem;
}
</style>
""", unsafe_allow_html=True)

# ------------------- AUTH UI (login/signup handlers) -------------------
def render_login():
    add_bg_local("image/bg2.jpg")  # <--- ADD THIS
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.title("🔐 Login — Infinite Storyteller")
    st.write("Use your email and password to sign in, or create a new account.")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Login"):
            if not email or not password:
                st.error("Please enter email and password.")
            else:
                try:
                    if verify_user(email, password):
                        st.success(f"Welcome back, {email}!")
                        st.session_state.logged_in = True
                        st.session_state.user_email = email.strip().lower()
                        st.session_state.page = "home"
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
                except Exception as e:
                    st.error(f"Error during login: {e}")

    with col2:
        if st.button("Go to Sign Up"):
            st.session_state.page = "signup"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_signup():
    add_bg_local("image/bg2.jpg")  # <--- ADD THIS
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.title("✨ Create Account — Infinite Storyteller")
    st.write("Create an account using your email and a password.")

    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")

    if st.button("Create Account"):
        if not email or not password or not confirm:
            st.error("Please fill all fields.")
        elif password != confirm:
            st.error("Passwords do not match.")
        else:
            try:
                add_user(email, password)
                st.success("Account created! You can now log in.")
                st.session_state.page = "login"
                # prefill login email for convenience
                st.session_state["login_email"] = email.strip().lower()
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("Email already exists. Try logging in.")
            except Exception as e:
                st.error(f"Error creating account: {e}")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------- STORY GENERATOR (protected) -------------------
# Keep your original story generator code mostly unchanged, wrapped in auth guard
def build_check_prompt(user_prompt: str) -> str:
    return f"Is this a meaningful creative writing prompt: '{user_prompt}'? Answer only 'yes' or 'no'."

def build_generation_prompt(user_prompt: str, genre: str, tone: str, length: str, outline: bool) -> str:
    length_map = {
        "Short (1-2 paragraphs)": "short (1-2 paragraphs)",
        "Medium (3-5 paragraphs)": "medium (3-5 paragraphs)",
        "Long (6+ paragraphs)": "long (6+ paragraphs)"
    }
    outline_text = " Also produce a 3-bullet outline before the story." if outline else ""
    return (
        f"Write a creative, detailed story based on this idea: \"{user_prompt}\". "
        f"Genre: {genre}. Tone/Style: {tone}. Desired length: {length_map.get(length,'medium')}.{outline_text} "
        "Keep language clear and engaging. If producing an outline, separate outline and story sections clearly."
    )

def generate_story(client: OpenAI, full_prompt: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": full_prompt}]
    )
    return resp.choices[0].message.content.strip()

def make_story_id() -> str:
    return datetime.now().strftime("ST-%Y%m%d-%H%M%S")

def create_initial_story_data(story_text: str, genre: str, tone: str, length: str) -> dict:
    now = datetime.now().isoformat()
    return {
        "story_id": make_story_id(),
        "genre": genre,
        "tone": tone,
        "length": length,
        "created_at": now,
        "updated_at": now,
        "chapters": [
            {
                "chapter_no": 1,
                "text": story_text,
                "created_at": now
            }
        ]
    }

def append_chapter(story_data: dict, new_text: str) -> None:
    now = datetime.now().isoformat()
    chapter_no = len(story_data["chapters"]) + 1
    story_data["chapters"].append({
        "chapter_no": chapter_no,
        "text": new_text,
        "created_at": now
    })
    story_data["updated_at"] = now

def get_full_story_text(story_data: dict) -> str:
    return "\n\n".join(ch["text"] for ch in story_data["chapters"])

def render_home():
    # top bar: logged in info + logout
    add_story_bg("image/bg.jpg")

    st.title("📖 Infinite Storyteller")
    st.write("✨ Tell me what kind of story you’d love to read! Choose a genre, set the tone, and decide how long the adventure should be. ✨")

    st.markdown(f"**Logged in as:** `{st.session_state.user_email}`")
    if st.button("Logout"):
        # clear auth info but preserve story if desired (here we clear everything)
        st.session_state.clear()
        # re-initialize minimal defaults
        st.session_state["logged_in"] = False
        st.session_state["page"] = "login"
        st.rerun()

    # ------------------- UI CONTROLS (SIDEBAR) -------------------
    with st.sidebar:
        st.header("Story Settings")
        genre = st.selectbox(
            "Genre",
            ["Fantasy", "Sci-fi", "Horror", "Romance", "Adventure", "Mystery", "Mythology", "Any"],
            index=0
        )
        # ------------------- BACKGROUND MUSIC SYSTEM -------------------
        st.markdown("### 🎶 Background Music")

        # Map genre → music file
        music_files = {
            "Fantasy": "music/fairy tale.mp3",
            "Sci-fi": "music/sci-fi.mp3",
            "Horror": "music/horror.mp3",
            "Romance": "music/romance.mp3",
            "Adventure": "music/adventure.mp3",
            "Mystery": "music/mystery.mp3",
            "Mythology": "music/mythology.mp3",
            "Any": "music/any.mp3"
        }

        selected_music_file = music_files.get(genre, "music/any.mp3")

        # Minimal volume control
        volume = st.slider("Background music volume", 0.0, 1.0, 0.2)

        # Auto-play music
        if os.path.exists(selected_music_file):
            with open(selected_music_file, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
        else:
            st.warning("Music file missing for this genre!")

        tone = st.selectbox(
            "Tone / Style",
            ["Neutral", "Whimsical", "Dark", "Romantic", "Humorous", "Poetic", "Formal"],
            index=0
        )
        length = st.selectbox(
            "Length",
            ["Short (1-2 paragraphs)", "Medium (3-5 paragraphs)", "Long (6+ paragraphs)"],
            index=1
        )
        include_outline = st.checkbox("Generate short outline before story", value=True)

        # ─────────────── STORY HISTORY ───────────────
        st.markdown("---")
        st.subheader("📚 Story Search History")

        # Initialize history
        if "history" not in st.session_state:
            st.session_state.history = []

        # Save prompt when story is generated
        if st.session_state.story and st.session_state.get("prompt"):
            prompt_text = st.session_state["prompt"]
            if prompt_text not in st.session_state.history:
                st.session_state.history.insert(0, prompt_text)
                st.session_state.history = st.session_state.history[:10]

        # Display history
        if st.session_state.history:
            for i, h in enumerate(st.session_state.history):
                if st.button(h, key=f"history_{i}"):
                    st.session_state["prompt"] = h
                    st.rerun()
        else:
            st.info("No story history yet.")
    # STORY PROMPT INPUT (Main Page)
    prompt = st.text_input(
        "💡 Enter your story idea (a sentence or two):",
        value=st.session_state.get("prompt", ""),
        placeholder="e.g., A young clockmaker discovers a city of forgotten clocks..."
    )

    # update prompt into session-state
    st.session_state["prompt"] = prompt

    # ------------------- GENERATION LOGIC -------------------
    if st.button("🚀 Generate Story", key="gen_story_btn"):
        if not prompt.strip():
            st.warning("⚠️ Please enter your story idea!")
        else:
            with st.spinner("Crafting your story... please wait ✨"):
                try:
                    check_prompt = build_check_prompt(prompt)
                    check = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": check_prompt}]
                    )
                    check_text = check.choices[0].message.content.lower()
                    if "no" in check_text:
                        st.error("🤔 That doesn’t look like a real prompt. Please enter something more meaningful.")
                    else:
                        gen_prompt = build_generation_prompt(prompt, genre, tone, length, include_outline)
                        story_text = generate_story(client, gen_prompt)

                        st.session_state.story = story_text
                        st.session_state.meta = {
                            "genre": genre,
                            "tone": tone,
                            "length": length,
                            "created_at": datetime.now().isoformat()
                        }
                        st.session_state.story_data = create_initial_story_data(story_text, genre, tone, length)
                        st.success("✨ Your AI-generated story is ready and saved with metadata! ✨")
                except Exception as e:
                    st.error(f"Error generating story: {e}")

    # ------------------- DISPLAY STORY -------------------
    if st.session_state.story_data:
        sd = st.session_state.story_data
        st.subheader("📜 Your Story")
        st.markdown(
            f"**ID:** `{sd.get('story_id')}`   •   "
            f"**Genre:** {sd.get('genre')}   •   "
            f"**Tone:** {sd.get('tone')}   •   "
            f"**Length:** {sd.get('length')}"
        )
        st.markdown(f"**Created:** {sd.get('created_at')}   •   **Last updated:** {sd.get('updated_at')}")
        st.markdown("---")

        # ------------------- CHAPTERS -------------------
        st.subheader("📖 Full Story (All Chapters)")
        for ch in sd["chapters"]:
            st.markdown(f"### Chapter {ch['chapter_no']}")
            st.markdown(f"**Created:** {ch['created_at']}")
            st.write(ch["text"])
            st.markdown("---")

        # ------------------- FULL STORY READABLE BLOCK -------------------
        st.subheader("📚 Full Story (Combined)")
        full_text = get_full_story_text(sd)
        st.markdown(full_text)
        # ------------------- VOICE SELECTION -------------------
        st.subheader("🔊 Voice Options")

        engine = pyttsx3.init()
        available_voices = engine.getProperty("voices")

        voice_names = [v.name for v in available_voices]
        selected_voice = st.selectbox(
            "Choose a voice for Read Aloud:",
            voice_names,
            key="voice_choice"
        )

        # ------------------- ACTION ROW -------------------
        col1, col2, col3 = st.columns([1, 1, 1])

        # ----- READ ALOUD -----
        with col1:
            if st.button("🔊 Read the story aloud", key="read_aloud_btn"):
                try:
                    engine = pyttsx3.init()
                    engine.setProperty("rate", 120)
                    engine.setProperty("volume", 1.0)

                    # apply selected voice
                    voices = engine.getProperty("voices")
                    for v in voices:
                        if v.name == st.session_state.voice_choice:
                            engine.setProperty("voice", v.id)
                            break

                    full_text = get_full_story_text(sd)

                    audio_path = "story_audio.mp3"
                    engine.save_to_file(full_text, audio_path)
                    engine.runAndWait()

                    with open(audio_path, "rb") as audio_file:
                        st.audio(audio_file.read(), format="audio/mp3")

                except Exception as e:
                    st.error(f"Audio error: {e}")

        # ----- CONTINUE STORY -----
        with col2:
            if st.button("➕ Continue Story (append chapter)", key="continue_btn"):
                cont_prompt = (
                    "Continue the following story while maintaining characters, tone, and plot continuity.\n\n"
                    f"Genre: {sd.get('genre')}\nTone: {sd.get('tone')}\nLength preference: {sd.get('length')}\n\n"
                    f"{get_full_story_text(sd)}\n\n"
                    "Now continue the story for the next chapter (2-4 paragraphs)."
                )
                with st.spinner("Generating continuation..."):
                    try:
                        continuation = generate_story(client, cont_prompt)
                        append_chapter(sd, continuation)
                        st.session_state.story = get_full_story_text(sd)
                        st.success("✅ Continued the story! New chapter added.")
                    except Exception as e:
                        st.error(f"Error continuing story: {e}")

        # ----- SAVE STORY -----
        with col3:
            st.write("💾 Save your story below:")
            filetype = st.selectbox("Choose file format:", ["txt", "pdf"], key="save_type")
            filename = st.text_input("Enter filename (without extension):", f"MyStory_{sd.get('story_id')}", key="save_name")

            if st.button("✅ Prepare Download", key="prepare_download_btn"):
                combined = get_full_story_text(sd)

                if filetype == "txt":
                    st.download_button(
                        label="📥 Download TXT File",
                        data=combined.encode("utf-8"),
                        file_name=f"{filename}.txt",
                        mime="text/plain"
                    )

                else:  # PDF
                    try:
                        buffer = BytesIO()
                        c = canvas.Canvas(buffer, pagesize=letter)
                        obj = c.beginText(40, 750)
                        obj.setFont("Times-Roman", 12)

                        obj.textLine(f"Story ID: {sd.get('story_id')}")
                        obj.textLine(f"Genre: {sd.get('genre')}   Tone: {sd.get('tone')}   Length: {sd.get('length')}")
                        obj.textLine(f"Created: {sd.get('created_at')}   Last updated: {sd.get('updated_at')}")
                        obj.textLine("")

                        for ch in sd["chapters"]:
                            obj.textLine(f"--- Chapter {ch['chapter_no']} ---")
                            for line in ch["text"].split("\n"):
                                while len(line) > 95:
                                    obj.textLine(line[:95])
                                    line = line[95:]
                                obj.textLine(line)
                            obj.textLine("")

                        c.drawText(obj)
                        c.save()
                        buffer.seek(0)

                        st.download_button(
                            label="📥 Download PDF File",
                            data=buffer,
                            file_name=f"{filename}.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"PDF generation error: {e}")

    else:
        st.subheader("No story yet")
        st.info("Enter a story idea and press 'Generate Story'. Generated stories can be continued and saved.")

    st.markdown("---")
    st.caption("Tip: Use the sidebar to change genre, tone and length before generating.")

# ------------------- ROUTER -------------------
def router():
    # If not logged in, force login/signup pages
    page = st.session_state.get("page", "login")
    if page == "login":
        render_login()
    elif page == "signup":
        render_signup()
    elif page == "home":
        if st.session_state.get("logged_in", False):
            render_home()
        else:
            # protect the home page
            st.warning("You must be logged in to access this page.")
            st.session_state.page = "login"
            st.rerun()
    else:
        # fallback
        st.session_state.page = "login"
        render_login()

if __name__ == "__main__":
    router()
