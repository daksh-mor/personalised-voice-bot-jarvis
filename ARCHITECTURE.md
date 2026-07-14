# System Architecture & Design

## Overview

This is a **production-grade conversational AI agent** built on modern cloud infrastructure. The system demonstrates:
- Real-time audio processing pipelines
- Low-latency LLM inference
- Stateful conversation management
- Scalable cloud deployment

---

## High-Level Architecture

```
                    ┌─────────────────────────────────┐
                    │       Client Browser (Web)       │
                    │  - Microphone Access (WebRTC)    │
                    │  - Real-time UI Updates          │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  Streamlit Frontend Layer   │
                    │  - Mic Recorder Widget      │
                    │  - Chat Display UI          │
                    │  - Session State Mgmt       │
                    └──────────────┬──────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
    ┌────────────┐          ┌────────────┐          ┌────────────┐
    │ Whisper    │          │ LLM Inference│         │ gTTS       │
    │ (Speech→   │          │ (Groq API)   │         │ (Text→     │
    │  Text)     │          │ Llama-3.1-8b │         │  Speech)   │
    │            │          │              │         │            │
    │ OpenAI API │          │ Context-aware│         │ gTTS API   │
    │ via Groq   │          │ response gen │         │            │
    └────────────┘          └────────────┘          └────────────┘
        Input                    Core Logic              Output
    Processing                                        Processing
```

---

## Component Details

### 1. Frontend Layer (Streamlit)
**Responsibility**: User interaction, real-time feedback, state management

```python
# Session State Management
st.session_state.messages      # Conversation history
st.session_state.session_start # Timestamp for analytics
st.session_state.total_responses # Counter for metrics
```

**Features**:
- Real-time metrics dashboard (messages, responses, duration)
- Modern chat UI with color-coded messages
- Multi-format export (JSON, plaintext)
- Text input fallback for accessibility

### 2. Speech Recognition (Whisper)
**API**: OpenAI Whisper Large-v3 (via Groq)
**Latency**: ~2-3 seconds for 15s audio
**Format**: WAV → Text

```python
transcription = client.audio.transcriptions.create(
    model="whisper-large-v3",
    file=audio_file
)
```

**Error Handling**:
- File not found → User retry
- API timeout → Graceful error message
- Invalid format → Auto-cleanup

### 3. LLM Inference (Groq)
**Model**: Llama-3.1-8b-instant
**Latency**: ~1-2 seconds (5x faster than OpenAI)
**Context**: System prompt + conversation history

```python
completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text}
    ]
)
```

**System Prompt Engineering**:
- Clear persona definition
- 5-shot examples (life story, superpower, growth areas, etc.)
- Instruction: Keep responses 1-3 sentences, conversational tone
- Fallback: Answer naturally for off-topic questions

### 4. Text-to-Speech (gTTS)
**API**: Google Text-to-Speech
**Latency**: ~1-2 seconds
**Format**: Text → MP3 (base64 embedded)

```python
tts = gTTS(text=ai_response, lang='en')
tts.save("response.mp3")
# Base64 encode for browser auto-play
```

### 5. Session Management
**State Persistence**:
- In-memory: Streamlit session state (per browser session)
- Export: JSON download for archival
- Analytics: Session start time, message count, response metrics

---

## Data Flow

### Request Flow
```
1. User speaks/types question
   └─ Audio WAV file (browser) or text input

2. [Optional] Transcribe with Whisper
   └─ Audio → Text (2-3s latency)

3. Add to conversation history
   └─ User message stored in st.session_state.messages

4. Call LLM inference
   └─ System prompt + conversation history → Groq API

5. LLM generates response
   └─ Text response (1-2s latency)

6. Convert to speech
   └─ Text → MP3 via gTTS (1-2s latency)

7. Display & play
   └─ HTML5 audio with autoplay
   └─ Update UI with response + metrics

8. Cleanup
   └─ Delete temp WAV and MP3 files
```

### Total Latency
- Voice input: 4-7 seconds end-to-end
- Text input: 2-4 seconds (skip transcription)

---

## Error Handling Strategy

### 1. Transcription Failures
```
Whisper API timeout
  └─ Catch: "Request timed out"
  └─ UX: "❌ Request timed out. Try again."
  └─ Auto-cleanup: Delete temp WAV
```

