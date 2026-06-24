from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import uuid
import time
import io
import json
import random
import requests
from datetime import datetime
from dotenv import load_dotenv
app = Flask(__name__, static_folder='static')
app.secret_key = 'mindmate_secret_key_2026'
# ==================== NEW LOGIN ROUTES ====================

@app.route('/login', methods=['GET'])
def login_page():
    return send_from_directory('.', 'login.html')

@app.route('/login', methods=['POST'])
def do_login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Demo credentials
    if email == "demo@mindmate.ai" and password == "demo123":
        session['user'] = {'email': email, 'name': 'Demo User'}
        return redirect('/')  # Redirect to main page
    else:
        return "Invalid credentials! Use demo@mindmate.ai / demo123", 401

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# Protect main page (optional)

# Try to import gTTS, show error if not installed
try:
    from gtts import gTTS # type: ignore
    GTTS_AVAILABLE = True
    print("[OK] gTTS loaded successfully")
except ImportError:
    GTTS_AVAILABLE = False
    print("[ERROR] gTTS not installed! Run: pip install gtts")
# Try to import SarvamAI Python SDK
try:
    from sarvamai import SarvamAI # type: ignore
    SARVAM_SDK_AVAILABLE = True
    print("[OK] SarvamAI SDK loaded successfully")
except ImportError:
    SARVAM_SDK_AVAILABLE = False
    print("[WARNING] SarvamAI SDK not installed. Falling back to direct REST requests.")
load_dotenv()
app = Flask(__name__, static_folder='static')
CORS(app)
# Create necessary folders
os.makedirs('static', exist_ok=True)
os.makedirs('temp', exist_ok=True)
os.makedirs('data', exist_ok=True)
# Local database file paths
HISTORY_FILE = 'data/history.json'
STRESS_DATA_FILE = 'data/stress_data.json'
# ============================================
# DATA STORAGE HELPERS
# ============================================
def load_history():
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []
def save_history(history):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving history: {e}")
def load_stress_data():
    try:
        with open(STRESS_DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []
def save_stress_data(data):
    try:
        with open(STRESS_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving stress data: {e}")
def add_stress_log(emotion, stress_score, source='text'):
    logs = load_stress_data()
    logs.append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'emotion': emotion,
        'stress_score': stress_score,
        'source': source
    })
    if len(logs) > 50:
        logs = logs[-50:]
    save_stress_data(logs)
    return logs
