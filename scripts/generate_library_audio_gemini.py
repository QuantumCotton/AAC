#!/usr/bin/env python3
"""
Generate high-quality narration audio for Liora's Library using Google Gemini 2.5 Pro TTS.
This is for the Discovery Mode mini-books - pre-cached for offline playback.
"""

import os
import json
import time
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

BASE_DIR = Path(__file__).parent.parent
AUDIO_OUTPUT_DIR = BASE_DIR / "public" / "assets" / "audio" / "library"

# Gemini 2.5 Pro TTS endpoint (December 2025)
GEMINI_TTS_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-tts:generateContent?key={GOOGLE_API_KEY}"

# Sample library books for testing
LIBRARY_BOOKS = {
    "black_holes": {
        "title": "Black Holes",
        "pages": [
            "Black holes are regions in space where gravity is so strong that nothing can escape, not even light!",
            "They form when massive stars collapse at the end of their lives. The star's core squeezes into a tiny point.",
            "The boundary around a black hole is called the event horizon. Once you cross it, there's no coming back!",
            "Time moves slower near a black hole due to its intense gravity. This is called time dilation.",
            "Scientists detect black holes by observing how they affect nearby stars and gas. They can't see the black hole directly!"
        ]
    },
    "dinosaurs": {
        "title": "Dinosaurs",
        "pages": [
            "Dinosaurs lived on Earth for over 160 million years! That's much longer than humans have been around.",
            "The word dinosaur means 'terrible lizard' in Greek. But they weren't actually lizards at all!",
            "Some dinosaurs were as small as chickens, while others were absolutely enormous - bigger than buildings!",
            "Many scientists believe birds evolved from small dinosaurs. So in a way, dinosaurs are still alive today!",
            "Dinosaurs went extinct about 66 million years ago after a giant asteroid hit Earth."
        ]
    },
    "ocean": {
        "title": "The Ocean",
        "pages": [
            "The ocean covers more than 70% of Earth's surface. That's a lot of water!",
            "The deepest part of the ocean is the Mariana Trench - over 36,000 feet deep. That's deeper than Mount Everest is tall!",
            "Coral reefs are like underwater cities, home to millions of colorful sea creatures.",
            "Whales are the largest animals ever to live on Earth - even bigger than the dinosaurs!",
            "The ocean produces over half of the world's oxygen through tiny plants called phytoplankton."
        ]
    }
}

def ensure_dirs():
    """Create output directories."""
    AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for book_id in LIBRARY_BOOKS.keys():
        (AUDIO_OUTPUT_DIR / book_id).mkdir(parents=True, exist_ok=True)

def generate_narration(text: str, output_path: Path, voice: str = "Aoede") -> bool:
    """Generate narration audio using Gemini 2.5 Pro TTS."""
    if output_path.exists():
        print(f"  ⏭️  Skipping (exists): {output_path.name}")
        return True
    
    try:
        # Gemini 2.5 Pro TTS request format
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Read this text in a warm, engaging, child-friendly storytelling voice. Make it sound exciting and educational:\n\n{text}"
                }]
            }],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {
                            "voiceName": voice
                        }
                    }
                }
            }
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(GEMINI_TTS_URL, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "inlineData" in part:
                            audio_data = base64.b64decode(part["inlineData"]["data"])
                            
                            with open(output_path, "wb") as f:
                                f.write(audio_data)
                            print(f"  ✅ Generated: {output_path.name} ({len(audio_data)} bytes)")
                            return True
            
            print(f"  ⚠️  No audio in response")
            return False
        else:
            error_text = response.text[:300]
            print(f"  ❌ Error {response.status_code}: {error_text}")
            return False
        
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

def main():
    print("📚 Liora's Library Audio Generator (Gemini 2.5 Pro TTS)")
    print("=" * 60)
    
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_GEMINI_API_KEY not found in .env")
        return
    
    ensure_dirs()
    
    print(f"\n📊 Found {len(LIBRARY_BOOKS)} books to narrate")
    
    generated = 0
    failed = 0
    
    for book_id, book in LIBRARY_BOOKS.items():
        print(f"\n📖 Book: {book['title']}")
        
        for i, page_text in enumerate(book["pages"]):
            output_path = AUDIO_OUTPUT_DIR / book_id / f"page_{i+1}.mp3"
            print(f"  Page {i+1}: {page_text[:50]}...")
            
            if generate_narration(page_text, output_path):
                generated += 1
            else:
                failed += 1
            
            time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"✅ Generated: {generated}")
    print(f"❌ Failed: {failed}")
    print(f"📂 Output: {AUDIO_OUTPUT_DIR}")

if __name__ == "__main__":
    main()
