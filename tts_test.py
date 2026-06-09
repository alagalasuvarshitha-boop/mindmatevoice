import requests
import pygame
import os
import time

# Your API setup
API_KEY = "your_api_key"  # Replace with your actual key
url = "https://api.sarvam.ai/text-to-speech"

# Test data
tests = [
    ("Hindi", "नमस्ते, आप कैसे हैं?"),
    ("Telugu", "నమస్కారం, ఎలా ఉన్నారు?"),
    ("Tamil", "வணக்கம், எப்படி இருக்கிறீர்கள்?"),
    ("Kannada", "ನಮಸ್ಕಾರ, ನೀವು ಹೇಗಿದ್ದೀರಿ?")
]

print("==================================================")
print("SARVAM TTS TEST")
print("==================================================\n")

for language, text in tests:
    print(f"\n--- {language} ---")
    print(f"Text: {text}")
    print(f"Generating speech for: {text}...")
    
    # Prepare API request
    payload = {
        "text": text,
        "speaker": "anushka",
        "language_code": "hi-IN"  # Adjust as needed
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Make API call
    response = requests.post(url, headers=headers, json=payload)
    
    # Save as WAV
    with open("response.wav", "wb") as f:
        f.write(response.content)
    
    print("✅ Audio saved to response.wav")
    
    # Play with default player
    print(f"Playing {language}...")
    os.startfile("response.wav")
    time.sleep(4)  # Wait for playback

print("\n✅ All tests complete!")