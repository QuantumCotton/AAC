#!/usr/bin/env python3
"""
Generate natural speech audio for Liora AAC using ElevenLabs API.
Generates both English and Tagalog audio for all symbols and phrases.
"""

import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "fjnwTZkKtQOJaYzGLa6n")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")

BASE_DIR = Path(__file__).parent.parent
AUDIO_OUTPUT_DIR = BASE_DIR / "public" / "assets" / "audio" / "liora"
SYMBOLS_FILE = BASE_DIR / "src" / "data" / "liora_symbols_full.json"

# Child-friendly voice settings (ElevenLabs v2 API format)
VOICE_SETTINGS = {
    "stability": 0.5,
    "similarity_boost": 0.75
}

def ensure_dirs():
    """Create output directories."""
    (AUDIO_OUTPUT_DIR / "en").mkdir(parents=True, exist_ok=True)
    (AUDIO_OUTPUT_DIR / "tl").mkdir(parents=True, exist_ok=True)
    (AUDIO_OUTPUT_DIR / "phrases" / "en").mkdir(parents=True, exist_ok=True)
    (AUDIO_OUTPUT_DIR / "phrases" / "tl").mkdir(parents=True, exist_ok=True)

def generate_audio(text: str, output_path: Path, language: str = "en") -> bool:
    """Generate audio using ElevenLabs API."""
    if output_path.exists():
        print(f"  ⏭️  Skipping (exists): {output_path.name}")
        return True
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    # Add language hint for Tagalog
    speech_text = text
    if language == "tl":
        # ElevenLabs multilingual model understands language tags
        speech_text = f"<lang xml:lang=\"fil\">{text}</lang>"
    
    data = {
        "text": speech_text,
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": VOICE_SETTINGS
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"  ✅ Generated: {output_path.name}")
            return True
        else:
            print(f"  ❌ Error {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

def generate_symbol_audio(symbol: dict, category_id: str):
    """Generate audio for a single symbol in both languages."""
    symbol_id = symbol["id"]
    text_en = symbol["text"]
    text_tl = symbol.get("text_tl", text_en)
    
    # English
    en_path = AUDIO_OUTPUT_DIR / "en" / f"{symbol_id}.mp3"
    generate_audio(text_en, en_path, "en")
    
    # Tagalog
    tl_path = AUDIO_OUTPUT_DIR / "tl" / f"{symbol_id}.mp3"
    generate_audio(text_tl, tl_path, "tl")
    
    # Small delay to avoid rate limiting
    time.sleep(0.3)

def generate_phrase_audio(phrase: dict):
    """Generate audio for common phrases."""
    phrase_id = phrase["id"]
    text_en = phrase["text"]
    text_tl = phrase.get("text_tl", text_en)
    
    # English
    en_path = AUDIO_OUTPUT_DIR / "phrases" / "en" / f"{phrase_id}.mp3"
    generate_audio(text_en, en_path, "en")
    
    # Tagalog
    tl_path = AUDIO_OUTPUT_DIR / "phrases" / "tl" / f"{phrase_id}.mp3"
    generate_audio(text_tl, tl_path, "tl")
    
    time.sleep(0.3)

def generate_sentence_templates():
    """Generate common sentence templates for the Bridge mode."""
    templates = [
        {"id": "i_want", "en": "I want", "tl": "Gusto ko"},
        {"id": "i_need", "en": "I need", "tl": "Kailangan ko"},
        {"id": "i_feel", "en": "I feel", "tl": "Nararamdaman ko"},
        {"id": "can_i_have", "en": "Can I have", "tl": "Pwede ba akong magkaroon ng"},
        {"id": "please_help", "en": "Please help me", "tl": "Pakitulungan mo ako"},
        {"id": "i_am", "en": "I am", "tl": "Ako ay"},
        {"id": "lets_go", "en": "Let's go", "tl": "Tayo na"},
        {"id": "thank_you", "en": "Thank you", "tl": "Salamat"},
        {"id": "yes_please", "en": "Yes please", "tl": "Oo, paki"},
        {"id": "no_thank_you", "en": "No thank you", "tl": "Hindi, salamat"},
        {"id": "i_love_you", "en": "I love you", "tl": "Mahal kita"},
        {"id": "good_morning", "en": "Good morning", "tl": "Magandang umaga"},
        {"id": "good_night", "en": "Good night", "tl": "Magandang gabi"},
        {"id": "excuse_me", "en": "Excuse me", "tl": "Paumanhin"},
        {"id": "im_sorry", "en": "I'm sorry", "tl": "Patawad"},
        {"id": "my_head_hurts", "en": "My head hurts", "tl": "Masakit ang ulo ko"},
        {"id": "my_tummy_hurts", "en": "My tummy hurts", "tl": "Masakit ang tiyan ko"},
        {"id": "im_hungry", "en": "I'm hungry", "tl": "Gutom ako"},
        {"id": "im_thirsty", "en": "I'm thirsty", "tl": "Uhaw ako"},
        {"id": "im_tired", "en": "I'm tired", "tl": "Pagod ako"},
    ]
    
    print("\n📝 Generating sentence templates...")
    templates_dir = AUDIO_OUTPUT_DIR / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    for t in templates:
        en_path = templates_dir / f"{t['id']}_en.mp3"
        tl_path = templates_dir / f"{t['id']}_tl.mp3"
        
        generate_audio(t["en"], en_path, "en")
        generate_audio(t["tl"], tl_path, "tl")
        time.sleep(0.3)

def main():
    print("🎙️ Liora AAC Audio Generator")
    print("=" * 50)
    
    if not ELEVENLABS_API_KEY:
        print("❌ ELEVENLABS_API_KEY not found in .env")
        return
    
    ensure_dirs()
    
    # Load symbols
    with open(SYMBOLS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    categories = data.get("categories", [])
    common_phrases = data.get("commonPhrases", [])
    
    # Count total
    total_symbols = sum(len(cat["symbols"]) for cat in categories)
    print(f"\n📊 Found {total_symbols} symbols in {len(categories)} categories")
    print(f"📊 Found {len(common_phrases)} common phrases")
    print(f"📊 Will generate ~{(total_symbols + len(common_phrases)) * 2} audio files\n")
    
    # Generate symbol audio
    for cat in categories:
        print(f"\n🏷️  Category: {cat['name']} ({cat['emoji']})")
        for symbol in cat["symbols"]:
            generate_symbol_audio(symbol, cat["id"])
    
    # Generate common phrases
    print("\n💬 Generating common phrases...")
    for phrase in common_phrases:
        generate_phrase_audio(phrase)
    
    # Generate sentence templates
    generate_sentence_templates()
    
    print("\n" + "=" * 50)
    print("✅ Audio generation complete!")
    print(f"📂 Output: {AUDIO_OUTPUT_DIR}")

if __name__ == "__main__":
    main()
