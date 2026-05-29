# personalised-voice-bot-jarvis

A voice chatbot that responds to personal questions as if you were answering them. Uses Groq AI API for fast LLM responses and gTTS for voice synthesis.

## ✨ Features

- 🎤 **Voice Input**: Record questions using your microphone
- 🧠 **AI Responses**: LLM-powered responses based on your persona
- 🗣️ **Voice Output**: Responses converted to speech and auto-played
- 💬 **Conversation History**: Track all Q&A in the session
- 🧹 **Auto Cleanup**: Temporary files cleaned after use
- 🛡️ **Secure**: API keys stored in `.env` (never committed)

## 🚀 Quick Start

### 1. **Clone & Setup**
```bash
git clone <your-repo>
cd personalised-voice-bot-jarvis
pip3 install -r requirements.txt
```

### 2. **Configure API Key**
Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key: https://console.groq.com

### 3. **Run Locally**
```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## 🧪 Testing

Run the test suite to verify bot responses:
```bash
python3 test_bot.py
```

## 📝 Sample Questions

The bot is trained to answer:
1. What should we know about your life story in a few sentences?
2. What's your #1 superpower?
3. What are the top 3 areas you'd like to grow in?
4. What misconception do your coworkers have about you?
5. How do you push your boundaries and limits?

## 🚢 Deployment

### Option 1: **Streamlit Cloud** (Recommended - Free)

1. **Push to GitHub** (already done ✅)

2. **Deploy on Streamlit Cloud**:
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your GitHub repo: `personalised-voice-bot-jarvis`
   - Select branch: `main`
   - Select file: `app.py`
   - Click "Deploy"

3. **Set API Key Secrets** (IMPORTANT):
   - After deployment, click **"Manage app"** (lower right)
   - Go to **Secrets** tab
   - Add this line:
     ```
     GROQ_API_KEY = "your_groq_api_key_here"
     ```
   - Click "Save"
   - App will auto-reload ✅

4. **Get your app URL** from Streamlit Cloud dashboard

### Option 2: **Railway** (Free tier available)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Option 3: **Heroku** (Paid)
```bash
heroku create your-app-name
git push heroku main
```

## 📋 Requirements

- Python 3.9+
- Streamlit
- OpenAI SDK (for Groq API)
- gTTS (Google Text-to-Speech)
- streamlit-mic-recorder

## 🔒 Security Notes

- ✅ API keys in `.env` (not in code)
- ✅ `.gitignore` prevents accidental commits
- ✅ Temp files auto-deleted
- ✅ No sensitive data logged

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| API key invalid | Check `.env` file has correct key from https://console.groq.com |
| Mic not working | Check browser permissions (allow microphone) |
| No audio output | Ensure speakers are on and check browser volume |
| Timeout errors | Check internet connection and Groq API status |

## 📞 Support

Submit issues or questions on GitHub.

---

**Made with ❤️ by Hanuman Ram Jethu**

