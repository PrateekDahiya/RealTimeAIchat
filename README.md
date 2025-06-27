# Realtime AI Chat App

**Hosted at**: [https://realtimeaichat-1wxn.onrender.com](https://realtimeaichat-1wxn.onrender.com)

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

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/PrateekDahiya/realtime-ai-chat.git
cd realtime-ai-chat
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Set up environment variables
Create a .env file in the root directory:
```bash
TOKEN_KEY=your_groq_api_key_here
DEBUG=False
PORT=5000
```

### Running the App
Run the app with:

```bash
python API.py
```
Then visit: [http://localhost:5000](http://localhost:5000)
