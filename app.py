import streamlit as st
from streamlit_mic_recorder import mic_recorder
from openai import OpenAI
from gtts import gTTS
import io
from dotenv import load_dotenv
load_dotenv()
import os
st.set_page_config(page_title="Voice Bot - Hanuman Ram", page_icon="🤖", layout="wide")

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

# --- 2. YOUR PERSONA (THE BRAIN) ---
# I've filled in the factual parts. PLEASE EDIT the [BRACKETED] sections below.
system_prompt = """
You are Hanuman Ram Jethu. Answer all questions in the first person ("I"). 
Keep your answers concise (1-3 sentences) and conversational.

Here is your context:

1. LIFE STORY:
"I am a final-year student, currently grinding through LeetCode and applying for jobs. 
I enjoy coding in Python and Java, and when I'm not studying, I'm usually gaming or scrolling through tech Twitter. 
I'm just trying to build a solid career and learn as I go."

2. MY SUPERPOWER:
"I’m really good at Googling errors. If I don't know the answer, I can find the Stack Overflow thread that does in about 30 seconds."

3. TOP 3 AREAS OF GROWTH:
"1. Improving my communication skills, 2. Learning React so I can be 'full stack', and 3. Actually fixing my sleep schedule."

4. MISCONCEPTION COWORKERS HAVE:
"That because I study CS, I know how to fix their printer or WiFi. (I usually don't.)"

5. HOW I PUSH BOUNDARIES:
"I force myself to apply for roles that I only meet 60% of the qualifications for. It’s scary, but you have to shoot your shot."

If asked a question not in this list, answer naturally based on my background as a regular student and developer.
"""

st.title("🤖 Chat with Me")
st.markdown("### Ask me about my life, superpower, growth areas, and more!")
st.markdown("---")

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for message in st.session_state.messages:
    if message["role"] == "user":
        st.write(f"👤 **You:** {message['content']}")
    else:
        st.write(f"🤖 **Me:** {message['content']}")

# Clear history button
if st.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

st.divider()

# --- MAIN APP ---
# 1. Record Audio
st.markdown("### 🎤 Start Recording")
audio_data = mic_recorder(
    start_prompt="🎤 Start Speaking",
    stop_prompt="🛑 Stop Recording",
    key='recorder'
)

if audio_data:
    # 2. Transcribe (Ears)
    with open("temp_input.wav", "wb") as f:
        f.write(audio_data['bytes'])
        
    st.write("👂 Listening...")
    
    try:
        with open("temp_input.wav", "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file
            )
        user_text = transcription.text
        st.success(f"You said: {user_text}")

        # Save user message to history
        st.session_state.messages.append({"role": "user", "content": user_text})

        # 3. Generate Response (Brain)
        st.write("🧠 Thinking...")
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ]
        )
        ai_response = completion.choices[0].message.content
        st.info(f"AI: {ai_response}")

        # Save AI response to history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

# 4. Convert to Audio (Mouth)
        st.write("🗣️ Generating Voice...")
        tts = gTTS(text=ai_response, lang='en')
        tts.save("response.mp3")
        
        # 5. Auto-Play Audio (The Fix)
        # We convert the audio file to a base64 string and embed it in HTML
        with open("response.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            
            # HTML to auto-play the audio
            md = f"""
                <audio controls autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            st.markdown(md, unsafe_allow_html=True)
        
        # Cleanup temp files
        import os
        if os.path.exists("temp_input.wav"):
            os.remove("temp_input.wav")
        if os.path.exists("response.mp3"):
            os.remove("response.mp3")

    except FileNotFoundError:
        st.error("❌ Audio recording failed. Please try again.")
    except Exception as e:
        error_msg = str(e)
        if "API" in error_msg or "authentication" in error_msg.lower():
            st.error("❌ API Error: Check your API key in .env file")
        elif "timeout" in error_msg.lower():
            st.error("❌ Request timed out. Please try again.")
        else:
            st.error(f"❌ Something went wrong: {e}")
        st.info("💡 Try refreshing the page or checking your connection.")
