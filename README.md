# personalised-voice-bot-jarvis

A **production-grade conversational voice agent** that combines real-time audio processing with AI-powered responses. Built for speed, accessibility, and intelligent conversation context.

## ✨ Key Features

### 🎯 Core Capabilities
- 🎤 **Voice Input**: Real-time microphone recording with transcription (Whisper-large-v3)
- 🧠 **AI Responses**: Context-aware replies powered by Llama-3.1-8b (Groq API)
- 🗣️ **Voice Output**: Natural speech synthesis with gTTS
- 💬 **Conversation Memory**: Full session history with context preservation
- ⏱️ **Live Metrics**: Real-time dashboard showing message count, response time, session duration

### 🚀 Advanced Features (V2)
- 📝 **Multi-format Export**: Download conversations as JSON or plain text
- 💾 **Session Persistence**: Automatic session tracking with timestamps
- 🎨 **Modern UI**: Professional chat interface with custom styling
- ✏️ **Text + Voice Input**: Toggle between typing and speaking
- 📊 **Analytics Dashboard**: Message count, response stats, session duration
- ⚡ **Smart Error Handling**: Graceful degradation with detailed user feedback
- 🔄 **Auto-cleanup**: Temporary files cleaned after each interaction

## 🏗️ Architecture

```
┌─────────────────┐
│   User Input    │  (Voice or Text)
└────────┬────────┘
        │
    ┌────▼─────┐
    │ Transcribe│  (Whisper API)
    └────┬─────┘
        │
    ┌────▼────────┐
    │ Context Mem │  (Session State)
    └────┬────────┘
        │
    ┌────▼──────────────┐
    │ LLM Inference     │  (Groq Llama-3.1-8b)
    └────┬──────────────┘
        │
    ┌────▼──────┐
    │ TTS Output│  (gTTS)
    └────┬──────┘
        │
    ┌────▼──────────┐
    │ Audio Playback│
    └───────────────┘
```

### Tech Stack
- **Frontend**: Streamlit (Python)
- **LLM Engine**: Groq API (llama-3.1-8b-instant)
- **Speech Recognition**: OpenAI Whisper (via Groq)
- **Text-to-Speech**: Google gTTS
- **Hosting**: Streamlit Cloud
- **Storage**: Session state (in-memory + JSON export)

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/hanumanjethu/personalised-voice-bot-jarvis
cd personalised-voice-bot-jarvis
pip3 install -r requirements.txt
```

### 2. Configure API Key
Create `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get free key: https://console.groq.com

### 3. Run Locally
```bash
streamlit run app.py
```
Visit: http://localhost:8501

## 📝 Sample Questions

The bot is trained to answer:
1. **What should we know about your life story?**
2. **What's your #1 superpower?**
3. **What are the top 3 areas you'd like to grow in?**
4. **What misconception do your coworkers have about you?**
5. **How do you push your boundaries and limits?**

*Plus any follow-up questions based on context!*

## 🧪 Testing

```bash
python3 test_bot.py
```

Runs 5 test cases to verify bot responses.

## 🎯 Live Deployment

**Live Demo**: https://personalised-jarvis-voice-bot.streamlit.app/

### Deploy Your Own (Streamlit Cloud)

1. Push to GitHub ✅
2. Go to https://share.streamlit.io
3. Click "New app" → Select repo/branch/file
4. After deploy: **Manage app** → **Secrets** → Add:
   ```
   GROQ_API_KEY = "your_key"
   ```
5. App auto-reloads ✅

## 📦 Requirements

```
streamlit>=1.28
streamlit-mic-recorder>=0.0.11
openai>=1.3
gTTS>=2.4
python-dotenv>=1.0
```

## 🔒 Security

- ✅ API keys in `.env` (never committed)
- ✅ `.gitignore` prevents leaks
- ✅ Temp files auto-deleted
- ✅ No sensitive data logged
- ✅ Cloud secrets for production

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| API key invalid | Verify key at https://console.groq.com |
| Mic not working | Check browser permissions |
| No audio output | Test speakers, check browser volume |
| Timeout errors | Check internet, verify Groq API status |
| Transcription fails | Speak clearly, check microphone |

## 📊 Performance

- **Transcription**: ~2-3 seconds (Whisper-large-v3)
- **LLM Response**: ~1-2 seconds (Groq llama-3.1-8b)
- **TTS Generation**: ~1-2 seconds (gTTS)
- **Total Latency**: ~4-7 seconds end-to-end

## 🎨 Customization

### Update Your Persona
Edit `app.py` lines 31-55 (system_prompt) to customize responses.

### Modify Styling
Update CSS in `app.py` lines 16-22 for custom colors/fonts.

### Change Voice Settings
In `app.py` line 124: `gTTS(text=ai_response, lang='en', slow=False)`

## 📝 License

Open source - feel free to fork and extend!

---

**Built with ❤️ by Hanuman Ram Jethu**  
*AI Engineer | LeetCode Enthusiast | Full-Stack Developer*