# ============================================
# OFFLINE BACKUP RESPONSES
# ============================================
RESPONSES = {
    'mr': {  # Marathi
        'greeting': "नमस्कार! मी तुमचा माइंडमेट सहाय्यक आहे. तुम्ही कसे आहात?",
        'how_are_you': "मी ठीक आहे, धन्यवाद! तुम्ही कसे आहात?",
        'good': "तुम्ही ठीक आहात हे ऐकून खूप आनंद झाला!",
        'sad': "तुम्ही दुःखी आहात हे ऐकून मला वाईट वाटले. मी तुमच्यासोबत आहे.",
        'stressed': "तुम्ही तणावात आहात. कृपया खोल श्वास घ्या. श्वास घ्या... आणि सोडा.",
        'angry': "राग येणे सामान्य आहे. तुमच्या भावना वैध आहेत.",
        'tired': "तुम्ही थकले आहात. कृपया विश्रांती घ्या.",
        'default': "मी तुमचे ऐकत आहे. कृपया सुरू ठेवा."
    },
    'hi': {  # Hindi
        'greeting': "नमस्ते! मैं आपका माइंडमेट सहायक हूँ। आप कैसे हैं?",
        'how_are_you': "मैं ठीक हूँ, धन्यवाद! आप कैसे हैं?",
        'good': "आप ठीक हैं सुनकर बहुत अच्छा लगा!",
        'sad': "आप दुखी हैं सुनकर मुझे दुख हुआ। मैं आपके साथ हूँ।",
        'stressed': "आप तनाव में हैं। कृपया गहरी सांस लें। सांस लें... और छोड़ें।",
        'angry': "गुस्सा आना सामान्य है। आपकी भावनाएँ वैध हैं।",
        'tired': "आप थके हुए हैं। कृपया आराम करें।",
        'default': "मैं आपकी बात सुन रहा हूँ। कृपया जारी रखें।"
    },
    'te': {  # Telugu
        'greeting': "నమస్కారం! నేను మీ మైండ్మేట్ సహాయకుడిని. మీరు ఎలా ఉన్నారు?",
        'how_are_you': "నేను బాగానే ఉన్నాను, ధన్యవాదాలు! మీరు ఎలా ఉన్నారు?",
        'good': "మీరు బాగానే ఉన్నారని విని చాలా సంతోషంగా ఉంది!",
        'sad': "మీరు బాధగా ఉన్నారని విని నాకు బాధగా ఉంది. నేను మీతో ఉన్నాను.",
        'stressed': "మీరు ఒత్తిడికి గురవుతున్నారు. దయచేసి లోతుగా శ్వాస తీసుకోండి.",
        'default': "నేను మీ మాట వింటున్నాను. దయచేసి కొనసాగించండి."
    },
    'en': {  # English
        'greeting': "Namaste! I'm your MindMate assistant. How are you?",
        'how_are_you': "I'm doing well, thank you! How are you?",
        'good': "I'm glad to hear you're doing well!",
        'sad': "I'm sorry to hear you're feeling sad. I'm here with you.",
        'stressed': "I understand you're feeling stressed. Take a deep breath. Breathe in... and out.",
        'angry': "Feeling angry is normal. Your feelings are valid.",
        'tired': "You sound tired. Please rest.",
        'default': "I'm listening. Please continue."
    }
}
def detect_intent(text):
    text_lower = text.lower()
    greetings = ['hello', 'hi', 'hey', 'namaste', 'नमस्कार', 'नमस्ते', 'నమస్కారం']
    how_are_you = ['how are you', 'कसे आहात', 'ఎలా ఉన్నారు', 'how do you do']
    good_words = ['good', 'great', 'happy', 'fine', 'ठीक', 'బాగా', 'well']
    sad_words = ['sad', 'unhappy', 'depressed', 'दुःखी', 'బాధ', 'down']
    stress_words = ['stress', 'stressed', 'tension', 'तणाव', 'ఒత్తిడి', 'anxious', 'worry']
    angry_words = ['angry', 'mad', 'frustrated', 'राग', 'कोపం']
    tired_words = ['tired', 'exhausted', 'sleepy', 'थका', 'అలసట']
    
    if any(w in text_lower for w in greetings):
        return 'greeting'
    elif any(w in text_lower for w in how_are_you):
        return 'how_are_you'
    elif any(w in text_lower for w in good_words):
        return 'good'
    elif any(w in text_lower for w in sad_words):
        return 'sad'
    elif any(w in text_lower for w in stress_words):
        return 'stressed'
    elif any(w in text_lower for w in angry_words):
        return 'angry'
    elif any(w in text_lower for w in tired_words):
        return 'tired'
    else:
        return 'default'
def analyze_text_stress_offline(text):
    text_lower = text.lower()
    high_stress = ['sad', 'unhappy', 'depressed', 'दुःखी', 'బాధ', 'stress', 'stressed', 'tension', 'तणाव', 'ఒత్తిడి', 'anxious', 'worry', 'suicide', 'kill', 'die', 'pain']
    low_stress = ['good', 'great', 'happy', 'fine', 'ठीक', 'బాగా', 'well', 'calm', 'relaxed']
    
    if any(w in text_lower for w in high_stress):
        return 75
    elif any(w in text_lower for w in low_stress):
        return 25
    return 40
def get_offline_fallback(text, language):
    intent = detect_intent(text)
    stress_score = analyze_text_stress_offline(text)
    lang_responses = RESPONSES.get(language, RESPONSES['en'])
    response_text = lang_responses.get(intent, lang_responses['default'])
    return response_text, stress_score
