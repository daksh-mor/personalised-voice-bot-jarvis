import streamlit as st
from openai import OpenAI
from gtts import gTTS
import base64
import os
import uuid
import tempfile
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Chat with Hanuman",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# STYLING
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

* { font-family: 'Inter', sans-serif; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #f8f9fa !important;
    border-right: 1px solid #e5e7eb;
}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
    color: #374151 !important;
}

/* Main */
.stApp { background: #ffffff; }
.stApp p, .stApp span, .stApp label { color: #374151; }

/* Buttons */
div[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, #10a37f, #0d8968);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(16, 163, 127, 0.3);
    transition: all 0.2s ease;
}
div[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
    background: linear-gradient(135deg, #0d8968, #0a6b54);
    box-shadow: 0 6px 18px rgba(16, 163, 127, 0.4);
    transform: translateY(-1px);
}

div[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: rgba(16, 163, 127, 0.1);
    color: #10a37f;
    border: 1px solid rgba(16, 163, 127, 0.3);
    border-radius: 8px;
    font-weight: 500;
}
div[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {
    background: rgba(16, 163, 127, 0.2);
}

/* Chat input */
div[data-testid="stChatInput"] textarea {
    background-color: #f3f4f6 !important;
    color: #1f2937 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 10px !important;
}
div[data-testid="stChatInput"] textarea:focus {
    border-color: #10a37f !important;
    box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1) !important;
}

/* Audio input button */
[data-testid="stAudioInput"] button:first-of-type {
    width: 56px !important;
    height: 56px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #10a37f, #0d8968) !important;
    box-shadow: 0 0 20px rgba(16, 163, 127, 0.4) !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
[data-testid="stAudioInput"] button:first-of-type:hover {
    box-shadow: 0 0 32px rgba(16, 163, 127, 0.6) !important;
    transform: scale(1.06) !important;
}

/* Title */
h2 {
    background: linear-gradient(90deg, #10a37f, #16b896);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #f3f4f6; }
::-webkit-scrollbar-thumb { background: #10a37f; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# API
try:
    api_key = st.secrets["GROQ_API_KEY"]
except KeyError:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ API Key Missing!")
    st.stop()

client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)

system_prompt = """You are Hanuman Ram Jethu. Answer in first person, 1-3 sentences, conversational.
- Life: Final-year student grinding LeetCode, Python/Java coding, gaming.
- Superpower: Finding Stack Overflow solutions in 30 seconds.
- Growth: Communication skills, React mastery, sleep schedule.
- Misconception: People think I fix printers. I don't!
- Boundaries: Apply for jobs where I meet only 60% requirements."""

# SESSION STATE
if "conversations" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.conversations = {
        first_id: {"title": "New Chat", "messages": []}
    }
    st.session_state.current_conv_id = first_id

if "mode" not in st.session_state:
    st.session_state.mode = "chat"

if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None

if "autoplay_audio_path" not in st.session_state:
    st.session_state.autoplay_audio_path = None

# AUTOPLAY HELPER
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    st.markdown(
        f'<audio autoplay style="width:100%; margin-top:8px;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>',
        unsafe_allow_html=True,
    )

# SIDEBAR
with st.sidebar:
    st.markdown("## 🤖 Hanuman")
    
    if st.button("＋ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.conversations[new_id] = {"title": "New Chat", "messages": []}
        st.session_state.current_conv_id = new_id
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Recent Chats**")
    
    for conv_id in reversed(list(st.session_state.conversations.keys())):
        conv = st.session_state.conversations[conv_id]
        is_active = conv_id == st.session_state.current_conv_id
        if st.button(
            conv["title"],
            key=f"conv_{conv_id}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.current_conv_id = conv_id
            st.rerun()

# MAIN AREA
current_conv = st.session_state.conversations[st.session_state.current_conv_id]

col_title, col_toggle = st.columns([5, 1])
with col_title:
    st.markdown("## 🤖 Chat with Hanuman")
with col_toggle:
    voice_on = st.toggle("🎙️ Voice", value=(st.session_state.mode == "voice"))
    st.session_state.mode = "voice" if voice_on else "chat"

# MESSAGE HISTORY
for msg in current_conv["messages"]:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.write(msg["content"])
            audio_path = msg.get("audio_path")
            if audio_path and os.path.exists(audio_path):
                if audio_path == st.session_state.autoplay_audio_path:
                    autoplay_audio(audio_path)
                    st.session_state.autoplay_audio_path = None
                else:
                    st.audio(audio_path)

# PROCESS & RESPOND
def process_and_respond(user_text: str):
    user_text = user_text.strip()
    if not user_text:
        return
    
    # Auto-title from first message
    if not current_conv["messages"]:
        current_conv["title"] = user_text[:35] + "…" if len(user_text) > 35 else user_text
    
    current_conv["messages"].append({"role": "user", "content": user_text})
    
    with st.spinner("Thinking…"):
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text}]
        )
        ai_text = completion.choices[0].message.content
    
    # TTS
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        speech_path = f.name
    
    with st.spinner("Generating voice…"):
        tts = gTTS(text=ai_text, lang='en')
        tts.save(speech_path)
    
    current_conv["messages"].append(
        {"role": "assistant", "content": ai_text, "audio_path": speech_path}
    )
    st.session_state.autoplay_audio_path = speech_path
    st.rerun()

# INPUT AREA
if st.session_state.mode == "chat":
    user_input = st.chat_input("Ask me anything…")
    if user_input:
        process_and_respond(user_input)
else:
    audio = st.audio_input("🎙️ Tap to Record")
    if audio:
        try:
            audio_bytes = audio.getbuffer().tobytes()
            
            if len(audio_bytes) < 5000:
                st.warning("Recording too short — please speak for at least 2 seconds.")
            else:
                audio_hash = hash(audio_bytes)
                
                if audio_hash != st.session_state.last_audio_hash:
                    st.session_state.last_audio_hash = audio_hash
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                        f.write(audio_bytes)
                        tmp_path = f.name
                    
                    with st.spinner("Transcribing…"):
                        result = client.audio.transcriptions.create(
                            model="whisper-large-v3",
                            file=open(tmp_path, "rb"),
                        )
                    
                    user_text = result.text.strip()
                    if user_text:
                        process_and_respond(user_text)
                    else:
                        st.warning("Could not hear anything — please try again.")
        except Exception as e:
            st.error(f"Voice error: {e}")
