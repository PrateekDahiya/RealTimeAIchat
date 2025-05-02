from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import os
import json
import re
import logging
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import difflib

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static')
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60)

# Get API key from environment or default to empty string
api_key = os.environ.get("TOKEN_KEY", "")
if not api_key:
    logger.warning("No API key found. Please set TOKEN_KEY environment variable.")

# Initialize Groq client
try:
    client = Groq(api_key=api_key)
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    client = None

# Initialize the conversation history
HISTORY_FILE = "conversation_history.json"

def load_conversation_history():
    """Load conversation history from file or create empty history"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        else:
            return []
    except Exception as e:
        logger.error(f"Error loading conversation history: {e}")
        return []

def save_conversation_history(history):
    """Save conversation history to file"""
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving conversation history: {e}")

# Load conversation history
conversation_history = load_conversation_history()

# Initialize system message
system_message = {
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

def is_duplicate_question(new_text):
    """Check if the question is a duplicate or very similar to a recent one"""
    if not conversation_history:
        return False
    
    # Check last 5 questions to allow for follow-ups
    recent_questions = [item['question'] for item in conversation_history[-5:]]
    
    for question in recent_questions:
        # Calculate similarity ratio
        similarity = difflib.SequenceMatcher(None, new_text.lower(), question.lower()).ratio()
        if similarity > 0.85:  # High similarity threshold
            return True
    
    return False

def is_incomplete_question(text):
    """Check if the question seems incomplete"""
    # Very short queries are often incomplete
    if len(text.split()) < 3:
        return True
    
    # Questions ending with prepositions or conjunctions often incomplete
    incomplete_endings = ['and', 'or', 'but', 'so', 'if', 'with', 'at', 'by', 'for', 'from', 'of', 'to']
    for ending in incomplete_endings:
        if text.lower().strip().endswith(ending):
            return True
    
    return False

def check_context_completion(current_text):
    """Check if this query completes a previous incomplete query"""
    if not conversation_history or len(conversation_history) < 2:
        return current_text
    
    last_question = conversation_history[-1]['question']
    
    # If last question was incomplete and current one would make sense appended
    if is_incomplete_question(last_question):
        combined = f"{last_question} {current_text}"
        # Return combined text if it makes more sense as one question
        return combined
    
    return current_text

def clean_text(text):
    """Clean and normalize input text"""
    # Remove multiple spaces, normalize punctuation
    text = re.sub(r'\s+', ' ', text).strip()
    # Capitalize first letter if it's a new sentence
    if text and not text[0].isupper() and len(text) > 1:
        text = text[0].upper() + text[1:]
    # Add question mark if it's clearly a question without one
    question_starters = ['who', 'what', 'when', 'where', 'why', 'how', 'can', 'could', 'will', 'would', 'should', 'do', 'does', 'did', 'is', 'are', 'was', 'were']
    if any(text.lower().startswith(q) for q in question_starters) and not text.endswith('?'):
        text += '?'
    return text

def call_chat_gpt(text):
    """Process text and call the language model"""
    if not text or not text.strip():
        return "I didn't catch that. Could you please repeat?"
    
    if not client:
        return "Sorry, I'm not connected to my language model at the moment."
    
    # Clean and normalize text
    text = clean_text(text)
    
    # Check for duplicates
    if is_duplicate_question(text):
        logger.info(f"Duplicate question detected: {text}")
        # Find the most similar question and return its answer
        highest_similarity = 0
        most_similar_answer = ""
        
        for item in conversation_history[-5:]:
            similarity = difflib.SequenceMatcher(None, text.lower(), item['question'].lower()).ratio()
            if similarity > highest_similarity:
                highest_similarity = similarity
                most_similar_answer = item['answer']
        
        if most_similar_answer:
            return most_similar_answer
    
    # Check for incomplete questions and context
    if is_incomplete_question(text):
        text = check_context_completion(text)
    
    try:
        # Prepare messages for LLM
        messages = [system_message]
        
        # Add last 3 exchanges for context if available
        context_history = []
        if conversation_history:
            recent_history = conversation_history[-3:]
            for item in recent_history:
                context_history.append({"role": "user", "content": item["question"]})
                context_history.append({"role": "assistant", "content": item["answer"]})
        
        messages.extend(context_history)
        messages.append({"role": "user", "content": text})
        
        # Call the language model
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",
            max_tokens=200,
            temperature=0.7,
        )
        
        reply = chat_completion.choices[0].message.content
        
        # Add to conversation history with timestamp
        new_entry = {
            "question": text,
            "answer": reply,
            "timestamp": datetime.now().isoformat()
        }
        
        conversation_history.append(new_entry)
        save_conversation_history(conversation_history)
        
        return reply
        
    except Exception as e:
        logger.error(f"Error calling language model: {e}")
        return "Sorry, I encountered an error processing your request."

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template("index.html")

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route("/keepalive", methods=["GET"])
def keep_alive():
    """Simple endpoint to keep the server alive"""
    return "Alive", 200

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected")
    emit('conversation_count', {'count': len(conversation_history)})

@socketio.on('speech_input')
def handle_speech_input(data):
    """Process speech input from client"""
    user_text = data.get('text', '')
    logger.info(f"Received speech input: {user_text}")
    
    reply = call_chat_gpt(user_text)
    current_index = len(conversation_history) - 1 if conversation_history else -1
    
    emit('assistant_reply', {
        'reply': reply, 
        'totalQuestions': len(conversation_history),
        'currentIndex': current_index
    })

@socketio.on('get_conversation_count')
def handle_get_count():
    """Send total count of conversations"""
    emit('conversation_count', {'count': len(conversation_history)})

@socketio.on('get_conversation')
def handle_get_conversation(data):
    """Send a specific conversation to client"""
    current_index = data.get('index', -1)  

    if current_index == -1 and conversation_history:
        current_index = len(conversation_history) - 1  # Get the last conversation

    if not conversation_history or current_index < 0 or current_index >= len(conversation_history):
        emit('conversation_response', {
            'question': 'No conversation history', 
            'answer': 'Ask me something to start our conversation!',
            'index': -1,
            'totalQuestions': len(conversation_history)
        })
    else:
        qa = conversation_history[current_index]
        emit('conversation_response', {
            'question': qa['question'], 
            'answer': qa['answer'], 
            'index': current_index,
            'totalQuestions': len(conversation_history)
        })

@socketio.on('navigate_conversation')
def handle_navigation(data):
    """Handle navigation between conversations"""
    current_index = data.get('index', -1)
    direction = data.get('direction', 'next')
    
    if direction == 'next':
        current_index += 1
    elif direction == 'previous':
        current_index -= 1
    
    # Prevent out of range indices
    current_index = max(0, min(current_index, len(conversation_history) - 1)) if conversation_history else -1
    
    # Emit the new question-answer pair
    handle_get_conversation({'index': current_index})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
    logger.info(f"Starting server on port {port}, debug mode: {debug}")
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)
