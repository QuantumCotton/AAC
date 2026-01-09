#!/usr/bin/env python3
"""
Generate household item audio using Eleven Labs or OpenAI
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)

# API keys
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Data file
DATA_FILE = PROJECT_ROOT / "src" / "data" / "household_items.json"

# Output directory
OUTPUT_DIR = PROJECT_ROOT / "public" / "assets" / "audio" / "household"

# Eleven Labs voice settings
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel (default child-friendly voice)
MODEL_ID = "eleven_multilingual_v2"

# OpenAI TTS settings
TTS_MODEL = "tts-1"
TTS_VOICE = "alloy"  # alloy, echo, fable, onyx, nova, shimmer


def load_items():
    """Load household items from JSON file"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['items']


def generate_elevenlabs_audio(text: str, output_path: Path) -> bool:
    """Generate audio using Eleven Labs"""
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }
        data = {
            "text": text,
            "model_id": MODEL_ID,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            }
        }
        
        print(f"  🎤 Generating Eleven Labs audio for: {text}")
        response = requests.post(url, json=data, headers=headers, timeout=(10, 120))
        
        if response.status_code == 200:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"    ✅ Saved: {output_path.name}")
            return True
        
        print(f"    ❌ Failed: {response.status_code} - {response.text}")
        return False
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False


def generate_openai_audio(text: str, output_path: Path) -> bool:
    """Generate audio using OpenAI"""
    try:
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "model": TTS_MODEL,
            "voice": TTS_VOICE,
            "input": text,
        }
        
        print(f"  🎤 Generating OpenAI audio for: {text}")
        response = requests.post(url, json=data, headers=headers, timeout=(10, 60))
        
        if response.status_code == 200:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"    ✅ Saved: {output_path.name}")
            return True
        
        print(f"    ❌ Failed: {response.status_code} - {response.text}")
        return False
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False


def generate_audio(text: str, output_path: Path, use_elevenlabs: bool = True) -> bool:
    """Generate audio using available service"""
    if use_elevenlabs and ELEVENLABS_API_KEY:
        return generate_elevenlabs_audio(text, output_path)
    elif OPENAI_API_KEY:
        return generate_openai_audio(text, output_path)
    else:
        print("  ❌ No API key found!")
        return False


def generate_all_audio(items: list, dry_run: bool = False, use_elevenlabs: bool = True) -> dict:
    """Generate audio for all items"""
    results = {"success": 0, "failed": 0, "total": len(items)}
    
    print(f"\n🎤 Generating Household Item Audio")
    print(f"📊 Total items: {len(items)}")
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"🎙️ Service: {'Eleven Labs' if use_elevenlabs and ELEVENLABS_API_KEY else 'OpenAI'}")
    
    if not use_elevenlabs and not OPENAI_API_KEY:
        print("\n❌ No API keys found in .env")
        print("📝 Please add ELEVENLABS_API_KEY or OPENAI_API_KEY to your .env file")
        return results
    
    for i, item in enumerate(items, 1):
        item_name = item['name']
        output_path = OUTPUT_DIR / f"{item['id']}.mp3"
        
        print(f"\n[{i}/{len(items)}] {item_name}")
        
        # Skip if exists
        if not dry_run and output_path.exists():
            print(f"  ⏭️ Skipping - already exists")
            results["success"] += 1
            continue
        
        if dry_run:
            print(f"  📝 Would generate: {item_name} -> {output_path.name}")
            results["success"] += 1
            continue
        
        # Generate audio
        if generate_audio(item_name, output_path, use_elevenlabs):
            results["success"] += 1
        else:
            results["failed"] += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Complete!")
    print(f"📊 Success: {results['success']}/{results['total']}")
    print(f"📊 Failed: {results['failed']}/{results['total']}")
    print(f"{'='*60}")
    
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate household item audio using AI"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate and print only (no API calls)"
    )
    parser.add_argument(
        "--items",
        type=str,
        default="all",
        help="Specific items to generate (comma-separated, or 'all')"
    )
    parser.add_argument(
        "--use-openai",
        action="store_true",
        help="Use OpenAI instead of Eleven Labs"
    )
    
    args = parser.parse_args()
    
    # Load items
    items = load_items()
    
    # Filter if specific items requested
    if args.items != "all":
        requested_ids = [id.strip() for id in args.items.split(",")]
        items = [item for item in items if item['id'] in requested_ids]
    
    # Generate audio
    generate_all_audio(items, args.dry_run, not args.use_openai)


if __name__ == "__main__":
    import sys
    sys.exit(main())
