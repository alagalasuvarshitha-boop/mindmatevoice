import pygame
import requests
import os
from tempfile import NamedTemporaryFile

class TTSManager:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.sarvam.ai/text-to-speech"
        pygame.mixer.init()
        
        # Language codes mapping
        self.language_codes = {
            'hi': 'hi-IN',    # Hindi
            'te': 'te-IN',    # Telugu
            'ta': 'ta-IN',    # Tamil
            'kn': 'kn-IN',    # Kannada
            'en': 'en-IN'     # English (if supported)
        }
        
        # Speaker voices (choose appropriate ones)
        self.speakers = {
            'hi': 'anushka',
            'te': 'anushka',
            'ta': 'anushka',
            'kn': 'anushka',
            'en': 'anushka'
        }
    
    def detect_language(self, text):
        """Detect language from text (simplified)"""
        # You can implement proper language detection here
        # For now, check Unicode ranges
        for char in text:
            if '\u0900' <= char <= '\u097F':  # Devanagari (Hindi)
                return 'hi'
            elif '\u0C00' <= char <= '\u0C7F':  # Telugu
                return 'te'
            elif '\u0B80' <= char <= '\u0BFF':  # Tamil
                return 'ta'
            elif '\u0C80' <= char <= '\u0CFF':  # Kannada
                return 'kn'
        return 'en'  # Default to English
    
    def speak(self, text, language_code=None):
        """Convert text to speech and play it"""
        if not text:
            return False
        
        # Auto-detect language if not specified
        if not language_code:
            lang = self.detect_language(text)
            language_code = self.language_codes.get(lang, 'hi-IN')
        
        payload = {
            "text": text,
            "speaker": self.speakers.get(lang, 'anushka'),
            "language_code": language_code,
            "format": "mp3"
        }
        
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.url, json=payload, headers=headers)
            
            if response.status_code == 200:
                # Save to temporary file
                with NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                    temp_file.write(response.content)
                    temp_path = temp_file.name
                
                # Play the audio
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                
                # Clean up temp file
                os.unlink(temp_path)
                return True
            else:
                print(f"TTS Error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"TTS Exception: {e}")
            return False
    
    def speak_multilingual(self, text_with_langs):
        """Speak multiple texts in different languages
        Args:
            text_with_langs: List of tuples [(text, lang_code), ...]
        """
        for text, lang_code in text_with_langs:
            print(f"Speaking: {text} [{lang_code}]")
            self.speak(text, lang_code)
    
    def stop(self):
        """Stop any ongoing speech"""
        pygame.mixer.music.stop()

# Test the TTS Manager
if __name__ == "__main__":
    API_KEY = "sk_rbfhhjja_kwTk67JNNUlveYhmFw4Sb8Db"
    tts = TTSManager(API_KEY)
    
    # Test multilingual speech
    test_phrases = [
        ("नमस्ते, मैं माइंडमेट हूँ", "hi-IN"),
        ("నమస్కారం, నేను మైండ్మేట్ ని", "te-IN"),
        ("வணக்கம், நான் மைண்ட்மேட்", "ta-IN"),
        ("ನಮಸ್ಕಾರ, ನಾನು ಮೈಂಡ್ಮೇಟ್", "kn-IN"),
        ("Hello, I am MindMate", "en-IN")
    ]
    
    for text, lang in test_phrases:
        print(f"\nSpeaking: {text}")
        tts.speak(text, lang)