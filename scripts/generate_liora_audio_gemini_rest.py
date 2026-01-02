#!/usr/bin/env python3
"""
Generate natural speech audio for Liora AAC using Google Gemini 2.0 TTS via REST API.
Testing the new December 2025 Gemini audio generation capabilities.
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
AUDIO_OUTPUT_DIR = BASE_DIR / "public" / "assets" / "audio" / "liora_gemini"
SYMBOLS_FILE = BASE_DIR / "src" / "data" / "liora_symbols_full.json"

# Gemini 2.0 Flash with audio output endpoint
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GOOGLE_API_KEY}"

def ensure_dirs():
    """Create output directories."""
    (AUDIO_OUTPUT_DIR / "en").mkdir(parents=True, exist_ok=True)
    (AUDIO_OUTPUT_DIR / "tl").mkdir(parents=True, exist_ok=True)

def generate_audio_gemini(text: str, output_path: Path, language: str = "en") -> bool:
    """Generate audio using Gemini 2.0 TTS REST API."""
    if output_path.exists():
        print(f"  ⏭️  Skipping (exists): {output_path.name}")
        return True
    
    try:
        lang_instruction = "Filipino/Tagalog" if language == "tl" else "English"
        
        # Request with audio output modality
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Please speak this word clearly and warmly, as if talking to a young child learning to communicate. Speak in {lang_instruction}. The word is: \"{text}\""
                }]
            }],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {
                            "voiceName": "Aoede"  # Child-friendly voice
                        }
                    }
                }
            }
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract audio from response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "inlineData" in part:
                            audio_data = base64.b64decode(part["inlineData"]["data"])
                            mime_type = part["inlineData"].get("mimeType", "audio/mp3")
                            
                            # Determine file extension
                            ext = ".wav" if "wav" in mime_type else ".mp3"
                            final_path = output_path.with_suffix(ext)
                            
                            with open(final_path, "wb") as f:
                                f.write(audio_data)
                            print(f"  ✅ Generated: {final_path.name} ({len(audio_data)} bytes)")
                            return True
            
            print(f"  ⚠️  No audio in response: {json.dumps(result)[:200]}")
            return False
        else:
            error_text = response.text[:300]
            print(f"  ❌ Error {response.status_code}: {error_text}")
            return False
        
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

def main():
    print("🎙️ Liora AAC Audio Generator (Gemini 2.0 TTS REST)")
    print("=" * 50)
    
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_GEMINI_API_KEY not found in .env")
        return
    
    ensure_dirs()
    
    # Load symbols
    with open(SYMBOLS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Just test with Core Words category first
    core_category = data["categories"][0]  # Core Words
    
    print(f"\n📊 Testing with Core Words ({len(core_category['symbols'])} symbols)")
    print(f"🔑 API Key: {GOOGLE_API_KEY[:20]}...")
    print("=" * 50)
    
    generated = 0
    failed = 0
    
    # Test first 5 symbols
    for symbol in core_category["symbols"][:5]:
        symbol_id = symbol["id"]
        text_en = symbol["text"]
        text_tl = symbol.get("text_tl", text_en)
        
        print(f"\n🔊 {text_en} / {text_tl}")
        
        # English
        en_path = AUDIO_OUTPUT_DIR / "en" / f"{symbol_id}.mp3"
        if generate_audio_gemini(text_en, en_path, "en"):
            generated += 1
        else:
            failed += 1
        
        time.sleep(1)
        
        # Tagalog
        tl_path = AUDIO_OUTPUT_DIR / "tl" / f"{symbol_id}.mp3"
        if generate_audio_gemini(text_tl, tl_path, "tl"):
            generated += 1
        else:
            failed += 1
        
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print(f"✅ Generated: {generated}")
    print(f"❌ Failed: {failed}")
    print(f"📂 Output: {AUDIO_OUTPUT_DIR}")

if __name__ == "__main__":
    main()
