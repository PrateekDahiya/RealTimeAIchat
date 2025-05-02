# server.py
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import speech_recognition as sr
import pyttsx3
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

r = sr.Recognizer()
client = Groq(api_key=os.environ.get("TOKEN_KEY"))

messages = [
    {
        "role": "system",
        "content": (
            "You are Prateek Dahiya, a software developer and student at NIT Kurukshetra (B.Tech IT, CGPA 8.00). "
            "You speak in the first person, representing yourself. "
            "You have experience with Java, Python, C++, JavaScript, React, Node.js, Flask, MongoDB, and MySQL. "
            "You've built projects like VidVault (YouTube clone), LingoVerse (language learning), and a Pac-Man clone. "
            "You've led a hardware team building an Automatic Garage Controller using Arduino. "
            "You're active in fine arts and have solved over 200 coding questions on platforms like LeetCode and GFG. "
            "You respond concisely and factually, using 30 words max per reply. Use line breaks after every 50 words. "
            "Do not refer to yourself as an assistant—you're speaking as Prateek. "
            "You can end conversations if asked directly or in case of abuse."
        )
    }
]


def callChatGPT(text):
    if text:
        messages.append({"role": "user", "content": text})
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",
        )
        reply = chat_completion.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        return reply

@app.route('/')
def index():
    return render_template("./index.html")

@app.route("/keepalive", methods=["GET"])
def keep_alive():
    return "Alive", 200

@socketio.on('speech_input')
def handle_speech_input(data):
    user_text = data['text']
    reply = callChatGPT(user_text)
    emit('assistant_reply', {'reply': reply})

if __name__ == '__main__':
    socketio.run(app, debug=True)
