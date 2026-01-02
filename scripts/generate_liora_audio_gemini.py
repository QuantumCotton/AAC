#!/usr/bin/env python3
"""
Generate natural speech audio for Liora AAC using Google Gemini 2.0 TTS.
Testing the new December 2025 Gemini audio generation capabilities.
"""

import os
import json
import time
import base64
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

BASE_DIR = Path(__file__).parent.parent
AUDIO_OUTPUT_DIR = BASE_DIR / "public" / "assets" / "audio" / "liora_gemini"
SYMBOLS_FILE = BASE_DIR / "src" / "data" / "liora_symbols_full.json"

def ensure_dirs():
    """Create output directories."""
    (AUDIO_OUTPUT_DIR / "en").mkdir(parents=True, exist_ok=True)
    (AUDIO_OUTPUT_DIR / "tl").mkdir(parents=True, exist_ok=True)

def generate_audio_gemini(text: str, output_path: Path, language: str = "en") -> bool:
    """Generate audio using Gemini 2.0 TTS API."""
    if output_path.exists():
        print(f"  ⏭️  Skipping (exists): {output_path.name}")
        return True
    
    try:
        # Use Gemini 2.0 Flash with audio output
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Create a prompt for TTS
        lang_instruction = "Filipino/Tagalog" if language == "tl" else "English"
        prompt = f"""Generate natural, child-friendly speech audio for this word/phrase.
Speak clearly and warmly like talking to a young child.
Language: {lang_instruction}
Word to speak: "{text}"

Please generate the audio output for this word."""

        # Generate with audio modality
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_modalities=["audio"],
            )
        )
        
        # Check if we got audio back
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # Save the audio data
                        audio_data = base64.b64decode(part.inline_data.data)
                        with open(output_path, "wb") as f:
                            f.write(audio_data)
                        print(f"  ✅ Generated: {output_path.name}")
                        return True
        
        print(f"  ⚠️  No audio in response for: {text}")
        return False
        
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

def main():
    print("🎙️ Liora AAC Audio Generator (Gemini 2.0 TTS)")
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
    
    print(f"\n📊 Testing with Core Words category ({len(core_category['symbols'])} symbols)")
    print("=" * 50)
    
    generated = 0
    failed = 0
    
    for symbol in core_category["symbols"][:10]:  # Test first 10 only
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
        
        # Tagalog
        tl_path = AUDIO_OUTPUT_DIR / "tl" / f"{symbol_id}.mp3"
        if generate_audio_gemini(text_tl, tl_path, "tl"):
            generated += 1
        else:
            failed += 1
        
        # Small delay
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print(f"✅ Generated: {generated}")
    print(f"❌ Failed: {failed}")
    print(f"📂 Output: {AUDIO_OUTPUT_DIR}")

if __name__ == "__main__":
    main()
