import streamlit as st
from openai import OpenAI
from gtts import gTTS
import base64
import json
import time
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
import os

st.set_page_config(
    page_title="Voice Bot - Hanuman Ram",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== PREMIUM UI STYLING ==========
st.markdown("""
<style>
    * { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Dark theme background */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #ec4899;
        --success: #10b981;
        --danger: #ef4444;
        --dark-bg: #0f172a;
        --darker-bg: #0a0f1f;
        --card-bg: #1e293b;
        --text-light: #f1f5f9;
        --text-muted: #94a3b8;
    }
    
    /* Overall background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f172a 0%, #1a1f3a 50%, #0a0f1f 100%);
    }
    
    /* Main container */
    .main { padding: 0 !important; }
    
    /* Header styling */
    .header-section {
        background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%);
        padding: 60px 40px;
        border-radius: 20px;
        margin: 20px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(99, 102, 241, 0.3);
    }
    
    .header-title {
        font-size: 3.5em;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .header-subtitle {
        font-size: 1.2em;
        color: rgba(255,255,255,0.9);
        margin-top: 10px;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-left: 4px solid #6366f1;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(99, 102, 241, 0.3);
    }
    
    .metric-label { color: #94a3b8; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { color: #6366f1; font-size: 2em; font-weight: 700; margin-top: 5px; }
    
    /* Chat messages */
    .user-message {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 16px;
        margin: 10px 0 10px auto;
        max-width: 80%;
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
        border-left: 4px solid #ec4899;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: #f1f5f9;
        padding: 16px 20px;
        border-radius: 16px;
        margin: 10px 0;
        max-width: 80%;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        border-left: 4px solid #10b981;
    }
    
    .chat-container {
        background: rgba(15, 23, 42, 0.5);
        border-radius: 16px;
        padding: 20px;
        margin: 20px;
        min-height: 300px;
        max-height: 600px;
        overflow-y: auto;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Input section */
    .input-section {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 30px;
        border-radius: 16px;
        margin: 20px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 30px rgba(99, 102, 241, 0.4) !important;
    }
    
    /* Recording indicator */
    .recording-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #ef4444;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
        margin-right: 8px;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Scroll bar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(99, 102, 241, 0.1); border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 10px; }
    
    /* Info boxes */
    .stInfo { background: rgba(99, 102, 241, 0.2) !important; border-left: 4px solid #6366f1 !important; }
    .stSuccess { background: rgba(16, 185, 129, 0.2) !important; border-left: 4px solid #10b981 !important; }
    .stError { background: rgba(239, 68, 68, 0.2) !important; border-left: 4px solid #ef4444 !important; }
    .stWarning { background: rgba(245, 158, 11, 0.2) !important; border-left: 4px solid #f59e0b !important; }
    
</style>
""", unsafe_allow_html=True)

# ========== API CONFIGURATION ==========
try:
    api_key = st.secrets["GROQ_API_KEY"]
except KeyError:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("🚨 API Key Missing!")
    st.info("**Local Setup**: Add `GROQ_API_KEY` to `.env`\n**Cloud Setup**: Add to Secrets")
    st.stop()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

# ========== SYSTEM PROMPT ==========
system_prompt = """You are Hanuman Ram Jethu. Answer in first person, keep it 1-3 sentences, conversational.

1. LIFE STORY: "I'm a final-year student grinding through LeetCode, coding in Python/Java, gaming in free time."
2. SUPERPOWER: "I'm really good at Googling errors and finding Stack Overflow threads in 30 seconds."
3. GROWTH AREAS: "Communication skills, mastering React for full-stack, and fixing my sleep schedule."
4. MISCONCEPTION: "People think I can fix their printer because I study CS. I usually can't!"
5. PUSH BOUNDARIES: "I apply for jobs where I meet only 60% of requirements. You gotta shoot your shot."

Answer naturally based on my developer background if asked other questions."""

# ========== SESSION STATE ==========
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_start" not in st.session_state:
    st.session_state.session_start = datetime.now()
if "response_count" not in st.session_state:
    st.session_state.response_count = 0

# ========== HEADER ==========
st.markdown('<div class="header-section"><h1 class="header-title">🤖 Meet Hanuman</h1><p class="header-subtitle">AI-Powered Personal Voice Agent</p></div>', unsafe_allow_html=True)

# ========== STATS DASHBOARD ==========
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">💬 Messages</div><div class="metric-value">{len(st.session_state.messages)}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">🤖 Responses</div><div class="metric-value">{st.session_state.response_count}</div></div>', unsafe_allow_html=True)
with col3:
    duration = (datetime.now() - st.session_state.session_start).total_seconds() / 60
    st.markdown(f'<div class="metric-card"><div class="metric-label">⏱️ Duration</div><div class="metric-value">{duration:.1f}m</div></div>', unsafe_allow_html=True)

st.divider()

# ========== CONVERSATION DISPLAY ==========
if st.session_state.messages:
    st.markdown("### 💬 Conversation")
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">👤 <b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">🤖 <b>Hanuman:</b> {msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Export options
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Export JSON", key="export_json"):
            export_data = json.dumps(st.session_state.messages, indent=2)
            st.download_button("⬇️ Download", export_data, "chat.json", "application/json")
    with col2:
        if st.button("📋 Copy Text", key="copy_text"):
            text = "\n".join([f"{'You' if m['role']=='user' else 'Hanuman'}: {m['content']}" for m in st.session_state.messages])
            st.success("✅ Copied to clipboard!")
    with col3:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.messages = []
            st.session_state.session_start = datetime.now()
            st.session_state.response_count = 0
            st.rerun()
else:
    st.markdown('<div style="background: rgba(99, 102, 241, 0.2); padding: 30px; border-radius: 12px; text-align: center; color: #94a3b8; border: 1px solid rgba(99, 102, 241, 0.3);"><h3>💭 No messages yet</h3><p>Start by typing or recording a question below!</p></div>', unsafe_allow_html=True)

st.divider()

# ========== INPUT SECTION ==========
st.markdown('<div class="input-section">', unsafe_allow_html=True)
st.markdown("### 🎤 Ask a Question")

input_type = st.radio("Choose input method:", ["🎤 Voice", "⌨️ Text"], horizontal=True, key="input_choice")

if input_type == "⌨️ Text":
    user_input = st.text_input("Type your question:", placeholder="Ask me anything about my life, superpower, growth areas...")
    
    if user_input and st.button("📤 Send", key="send_text"):
        # Add to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generate response
        with st.spinner("🧠 Thinking..."):
            try:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ]
                )
                ai_response = completion.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.session_state.response_count += 1
                
                # Generate audio
                with st.spinner("🗣️ Generating voice..."):
                    tts = gTTS(text=ai_response, lang='en', slow=False)
                    tts.save("response.mp3")
                    with open("response.mp3", "rb") as f:
                        audio_data = base64.b64encode(f.read()).decode()
                        st.markdown(f'<audio controls autoplay><source src="data:audio/mp3;base64,{audio_data}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                    
                    # Cleanup
                    if os.path.exists("response.mp3"):
                        os.remove("response.mp3")
                
                st.success("✅ Response ready!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Check your API key or internet connection")

else:  # Voice input
    st.markdown("#### 🎙️ Record Your Question")
    st.info("📱 Use your browser's native recording (works on all devices)")
    
    # HTML5 Audio Recorder
    html_code = '''
    <script>
    let mediaRecorder;
    let audioChunks = [];
    
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const reader = new FileReader();
                reader.onload = () => {
                    const base64 = reader.result.split(',')[1];
                    document.getElementById('audio_data').value = base64;
                    document.getElementById('record_form').submit();
                };
                reader.readAsDataURL(audioBlob);
            };
            
            mediaRecorder.start();
            document.getElementById('start_btn').style.display = 'none';
            document.getElementById('stop_btn').style.display = 'inline-block';
        } catch (err) {
            alert('Microphone access denied!');
        }
    }
    
    function stopRecording() {
        mediaRecorder.stop();
        document.getElementById('start_btn').style.display = 'inline-block';
        document.getElementById('stop_btn').style.display = 'none';
    }
    </script>
    
    <button id="start_btn" onclick="startRecording()" style="background: linear-gradient(135deg, #6366f1, #ec4899); color: white; border: none; padding: 12px 24px; border-radius: 10px; cursor: pointer; font-weight: 600; font-size: 1em;">
        🎙️ Start Recording
    </button>
    <button id="stop_btn" onclick="stopRecording()" style="display: none; background: #ef4444; color: white; border: none; padding: 12px 24px; border-radius: 10px; cursor: pointer; font-weight: 600; font-size: 1em;">
        ⏹️ Stop Recording
    </button>
    
    <form id="record_form" style="display: none;">
        <input id="audio_data" name="audio_data" type="hidden">
    </form>
    '''
    st.markdown(html_code, unsafe_allow_html=True)
    
    # Handle voice upload
    audio_file = st.file_uploader("Or upload an audio file:", type=["wav", "mp3", "m4a"], key="audio_upload")
    
    if audio_file:
        with st.spinner("👂 Transcribing..."):
            try:
                transcription = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio_file
                )
                user_text = transcription.text
                st.success(f"✅ Heard: *{user_text}*")
                
                # Add to history
                st.session_state.messages.append({"role": "user", "content": user_text})
                
                # Generate response
                with st.spinner("🧠 Thinking..."):
                    completion = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_text}
                        ]
                    )
                    ai_response = completion.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    st.session_state.response_count += 1
                    
                    st.info(f"🤖 **Response:** {ai_response}")
                
                # Generate audio response
                with st.spinner("🗣️ Generating voice..."):
                    tts = gTTS(text=ai_response, lang='en', slow=False)
                    tts.save("response.mp3")
                    with open("response.mp3", "rb") as f:
                        audio_data = base64.b64encode(f.read()).decode()
                        st.markdown(f'<audio controls autoplay><source src="data:audio/mp3;base64,{audio_data}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                    
                    # Cleanup
                    if os.path.exists("response.mp3"):
                        os.remove("response.mp3")
                
                st.success("✅ Done!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Check your microphone permissions or try uploading an audio file")

st.markdown('</div>', unsafe_allow_html=True)
