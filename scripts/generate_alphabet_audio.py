#!/usr/bin/env python3
"""
Generate alphabet audio files using Eleven Labs TTS
Generates letter names and phonetic sounds for all 26 letters
"""

import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import requests
from dotenv import load_dotenv

# Load environment variables (ensure we load from project root even when run from scripts/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)

# Configure Eleven Labs
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "UgBBYS2sOqTuMpoF3BR0")  # Mark - neutral American English
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_turbo_v2")  # Supports phoneme tags

# For v3 model, stability must be exactly 0.0, 0.5, or 1.0
stability_env = float(os.getenv("ELEVENLABS_STABILITY", "0.5"))
# Round to nearest allowed value for v3
ELEVENLABS_STABILITY = round(stability_env * 2) / 2
ELEVENLABS_SIMILARITY_BOOST = float(os.getenv("ELEVENLABS_SIMILARITY_BOOST", "0.85"))
ELEVENLABS_STYLE = float(os.getenv("ELEVENLABS_STYLE", "0.0"))
ELEVENLABS_USE_SPEAKER_BOOST = os.getenv("ELEVENLABS_USE_SPEAKER_BOOST", "true").strip().lower() in {"1", "true", "yes"}
ELEVENLABS_OUTPUT_FORMAT = os.getenv("ELEVENLABS_OUTPUT_FORMAT", "mp3_44100_128")

# Alphabet data
ALPHABET = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# Vowels that have long and short sounds
VOWELS = ['A', 'E', 'I', 'O', 'U']

# Phonetic sounds for each letter (default to short letter sounds)
LETTER_SOUNDS = {
    'A': 'ah',
    'B': 'buh',
    'C': 'kuh',
    'D': 'duh',
    'E': 'eh',
    'F': 'fuh',
    'G': 'guh',
    'H': 'huh',
    'I': 'ihh',
    'J': 'juh',
    'K': 'kuh',
    'L': 'luh',
    'M': 'muh',
    'N': 'nuh',
    'O': 'ah',
    'P': 'pih',
    'Q': 'kwuh',
    'R': 'ruh',
    'S': 'suh',
    'T': 'tuh',
    'U': 'uh',
    'V': 'vuh',
    'W': 'wuh',
    'X': 'ks',
    'Y': 'yuh',
    'Z': 'zuh'
}

# Short vowel sounds
VOWEL_SOUNDS_SHORT = {
    'A': 'ah',    # apple
    'E': 'eh',    # egg
    'I': 'ihh',   # igloo
    'O': 'ah',    # octopus
    'U': 'uh'     # umbrella
}

# Long vowel sounds
VOWEL_SOUNDS_LONG = {
    'A': 'ay',    # ape
    'E': 'ee',    # eat
    'I': 'eye',   # ice
    'O': 'oh',    # open
    'U': 'you'    # use
}

# Pronunciation dictionary using phoneme tags for SHORT letter sounds
# Format: <phoneme>pronunciation</phoneme> wrapped in text
PRONUNCIATION_DICTIONARY = {
    'A': '<phoneme="ə">ah</phoneme>',
    'B': '<phoneme="bə">buh</phoneme>',
    'C': '<phoneme="kə">kuh</phoneme>',
    'D': '<phoneme="də">duh</phoneme>',
    'E': '<phoneme="ɛ">eh</phoneme>',
    'F': '<phoneme="fə">fuh</phoneme>',
    'G': '<phoneme="ɡə">guh</phoneme>',
    'H': '<phoneme="hə">huh</phoneme>',
    'I': 'ihh',
    'J': '<phoneme="dʒə">juh</phoneme>',
    'K': '<phoneme="kə">kuh</phoneme>',
    'L': '<phoneme="lə">luh</phoneme>',
    'M': '<phoneme="mə">muh</phoneme>',
    'N': '<phoneme="nə">nuh</phoneme>',
    'O': '<phoneme="ɑ">ah</phoneme>',
    'P': '<phoneme="pə">pih</phoneme>',
    'Q': '<phoneme="kwə">kwuh</phoneme>',
    'R': '<phoneme="ɹ">ruh</phoneme>',
    'S': '<phoneme="sə">suh</phoneme>',
    'T': '<phoneme="tə">tuh</phoneme>',
    'U': '<phoneme="ʌ">uh</phoneme>',
    'V': '<phoneme="və">vuh</phoneme>',
    'W': '<phoneme="wə">wuh</phoneme>',
    'X': '<phoneme="ɛks">ks</phoneme>',
    'Y': '<phoneme="jə">yuh</phoneme>',
    'Z': '<phoneme="zə">zuh</phoneme>'
}


def sanitize_text(text: str) -> str:
    """Clean text for TTS"""
    s = (text or "").replace("\r", " ").replace("\n", " ").replace("\t", " ")
    s = " ".join(s.split())
    return s.strip()


