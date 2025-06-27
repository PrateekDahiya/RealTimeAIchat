# Realtime AI Chat App

**Hosted at**: [https://realtimeaichat.onrender.com](https://realtimeaichat.onrender.com)

A real-time voice-based AI chat application powered by Flask, Socket.IO, and LLaMA-3 via Groq API. It simulates a conversation with *Prateek Dahiya*, a software developer persona, and includes smart features like duplicate detection, context awareness, and speech interaction.

---

## 🚀 Features

- 🔊 **Voice-enabled Input**: Speak your questions using your microphone.
- 🤖 **AI Persona Simulation**: Interact with "Prateek Dahiya", a detailed, developer-student persona.
- 🔁 **Context-aware Replies**: Maintains conversation history for coherent responses.
- 🧠 **Duplicate Detection**: Avoids repetitive answers using fuzzy matching.
- 💾 **Conversation Memory**: Saves and retrieves past question-answer pairs.
- 🌐 **Real-time Communication**: Powered by Flask-SocketIO and WebSockets.

---

## 🧱 Tech Stack

- **Backend**: Flask, Flask-SocketIO, Eventlet
- **LLM API**: [Groq](https://groq.com) using LLaMA 3
- **Frontend**: HTML/CSS/JavaScript (in `templates/` and `static/`)
- **Voice Recognition**: SpeechRecognition + Pyttsx3
- **Environment Variables**: Handled with `python-dotenv`

---

## 📦 Requirements

Install all dependencies using:

```bash
pip install -r requirements.txt
