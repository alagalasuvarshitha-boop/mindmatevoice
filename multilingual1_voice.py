import os
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()
api_key = os.getenv("SARVAM_API_KEY")
client = SarvamAI(api_key=api_key)

# Language mapping for your UI dropdown
LANGUAGES = {
    "gujarati": "gu-IN",      # Current UI language
    "hindi": "hi-IN",
    "telugu": "te-IN",
    "tamil": "ta-IN",
    "kannada": "kn-IN",
    "english": "en-IN",
    "bengali": "bn-IN",
    "malayalam": "ml-IN",
    "marathi": "mr-IN",
    "punjabi": "pa-IN"
}

def speak_text(text, language_code="gu-IN", speaker="anushka"):
    """Convert text to speech in any Indian language"""
    try:
        audio_response = client.text_to_speech(
            text=text,
            language_code=language_code,
            speaker=speaker,
            model="bulbul:v2"
        )
        
        # Save and play audio
        with open("response.wav", "wb") as f:
            f.write(audio_response.audio_data)
        
        os.system("start response.wav")  # Windows
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def translate_and_speak(english_text, target_lang_code):
    """Translate English to target language and speak"""
    try:
        # Translate
        translation = client.translate(
            input=english_text,
            source_language_code="en-IN",
            target_language_code=target_lang_code,
            model="sarvam-translate:v1"
        )
        
        # Speak the translated text
        return speak_text(translation.translated_text, target_lang_code)
    except Exception as e:
        print(f"Translation error: {e}")
        # Fallback to English
        return speak_text(english_text, "en-IN")