# ============================================
# SARVAM AI LLM CONNECTOR
# ============================================
def query_sarvam_llm(user_message, language):
    """
    Queries Sarvam AI's Chat Completion API with the user message and target language.
    Returns: (response_text, stress_score)
    """
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        print("[WARNING] SARVAM_API_KEY not found in environment. Using offline fallback.")
        return get_offline_fallback(user_message, language)
    url = "https://api.sarvam.ai/v1/chat/completions"
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    # Map language codes to friendly names for the system prompt
    lang_names = {
        'en': 'English',
        'hi': 'Hindi',
        'bn': 'Bengali',
        'te': 'Telugu',
        'mr': 'Marathi',
        'ta': 'Tamil',
        'ur': 'Urdu',
        'gu': 'Gujarati',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'pa': 'Punjabi',
        'or': 'Odia'
    }
    target_lang = lang_names.get(language, 'English')
    # Construct system prompt to return output in JSON format containing the text response and stress score
    system_prompt = (
        "You are MindMate, a warm, highly empathetic, and supportive AI mental health companion.\n"
        f"Provide your response to the user's message in {target_lang}.\n"
        "Keep your response warm, supportive, and concise (2-4 sentences).\n"
        "Estimate the user's current stress level as a score between 0 and 100 based on their message.\n"
        "Format your output ONLY as a valid JSON object with the following structure:\n"
        "{\n"
        '  "response": "<supportive response in ' + target_lang + '>",\n'
        '  "stress_score": <estimated stress level of user\'s message from 0 to 100>\n'
        "}\n"
        "Do not include any Markdown backticks, HTML tags, or trailing text before or after the JSON."
    )
    payload = {
        "model": "sarvam-30b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.5
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content'].strip()
            
            # Clean potential Markdown formatting
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            try:
                parsed = json.loads(content)
                response_text = parsed.get("response", "")
                stress_score = int(parsed.get("stress_score", 40))
                return response_text, stress_score
            except Exception as pe:
                print(f"JSON parsing failed for LLM response: {pe}. Raw Content: {content}")
                return content, analyze_text_stress_offline(user_message)
        else:
            print(f"Sarvam LLM API returned error {response.status_code}: {response.text}")
            return get_offline_fallback(user_message, language)
    except Exception as e:
        print(f"Exception during Sarvam LLM query: {e}")
        return get_offline_fallback(user_message, language)

def generate_tts_audio(text, language, gender):
    """
    Generate audio for given text, language, and gender.
    Uses Sarvam AI TTS if key is present, otherwise falls back to gTTS.
    """
    api_key = os.getenv("SARVAM_API_KEY")
    audio_url = None
    
    if api_key:
        # Map frontend language code to Sarvam BCP-47 codes
        lang_map = {
            'hi': 'hi-IN', 'te': 'te-IN', 'ta': 'ta-IN', 'kn': 'kn-IN',
            'en': 'en-IN', 'bn': 'bn-IN', 'mr': 'mr-IN', 'gu': 'gu-IN',
            'ml': 'ml-IN', 'or': 'or-IN', 'pa': 'pa-IN', 'ur': 'ur-PK'
        }
        language_code = lang_map.get(language, 'en-IN')
        
        # Sarvam supports multiple speakers:
        # Female: anushka (default), kavya, aarohi, aditi
        # Male: arvind (default), narendra, madhav, chaitanya
        speaker = 'arvind' if gender == 'male' else 'anushka'
        
        url = "https://api.sarvam.ai/text-to-speech"
        payload = {
            "text": text,
            "speaker": speaker,
            "language_code": language_code,
            "format": "mp3"
        }
        headers = {
            "api-subscription-key": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                audio_filename = f"response_{uuid.uuid4().hex}.mp3"
                audio_path = os.path.join('static', audio_filename)
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                audio_url = f'/static/{audio_filename}'
                return audio_url
            else:
                print(f"Sarvam TTS failed with {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Exception during Sarvam TTS generation: {e}")
            
    # Fallback to gTTS
    if GTTS_AVAILABLE:
        try:
            lang_map = {
                'mr': 'mr', 'hi': 'hi', 'te': 'te', 'ta': 'ta',
                'kn': 'kn', 'ml': 'ml', 'bn': 'bn', 'gu': 'gu',
                'en': 'en', 'pa': 'pa', 'ur': 'ur', 'or': 'or'
            }
            tts_lang = lang_map.get(language, 'en')
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            audio_filename = f"response_{uuid.uuid4().hex}.mp3"
            audio_path = os.path.join('static', audio_filename)
            tts.save(audio_path)
            audio_url = f'/static/{audio_filename}'
        except Exception as e:
            print(f"gTTS Generation Error: {e}")
            
    return audio_url

# ============================================
# API ENDPOINTS
# ============================================
@app.route('/predict', methods=['POST'])
def predict():
    """Handle text chat messages and return LLM response with stress score"""
    message = request.form.get('message', '')
    language = request.form.get('language', 'en')
    
    if not message:
        return jsonify({'success': False, 'error': 'No message provided'}), 400
    # Call LLM
    response_text, stress_score = query_sarvam_llm(message, language)
    
    # Save to history
    risk = "red" if stress_score > 70 else "orange" if stress_score > 40 else "green"
    history = load_history()
    history.append({
        'timestamp': datetime.now().isoformat(),
        'user_message': message,
        'ai_response': response_text,
        'stress_score': stress_score,
        'risk': risk
    })
    save_history(history)
    # Save to stress dashboard log
    emotion = "distressed" if stress_score > 70 else "stressed" if stress_score > 40 else "calm"
    add_stress_log(emotion, stress_score, source='text')
    return jsonify({
        'success': True,
        'suggestion': response_text,
        'risk': risk,
        'stress_score': stress_score
    })

@app.route('/process_voice', methods=['POST'])
def process_voice():
    """Process voice text and return AI response with audio URL"""
    data = request.json
    user_text = data.get('text', '')
    language = data.get('language', 'en')
    gender = data.get('gender', 'female')
    
    if not user_text:
        return jsonify({'error': 'No text provided'}), 400
    
    # Get LLM response
    ai_response, stress_score = query_sarvam_llm(user_text, language)
    
    # Generate voice response
    audio_url = generate_tts_audio(ai_response, language, gender)
    
    # Add to stress logs
    emotion = "distressed" if stress_score > 70 else "stressed" if stress_score > 40 else "calm"
    add_stress_log(emotion, stress_score, source='voice')
    return jsonify({
        'success': True,
        'user_text': user_text,
        'ai_response': ai_response,
        'stress_score': stress_score,
        'audio_url': audio_url
    })
@app.route('/speak', methods=['POST'])
def speak():
    """Convert text to speech stream on the fly"""
    if not GTTS_AVAILABLE:
        return jsonify({'error': 'gTTS not installed'}), 500
    
    data = request.json
    text = data.get('text', '')
    language = data.get('language', 'en')
    
    if not text:
        return jsonify({'error': 'No text'}), 400
    
    lang_map = {'mr': 'mr', 'hi': 'hi', 'te': 'te', 'en': 'en', 'bn': 'bn', 'ta': 'ta', 'gu': 'gu', 'kn': 'kn', 'ml': 'ml'}
    tts_lang = lang_map.get(language, 'en')
    
    try:
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        audio_data = io.BytesIO()
        tts.write_to_fp(audio_data)
        audio_data.seek(0)
        
        return send_file(
            audio_data,
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='speech.mp3'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/analyze_voice_stress', methods=['POST'])
def analyze_voice_stress():
    """Endpoint to upload a WebM audio blob, transcribe it via Sarvam STT, and run LLM stress analysis"""
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    language = request.args.get('language', 'en')
    
    temp_path = None
    try:
        # Save audio file temporarily
        temp_filename = f"temp_{uuid.uuid4().hex}.webm"
        temp_path = os.path.join('temp', temp_filename)
        audio_file.save(temp_path)
        
        transcript = ""
        api_key = os.getenv("SARVAM_API_KEY")
        # Map language code to Sarvam STT BCP-47 codes
        lang_map = {
            'en': 'en-IN', 'hi': 'hi-IN', 'te': 'te-IN', 'ta': 'ta-IN',
            'kn': 'kn-IN', 'ml': 'ml-IN', 'bn': 'bn-IN', 'gu': 'gu-IN',
            'mr': 'mr-IN', 'pa': 'pa-IN', 'ur': 'ur-IN', 'or': 'or-IN'
        }
        stt_lang = lang_map.get(language, 'unknown')
        # Use Sarvam STT REST API
        if api_key:
            try:
                url = "https://api.sarvam.ai/speech-to-text"
                headers = {
                    "api-subscription-key": api_key
                }
                
                # Read file as binary
                with open(temp_path, 'rb') as f:
                    files = {
                        'file': (temp_filename, f, 'audio/webm')
                    }
                    data = {
                        'language_code': stt_lang
                    }
                    response = requests.post(url, headers=headers, files=files, data=data, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    transcript = result.get('transcript', '')
                    print(f"STT Transcript: {transcript}")
                else:
                    print(f"Sarvam STT failed: {response.status_code} - {response.text}")
                    transcript = "I am feeling stressed and overwhelmed"
            except Exception as stt_err:
                print(f"Error calling Sarvam STT: {stt_err}")
                transcript = "I am feeling stressed and overwhelmed"
        else:
            # Fallback
            transcript = "I am feeling stressed and overwhelmed"
        # Query LLM with the transcribed text
        ai_response, stress_score = query_sarvam_llm(transcript, language)
        emotion = "distressed" if stress_score > 70 else "stressed" if stress_score > 40 else "calm"
        
        # Save to logs
        add_stress_log(emotion, stress_score, source='voice')
        
        return jsonify({
            'success': True,
            'transcript': transcript,
            'stress_score': stress_score,
            'emotion': emotion,
            'ai_response': ai_response,
            'suggestion': ai_response
        })
    except Exception as e:
        print(f"Voice stress analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
# ============================================
# MOCK / ADDITIONAL DASHBOARD ROUTING
# ============================================
@app.route('/analyze_face', methods=['POST'])
def analyze_face():
    """Mock facial analysis endpoint supporting the webcam dashboard feature"""
    try:
        stress_score = random.randint(15, 85)
        emotion = "distressed" if stress_score > 70 else "neutral" if stress_score > 40 else "happy"
        return jsonify({
            'success': True,
            'stress_score': stress_score,
            'emotion': emotion,
            'combined_stress_score': stress_score,
            'face_emotion': emotion
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/analyze_audio', methods=['POST'])
def analyze_audio():
    """Mock audio analysis endpoint"""
    try:
        stress_score = random.randint(20, 80)
        emotion = "neutral"
        return jsonify({
            'success': True,
            'transcript': "Hello",
            'speech_emotion': emotion,
            'speech_score': stress_score,
            'text_risk': 'green'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
# ============================================
# GUIDED DOCTOR SURVEY / INTAKE ENDPOINTS
# ============================================
INTAKE_QUESTIONS = [
    {'id': 1, 'text': "How would you rate your overall mood today on a scale of 1-10?"},
    {'id': 2, 'text': "Have you been experiencing any trouble sleeping lately?"},
    {'id': 3, 'text': "How has your appetite been over the past few days?"},
    {'id': 4, 'text': "Have you felt more anxious or worried than usual?"},
    {'id': 5, 'text': "Is there anything specific that's been bothering you?"}
]
intake_sessions = {}
@app.route('/start_intake', methods=['POST'])
def start_intake():
    session_id = str(uuid.uuid4())
    intake_sessions[session_id] = {
        'current_question_index': 0,
        'answers': {},
        'started_at': time.time()
    }
    return jsonify({
        'first_question': INTAKE_QUESTIONS[0],
        'session_id': session_id
    })
@app.route('/next_question', methods=['GET'])
def next_question():
    session_id = request.args.get('session_id', 'default')
    if session_id not in intake_sessions:
        return jsonify({'done': True})
    
    session = intake_sessions[session_id]
    next_index = session['current_question_index']
    
    if next_index >= len(INTAKE_QUESTIONS):
        return jsonify({'done': True})
    
    return jsonify({
        'question': INTAKE_QUESTIONS[next_index],
        'done': False
    })
@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    data = request.json
    question_id = data.get('question_id')
    answer = data.get('answer', '')
    session_id = data.get('session_id', 'default')
    
    if session_id not in intake_sessions:
        session_id = 'default'
        if 'default' not in intake_sessions:
            intake_sessions['default'] = {
                'current_question_index': 0,
                'answers': {},
                'started_at': time.time()
            }
            
    session = intake_sessions[session_id]
    session['answers'][question_id] = answer
    session['current_question_index'] += 1
    
    # Generate supportive response via LLM
    question_idx = int(question_id) - 1
    question_text = INTAKE_QUESTIONS[question_idx]['text'] if 0 <= question_idx < len(INTAKE_QUESTIONS) else "Question"
    
    prompt = f"The user is undergoing a mental health intake survey. The question was: '{question_text}'. The user answered: '{answer}'. Provide a short, highly supportive and empathetic feedback sentence."
    reply, _ = query_sarvam_llm(prompt, 'en')
    # Urgency check
    urgent = False
    urgent_message = None
    urgent_keywords = ['suicide', 'kill', 'die', 'harm', 'hopeless', 'worthless']
    if any(w in answer.lower() for w in urgent_keywords):
        urgent = True
        urgent_message = "I am deeply concerned about what you shared. Please contact a mental health professional or call a crisis hotline immediately. You are not alone."
    next_question_index = session['current_question_index']
    next_q = INTAKE_QUESTIONS[next_question_index] if next_question_index < len(INTAKE_QUESTIONS) else None
    return jsonify({
        'reply': reply,
        'urgent': urgent,
        'urgent_message': urgent_message,
        'next_question': next_q,
        'done': next_q is None
    })
# ============================================
# DATABASE ACCESS ENDPOINTS
# ============================================
@app.route('/get_history', methods=['GET'])
def get_history():
    history = load_history()
    return jsonify({
        'success': True,
        'history': history[-20:]
    })
@app.route('/get_stress_data', methods=['GET'])
def get_stress_data():
    logs = load_stress_data()
    if logs:
        total_stress = sum(log.get('stress_score', 0) for log in logs)
        avg_stress = round(total_stress / len(logs))
    else:
        avg_stress = 0
    return jsonify({
        'success': True,
        'average_stress': avg_stress,
        'logs': logs[-10:] if logs else [],
        'total_logs': len(logs)
    })
# ============================================
# AUTHENTICATION MOCKS
# ============================================
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': {
            'name': email.split('@')[0] if email else 'User',
            'email': email,
            'age': 25,
            'location': 'India'
        }
    })
@app.route('/register', methods=['POST'])
def register():
    return jsonify({
        'success': True,
        'message': 'Registration successful'
    })
# ============================================
# STATIC AND DOCK ROUTING
# ============================================
@app.route('/home')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    return send_from_directory('.', 'login 2.html')
# ============================================
# MAIN APPLICATION BOOT
# ============================================
if __name__ == '__main__':
    print("\n" + "="*60)
    print("[MindMate] CONSOLIDATED LLM MULTILINGUAL SYSTEM")
    print("="*60)
    print(f"[TTS] gTTS Available: {GTTS_AVAILABLE}")
    print(f"[AI]  Sarvam SDK: {'Available' if SARVAM_SDK_AVAILABLE else 'REST Mode (Fallback)'}")
    print("\n[SERVER] Launching at: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
