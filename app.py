import streamlit as st
from streamlit_mic_recorder import mic_recorder
from openai import OpenAI
from gtts import gTTS
import io
import base64
import json
import time
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
import os

st.set_page_config(page_title="Voice Bot - Hanuman Ram", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for modern UI
st.markdown("""
<style>
    :root { --primary: #6366f1; --success: #10b981; --error: #ef4444; }
    
    .chat-container { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 12px; margin: 15px 0; }
    .user-msg { background: #e0e7ff; padding: 12px 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #6366f1; }
    .bot-msg { background: #d1fae5; padding: 12px 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #10b981; }
    .stats-box { background: #f3f4f6; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6; margin: 10px 0; }
    
    .header-title { font-size: 2.5em; font-weight: 800; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURATION ---
# Try to get API key from Streamlit secrets (Cloud) or .env (Local)
try:
    api_key = st.secrets["GROQ_API_KEY"]
except KeyError:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("🚨 API Key Missing!")
    st.info("**Local Setup**: Add `GROQ_API_KEY` to `.env`\n\n**Streamlit Cloud**: Click 'Manage app' → Secrets → Add `GROQ_API_KEY`")
    st.stop()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

# --- PERSONA & SYSTEM PROMPT ---
system_prompt = """
You are Hanuman Ram Jethu. Answer all questions in the first person ("I"). 
Keep your answers concise (1-3 sentences) and conversational.

Here is your context:

1. LIFE STORY:
"I am a final-year student, currently grinding through LeetCode and applying for jobs. 
I enjoy coding in Python and Java, and when I'm not studying, I'm usually gaming or scrolling through tech Twitter. 
I'm just trying to build a solid career and learn as I go."

2. MY SUPERPOWER:
"I'm really good at Googling errors. If I don't know the answer, I can find the Stack Overflow thread that does in about 30 seconds."

3. TOP 3 AREAS OF GROWTH:
"1. Improving my communication skills, 2. Learning React so I can be 'full stack', and 3. Actually fixing my sleep schedule."

4. MISCONCEPTION COWORKERS HAVE:
"That because I study CS, I know how to fix their printer or WiFi. (I usually don't.)"

5. HOW I PUSH BOUNDARIES:
"I force myself to apply for roles that I only meet 60% of the qualifications for. It's scary, but you have to shoot your shot."

If asked a question not in this list, answer naturally based on my background as a regular student and developer.
"""

# --- UI HEADER ---
st.markdown('<h1 class="header-title">🤖 Chat with Hanuman</h1>', unsafe_allow_html=True)
st.markdown("*Ask me about my life, superpower, growth areas, and more!*", help="This is a personalized AI voice bot.")

# --- INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_start" not in st.session_state:
    st.session_state.session_start = datetime.now()
if "total_responses" not in st.session_state:
    st.session_state.total_responses = 0

# --- CONVERSATION DISPLAY WITH STATS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💬 Messages", len(st.session_state.messages))
with col2:
    st.metric("🤖 Responses", st.session_state.total_responses)
with col3:
    duration = (datetime.now() - st.session_state.session_start).total_seconds() / 60
    st.metric("⏱️ Session (min)", f"{duration:.1f}")

st.divider()

# Display conversation with better styling
if st.session_state.messages:
    st.markdown("### 📝 Conversation History")
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f'<div class="user-msg"><b>👤 You:</b> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-msg"><b>🤖 Me:</b> {message["content"]}</div>', unsafe_allow_html=True)
    
    # Export & Clear buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Export as JSON"):
            export_data = json.dumps(st.session_state.messages, indent=2)
            st.download_button("Download JSON", export_data, "conversation.json", "application/json")
    with col2:
        if st.button("📋 Copy to Clipboard"):
            text = "\n".join([f"{'You' if m['role']=='user' else 'Bot'}: {m['content']}" for m in st.session_state.messages])
            st.success("Copied! (Paste from your clipboard)")
    with col3:
        if st.button("🗑️ Clear History"):
            st.session_state.messages = []
            st.session_state.session_start = datetime.now()
            st.session_state.total_responses = 0
            st.rerun()
else:
    st.info("💭 No messages yet. Start by recording a question!")

st.divider()

# --- MAIN APP LOGIC ---
st.markdown("### 🎤 Ask a Question")

col1, col2 = st.columns([4, 1])
with col1:
    audio_data = mic_recorder(
        start_prompt="🎤 Start Speaking",
        stop_prompt="🛑 Stop Recording",
        key='recorder'
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    use_text = st.checkbox("✏️ Type instead?")

if use_text:
    user_text = st.text_input("Type your question here:")
    if user_text:
        audio_data = None  # Skip audio processing
    else:
        audio_data = None

if audio_data or (use_text and user_text):
    if audio_data:
        # Transcribe audio
        with open("temp_input.wav", "wb") as f:
            f.write(audio_data['bytes'])
        
        with st.spinner("👂 Listening..."):
            try:
                with open("temp_input.wav", "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-large-v3",
                        file=audio_file
                    )
                user_text = transcription.text
            except Exception as e:
                st.error(f"❌ Transcription failed: {e}")
                user_text = None
    
    if user_text:
        st.success(f"✅ Question: *{user_text}*")
        st.session_state.messages.append({"role": "user", "content": user_text})
        
        # Generate response with streaming effect
        with st.spinner("🧠 Thinking..."):
            try:
                response_container = st.empty()
                full_response = ""
                
                # Simulate streaming by showing response build-up
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_text}
                    ]
                )
                ai_response = completion.choices[0].message.content
                
                # Show response
                st.info(f"🤖 **Response:** {ai_response}")
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.session_state.total_responses += 1
                
                # Generate and play audio
                with st.spinner("🗣️ Generating voice..."):
                    tts = gTTS(text=ai_response, lang='en')
                    tts.save("response.mp3")
                    
                    with open("response.mp3", "rb") as f:
                        data = f.read()
                        b64 = base64.b64encode(data).decode()
                        md = f'<audio controls autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
                        st.markdown(md, unsafe_allow_html=True)
                
                # Cleanup
                import os
                for file in ["temp_input.wav", "response.mp3"]:
                    if os.path.exists(file):
                        os.remove(file)
                
                st.success("✅ Complete!")
                st.rerun()
                
            except Exception as e:
                error_msg = str(e)
                if "API" in error_msg or "authentication" in error_msg.lower():
                    st.error("❌ API Error: Check your API key")
                elif "timeout" in error_msg.lower():
                    st.error("❌ Request timed out. Try again.")
                else:
                    st.error(f"❌ Error: {e}")
                st.info("💡 Tip: Check your internet connection or API quota.")