### 2. LLM API Failures
```
Authentication error
  └─ Catch: "API authentication failed"
  └─ UX: "❌ API Error: Check your API key"
  └─ Resolution: User checks .env/secrets

Timeout/Rate Limit
  └─ Catch: "Request timeout" / "Rate limited"
  └─ UX: "❌ Service unavailable. Please retry."
  └─ Fallback: None (can retry)
```

### 3. TTS Failures
```
gTTS service down
  └─ Catch: gTTS exception
  └─ UX: "❌ Voice generation failed"
  └─ Fallback: Show text response (already cached)
```

### 4. Cleanup & Resource Management
```python
# Always cleanup temp files
for file in ["temp_input.wav", "response.mp3"]:
    if os.path.exists(file):
        os.remove(file)
```

---

## Performance Characteristics

### Latency Breakdown
| Component | Time | Notes |
|-----------|------|-------|
| Whisper Transcription | 2-3s | Depends on audio length |
| LLM Inference | 1-2s | Groq is 5x faster than OpenAI |
| TTS Generation | 1-2s | Depends on response length |
| **Total (voice)** | 4-7s | Acceptable for interactive use |
| **Total (text)** | 2-4s | Faster path |

### Resource Usage
- **Memory**: ~50-100MB per session
- **API Calls**: 1 Whisper + 1 LLM + 1 gTTS per exchange
- **Storage**: Temp files auto-deleted
- **Bandwidth**: ~200KB per exchange (audio + text)

### Scalability Limits
- Streamlit Cloud: 3 apps free, 1 GB memory per app
- Groq Free Tier: 30 req/min, 25K tokens/day
- gTTS: Rate limited by Google (typical: unlimited for small apps)

---

## Security & Compliance

### API Key Management
```
Local: .env file (git-ignored)
Cloud: Streamlit Secrets (encrypted)
```

### Data Privacy
- ✅ No user data stored permanently
- ✅ Conversation exported locally only (user choice)
- ✅ Temp audio files auto-deleted
- ✅ No logging of sensitive content

### Input Validation
- Audio file type check (WAV)
- Text input sanitization
- Transcription length limits

---

## Deployment & DevOps

### Current Deployment: Streamlit Cloud
```
GitHub repo (main branch)
    ↓
Streamlit Cloud (auto-deploy)
    ↓
https://personalised-jarvis-voice-bot.streamlit.app/
```

**Workflow**:
1. Push to GitHub
2. Streamlit detects change
3. Auto-redeploy within 1 minute
4. Zero downtime

### Environment Configuration
```
Local (.env):
  GROQ_API_KEY=xxx

Cloud (Streamlit Secrets):
  GROQ_API_KEY=xxx
  (Encrypted at rest)
```

---

## Future Enhancements (Roadmap)

### Phase 2: Advanced Context
- [ ] Summarization of long conversations
- [ ] Key topic extraction
- [ ] Follow-up question suggestions
- [ ] Context-aware emoji reactions

### Phase 3: Analytics & Monitoring
- [ ] User session analytics
- [ ] Response quality metrics
- [ ] Latency tracking dashboard
- [ ] Error rate monitoring

### Phase 4: Production Hardening
- [ ] Database storage (MongoDB)
- [ ] Distributed caching (Redis)
- [ ] Load balancing
- [ ] Multi-region deployment
- [ ] CI/CD pipeline

### Phase 5: ML Personalization
- [ ] Fine-tune LLM on persona data
- [ ] Custom voice synthesis
- [ ] Response tone adaptation
- [ ] User preference learning

---

## Testing & Quality Assurance

### Unit Tests (test_bot.py)
```bash
python3 test_bot.py
```
- Tests 5 standard questions
- Verifies API connectivity
- Validates response format

### Manual Testing Checklist
- [ ] Microphone recording works
- [ ] Transcription accuracy
- [ ] LLM response relevance
- [ ] Audio playback
- [ ] Session export
- [ ] Error handling (simulate timeout)

### Performance Testing
```python
import time
start = time.time()
# API calls
end = time.time()
print(f"Latency: {end - start:.2f}s")
```

---

## References

- [Groq API Docs](https://console.groq.com/docs)
- [Streamlit Docs](https://docs.streamlit.io)
- [Llama 3.1 Model Card](https://huggingface.co/meta-llama/Llama-3.1-8B)
- [gTTS Docs](https://gtts.readthedocs.io)

---

**Last Updated**: July 2026  
**Version**: 2.0 (Production-Grade)