def generate_audio_with_retry(text: str, output_path: Path, max_retries: int = 3) -> bool:
    """Generate audio using Eleven Labs with retry logic."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    
    cleaned_text = sanitize_text(text)
    
    data = {
        "text": cleaned_text,
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": {
            "stability": ELEVENLABS_STABILITY,
            "similarity_boost": ELEVENLABS_SIMILARITY_BOOST,
            "use_speaker_boost": ELEVENLABS_USE_SPEAKER_BOOST,
        },
        "output_format": ELEVENLABS_OUTPUT_FORMAT,
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, headers=headers, timeout=(10, 120))
            
            if response.status_code == 200:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            elif response.status_code == 429:
                wait_time = 3 * (attempt + 1)  # Exponential backoff
                print(f"⏱️ Rate limit. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            elif response.status_code in (400, 401, 402, 403):
                body_text = (response.text or "").strip()
                try:
                    body_json = response.json()
                except Exception:
                    body_json = None
                
                detail_status = None
                if isinstance(body_json, dict):
                    detail = body_json.get("detail")
                    if isinstance(detail, dict):
                        detail_status = detail.get("status")
                
                if detail_status in {
                    "insufficient_credits",
                    "quota_exceeded",
                    "rate_limit_exceeded",
                    "voice_limit_reached",
                    "subscription_required",
                }:
                    raise RuntimeError(f"ELEVENLABS_LIMIT::{detail_status}")
                
                if len(body_text) > 200:
                    body_text = body_text[:200] + "..."
                print(f"❌ Failed: {response.status_code} {body_text}")
                return False
            else:
                body = (response.text or "").strip()
                if body:
                    if len(body) > 200:
                        body = body[:200] + "..."
                    print(f"❌ Failed: {response.status_code} {body}")
                else:
                    print(f"❌ Failed: {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
        except Exception as e:
            print(f"❌ Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
    
    return False


def generate_letter_name_audio(letter: str, output_dir: Path, dry_run: bool = False) -> bool:
    """Generate letter name audio (e.g., 'A', 'B')"""
    filename = f"letter_{letter.lower()}_name.mp3"
    output_path = output_dir / filename
    
    if not dry_run and output_path.exists():
        print(f"  ⏭️ Skipping {letter} name - already exists")
        return True
    
    if dry_run:
        print(f"  📝 Would generate: {letter} -> '{letter}'")
        return True
    
    print(f"  🔤 Generating {letter} name: '{letter}'")
    
    # Special handling for letter I to avoid "one" pronunciation
    text_to_speak = letter
    if letter == 'I':
        text_to_speak = 'ai'  # Phonetically spell it as "eye" sound
    
    if generate_audio_with_retry(text_to_speak, output_path):
        print(f"    ✅ {letter} name: '{text_to_speak}'")
        return True
    return False


def generate_letter_sound_audio(letter: str, output_dir: Path, dry_run: bool = False) -> bool:
    """Generate letter phonetic sound (e.g., 'ah', 'buh')"""
    # For vowels, we generate both long and short sounds
    if letter in VOWELS:
        # Generate short vowel sound
        short_filename = f"letter_{letter.lower()}_sound_short.mp3"
        short_output_path = output_dir / short_filename
        
        if not dry_run and short_output_path.exists():
            print(f"  ⏭️ Skipping {letter} short sound - already exists")
        else:
            if dry_run:
                print(f"  📝 Would generate: {letter} short sound: '{VOWEL_SOUNDS_SHORT[letter]}'")
            else:
                short_sound = VOWEL_SOUNDS_SHORT[letter]
                print(f"  🎵 Generating {letter} short sound: '{short_sound}'")
                if generate_audio_with_retry(short_sound, short_output_path):
                    print(f"    ✅ {letter} short sound: '{short_sound}'")
        
        # Generate long vowel sound
        long_filename = f"letter_{letter.lower()}_sound_long.mp3"
        long_output_path = output_dir / long_filename
        
        if not dry_run and long_output_path.exists():
            print(f"  ⏭️ Skipping {letter} long sound - already exists")
        else:
            if dry_run:
                print(f"  📝 Would generate: {letter} long sound: '{VOWEL_SOUNDS_LONG[letter]}'")
            else:
                long_sound = VOWEL_SOUNDS_LONG[letter]
                print(f"  🎵 Generating {letter} long sound: '{long_sound}'")
                if generate_audio_with_retry(long_sound, long_output_path):
                    print(f"    ✅ {letter} long sound: '{long_sound}'")
        
        return True
    
    # For consonants, generate default sound
    filename = f"letter_{letter.lower()}_sound.mp3"
    output_path = output_dir / filename
    
    if not dry_run and output_path.exists():
        print(f"  ⏭️ Skipping {letter} sound - already exists")
        return True
    
    if dry_run:
        sound_desc = LETTER_SOUNDS.get(letter, letter.lower())
        print(f"  📝 Would generate: {letter} sound: '{sound_desc}'")
        return True
    
    sound_desc = LETTER_SOUNDS.get(letter, letter.lower())
    print(f"  🎵 Generating {letter} sound: '{sound_desc}'")
    
    # Use short sound text directly (no phoneme tags)
    text = sound_desc
    
    if generate_audio_with_retry(text, output_path):
        print(f"    ✅ {letter} sound: '{sound_desc}'")
        return True
    return False


def generate_all_letter_audio(
    letters: List[str],
    output_dir: Path,
    dry_run: bool = False,
    skip_existing: bool = False
) -> Tuple[int, int, int]:
    """Generate audio for all letters."""
    print(f"\n🎤 Generating Alphabet Audio with Eleven Labs...")
    print(f"📚 Letters: {len(letters)}")
    print(f"🎙️ Voice ID: {ELEVENLABS_VOICE_ID}")
    print(f"📊 Model: {ELEVENLABS_MODEL}")
    print(f"🎛️ Stability: {ELEVENLABS_STABILITY}")
    print(f"📈 Similarity Boost: {ELEVENLABS_SIMILARITY_BOOST}")
    
    name_success = 0
    sound_success = 0
    name_total = len(letters)
    sound_total = len(letters)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i, letter in enumerate(letters, 1):
        print(f"\n📝 [{i}/{len(letters)}] Processing: {letter}")
        
        # Generate letter name
        if not skip_existing or not (output_dir / f"letter_{letter.lower()}_name.mp3").exists():
            if generate_letter_name_audio(letter, output_dir, dry_run):
                name_success += 1
            else:
                name_total -= 1
        
        # Generate letter sound
        sound_file_exists = False
        if letter in VOWELS:
            # Check for both long and short sounds
            sound_file_exists = (
                (output_dir / f"letter_{letter.lower()}_sound_short.mp3").exists() and
                (output_dir / f"letter_{letter.lower()}_sound_long.mp3").exists()
            )
        else:
            sound_file_exists = (output_dir / f"letter_{letter.lower()}_sound.mp3").exists()
        
        if not skip_existing or not sound_file_exists:
            if generate_letter_sound_audio(letter, output_dir, dry_run):
                sound_success += 1
            else:
                sound_total -= 1
        
        # Small delay between requests to be nice to the API
        if i < len(letters):
            time.sleep(0.5)
    
    print(f"\n{'='*60}")
    print(f"✅ Complete!")
    print(f"📊 Letter Names: {name_success}/{name_total} generated")
    print(f"📊 Letter Sounds: {sound_success}/{sound_total} generated")
    print(f"📊 Total: {name_success + sound_success}/{name_total + sound_total} files")
    print(f"{'='*60}")
    
    return name_success, sound_success, name_success + sound_success


def main():
    parser = argparse.ArgumentParser(
        description="Generate alphabet audio using Eleven Labs TTS"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate and print only (no Eleven Labs API calls)"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip letters that already have audio files"
    )
    parser.add_argument(
        "--name-only",
        action="store_true",
        help="Only generate letter name audio (skip sounds)"
    )
    parser.add_argument(
        "--sound-only",
        action="store_true",
        help="Only generate letter sound audio (skip names)"
    )
    parser.add_argument(
        "--letters",
        type=str,
        default="ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        help="Letters to generate (default: all 26)"
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Start at specific letter index (1-based)"
    )
    parser.add_argument(
        "--end",
        type=int,
        default=26,
        help="End at specific letter index (1-based)"
    )
    
    args = parser.parse_args()
    
    # Validate API key
    if not ELEVENLABS_API_KEY:
        print("❌ No Eleven Labs API key found in .env")
        print("📝 Please add ELEVENLABS_API_KEY to your .env file")
        return 1
    
    # Parse letters
    letters_to_generate = args.letters.upper()
    
    # Apply range if specified
    if args.start > 1 or args.end < 26:
        letters_to_generate = letters_to_generate[args.start-1:args.end]
    
    print(f"🎯 Letters to generate: {letters_to_generate}")
    
    # Filter based on --name-only or --sound-only
    if args.name_only and not args.sound_only:
        print("📝 Generating letter names only (--name-only)")
        name_only_mode = True
    elif args.sound_only and not args.name_only:
        print("🎵 Generating letter sounds only (--sound-only)")
        name_only_mode = False
    else:
        name_only_mode = None  # Generate both
    
    # Generate audio
    output_dir = PROJECT_ROOT / "public" / "assets" / "audio" / "alphabet"
    
    if name_only_mode is True:
        # Names only
        name_success = 0
        for i, letter in enumerate(letters_to_generate, 1):
            print(f"\n📝 [{i}/{len(letters_to_generate)}] Processing: {letter}")
            if generate_letter_name_audio(letter, output_dir, args.dry_run):
                name_success += 1
            time.sleep(0.5)
        
        print(f"\n✅ Letter Names: {name_success}/{len(letters_to_generate)} generated")
        
    elif name_only_mode is False:
        # Sounds only
        sound_success = 0
        for i, letter in enumerate(letters_to_generate, 1):
            print(f"\n📝 [{i}/{len(letters_to_generate)}] Processing: {letter}")
            if generate_letter_sound_audio(letter, output_dir, args.dry_run):
                sound_success += 1
            time.sleep(0.5)
        
        print(f"\n✅ Letter Sounds: {sound_success}/{len(letters_to_generate)} generated")
        
    else:
        # Both names and sounds
        generate_all_letter_audio(
            letters_to_generate,
            output_dir,
            args.dry_run,
            args.skip_existing
        )
    
    print(f"\n📁 Output directory: {output_dir}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
