#!/usr/bin/env python3
"""
Test script for ElevenLabs audio generation
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_monolingual_v1")

def test_audio_generation():
    """Test generating audio with ElevenLabs API"""
    if not ELEVENLABS_API_KEY:
        print("❌ No ElevenLabs API key found in .env")
        return False
    
    print("🎤 Testing ElevenLabs audio generation...")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    
    test_text = "Hello! I am a lion from the African savanna. I have a big mane and I roar loudly!"
    
    data = {
        "text": test_text,
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            # Save test audio
            output_dir = Path("test_output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / "test_lion.mp3"
            
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            print(f"✅ Success! Audio saved to {output_path}")
            print(f"📊 File size: {output_path.stat().st_size} bytes")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_voice_info():
    """Test getting voice info from ElevenLabs"""
    if not ELEVENLABS_API_KEY:
        return
    
    print("\n🔍 Getting available voices...")
    
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            voices = response.json()
            rachel_voice = next((v for v in voices['voices'] if v['voice_id'] == ELEVENLABS_VOICE_ID), None)
            if rachel_voice:
                print(f"✅ Found voice: {rachel_voice['name']}")
            else:
                print(f"⚠️ Voice ID {ELEVENLABS_VOICE_ID} not found")
        else:
            print(f"❌ Error getting voices: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception getting voices: {e}")

if __name__ == "__main__":
    test_voice_info()
    test_audio_generation()
