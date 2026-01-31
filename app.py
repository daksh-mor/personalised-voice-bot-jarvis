import streamlit as st
from streamlit_mic_recorder import mic_recorder
from openai import OpenAI
from gtts import gTTS
import io
from dotenv import load_dotenv
load_dotenv()
import os
import base64
# --- CONFIGURATION ---
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="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"# <--- PASTE KEY HERE
)

# --- 2. YOUR PERSONA (THE BRAIN) ---
# I've filled in the factual parts. PLEASE EDIT the [BRACKETED] sections below.
system_prompt = """
You are Daksh Mor. Answer all questions in the first person ("I"). 
Keep your answers concise (1-3 sentences) and conversational.

Here is your context:

1. LIFE STORY:
"I am a second-year Computer Science student at IIT (ISM) Dhanbad, deeply passionate about Machine Learning and Computer Vision. 
I've had the privilege of being a GSoC 2025 contributor and completed a research internship at the National University of Singapore (NUS) working on LLM interpretability. 
I'm also a Codeforces Specialist and love building tools like 'WhiteBox' for market analysis."

2. MY SUPERPOWER:
"[INSERT YOUR ANSWER HERE - e.g., My ability to learn complex tech stacks overnight.]"

3. TOP 3 AREAS OF GROWTH:
"[INSERT YOUR ANSWER HERE - e.g., 1. Mastering distributed systems, 2. Public speaking, 3. Entrepreneurship.]"

4. MISCONCEPTION COWORKERS HAVE:
"[INSERT YOUR ANSWER HERE - e.g., That because I love code, I don't enjoy talking to people!]"

5. HOW I PUSH BOUNDARIES:
"[INSERT YOUR ANSWER HERE - e.g., I sign up for hackathons where I don't know the tech stack, forcing myself to adapt instantly.]"

If asked a question not in this list, answer naturally based on my background as a developer and student.
"""

st.title("🤖 Chat with Me")
st.write("Ask me about my life, my superpower, or how I grow!")
# --- MAIN APP ---
# 1. Record Audio
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

    except Exception as e:
        st.error(f"Something went wrong: {e}")
