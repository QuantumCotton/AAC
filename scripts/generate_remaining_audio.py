#!/usr/bin/env python3
"""
Generate audio for animals that don't have it yet
"""

import os
import json
import requests
import time
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_monolingual_v1")

def slugify(name: str) -> str:
    """Convert animal name to URL-friendly slug."""
    return name.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')

def check_existing_audio() -> dict:
    """Check which animals already have audio."""
    audio_dir = Path(__file__).parent.parent / "public" / "assets" / "audio" / "names"
    existing = set()
    if audio_dir.exists():
        for file in audio_dir.glob("*.mp3"):
            existing.add(file.stem)
    return existing

def generate_audio_with_retry(text: str, output_path: Path, max_retries=5) -> bool:
    """Generate audio using ElevenLabs API with retry logic."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ Generated audio: {output_path.name}")
                return True
            elif response.status_code == 429:
                # Rate limited - wait with exponential backoff
                wait_time = 5 * (attempt + 1)  # 5s, 10s, 15s, 20s, 25s
                print(f"⏱️ Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            else:
                print(f"❌ Audio generation failed for {output_path.name}: {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                continue
        except Exception as e:
            print(f"❌ Error generating audio for {output_path.name}: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            continue
    
    return False

def load_facts_for_animal(animal_name: str) -> dict:
    """Load facts for a specific animal."""
    facts_file = Path(__file__).parent.parent / "src/data/facts_clean.json"
    if facts_file.exists():
        with open(facts_file, 'r', encoding='utf-8') as f:
            facts = json.load(f)
            for fact in facts:
                if fact['name'] == animal_name:
                    return fact
    return {}

def main():
    """Generate audio for animals that don't have it."""
    print("🎤 Generating Remaining Animal Audio...")
    
    # Load animals list
    animals_file = Path(__file__).parent.parent / "src/data" / "animals_clean.json"
    with open(animals_file, 'r', encoding='utf-8') as f:
        animals = json.load(f)
    
    # Check existing audio
    existing_audio = check_existing_audio()
    print(f"📊 Found {len(existing_audio)} existing audio files")
    
    # Create directories
    base_dir = Path(__file__).parent.parent
    assets_dir = base_dir / "public" / "assets"
    
    dirs = [
        assets_dir / "audio" / "names",
        assets_dir / "audio" / "facts",
    ]
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Find animals without audio
    to_generate = []
    for animal in animals:
        animal_id = slugify(animal["name"])
        if animal_id not in existing_audio:
            to_generate.append(animal)
    
    print(f"🎯 Need to generate audio for {len(to_generate)} animals")
    
    # Generate audio
    success_count = 0
    for i, animal in enumerate(to_generate):
        animal_id = slugify(animal["name"])
        
        print(f"\n🦁 [{i+1}/{len(to_generate)}] Processing: {animal['name']}")
        
        # Generate name audio
        name_text = f"{animal['name']}! Starts with {animal['name'][0]}."
        
        if generate_audio_with_retry(name_text, assets_dir / "audio" / "names" / f"{animal_id}_name.mp3"):
            success_count += 1
        
        # Load facts and generate fact audio
        facts = load_facts_for_animal(animal["name"])
        if facts:
            if 'fact_level_1' in facts:
                if generate_audio_with_retry(facts['fact_level_1'], assets_dir / "audio" / "facts" / f"{animal_id}_fact_simple.mp3"):
                    success_count += 1
            
            if 'fact_level_2' in facts:
                detailed_fact = f"Size: {facts['fact_level_2']['size_details']}. {facts['fact_level_2']['unique_fact']}. Habitat: {facts['fact_level_2']['habitat']}."
                if generate_audio_with_retry(detailed_fact, assets_dir / "audio" / "facts" / f"{animal_id}_fact_detailed.mp3"):
                    success_count += 1
        
        # Small delay between animals
        time.sleep(2)
        
        # Check if we should pause briefly (every 10 animals)
        if (i + 1) % 10 == 0:
            print(f"⏸️ Brief pause to avoid rate limits...")
            time.sleep(10)
    
    print("\n✅ Audio generation complete!")
    print(f"📊 Generated audio for {success_count} files")
    print(f"📁 Check {assets_dir / 'audio'} for generated files")

if __name__ == "__main__":
    main()
