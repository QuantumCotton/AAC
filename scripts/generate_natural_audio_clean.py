#!/usr/bin/env python3
"""
Generate natural audio without overused excitement words
"""

import os
import json
import time
import random
from pathlib import Path
from typing import Dict, List, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure ElevenLabs
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_monolingual_v1")

def slugify(name: str) -> str:
    """Convert animal name to URL-friendly slug."""
    return name.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')

def create_natural_script(animal_name: str, facts: dict) -> dict:
    """Create natural scripts that let facts speak for themselves."""
    
    # Get facts
    simple_fact = facts.get('fact_level_1', f"I'm a special {animal_name}!")
    size = facts.get('fact_level_2', {}).get('size_details', '')
    unique = facts.get('fact_level_2', {}).get('unique_fact', '')
    habitat = facts.get('fact_level_2', {}).get('habitat', '')
    
    # Name introductions - simple and clear
    name_scripts = [
        f"{animal_name}! Starts with {animal_name[0]}!",
        f"Look! It's a {animal_name}!",
        f"{animal_name}! Can you say {animal_name}?",
        f"That's a {animal_name}!",
    ]
    
    # Simple fact - just state it naturally
    simple_scripts = [
        f"{simple_fact}",
        f"Did you know? {simple_fact}",
        f"Here's something cool: {simple_fact}",
        f"{simple_fact} Pretty neat, right?",
    ]
    
    # Detailed script - combine facts naturally
    detailed_parts = []
    
    # Add size if available
    if size:
        size_phrases = [
            f"I can grow to be {size.lower()}",
            f"I'm about {size.lower()}",
            f"I reach up to {size.lower()}",
        ]
        detailed_parts.append(random.choice(size_phrases))
    
    # Add unique fact if available
    if unique:
        unique_phrases = [
            f"And {unique.lower()}",
            f"Plus, {unique.lower()}",
            f"What's really interesting is {unique.lower()}",
            f"Something special about me is {unique.lower()}",
        ]
        detailed_parts.append(random.choice(unique_phrases))
    
    # Add habitat if available
    if habitat:
        habitat_phrases = [
            f"I live in {habitat.lower()}",
            f"You can find me in {habitat.lower()}",
            f"My home is in {habitat.lower()}",
            f"I make my home in {habitat.lower()}",
        ]
        detailed_parts.append(random.choice(habitat_phrases))
    
    # If no detailed facts, create simple category-based content
    if not detailed_parts:
        animal_lower = animal_name.lower()
        if any(word in animal_lower for word in ["fish", "shark", "whale"]):
            detailed_parts = [
                "I swim through the ocean",
                "I breathe underwater with my gills",
                "The ocean is my home"
            ]
        elif any(word in animal_lower for word in ["bird"]):
            detailed_parts = [
                "I can fly high in the sky",
                "I have feathers to keep me warm",
                "I build nests in trees"
            ]
        else:
            detailed_parts = [
                f"I'm a {animal_name}",
                "I have my own special way of life",
                "I'm unique in my own way"
            ]
    
    # Combine into natural flowing sentences
    if len(detailed_parts) == 1:
        detailed_script = detailed_parts[0] + "."
    elif len(detailed_parts) == 2:
        detailed_script = f"{detailed_parts[0]}, and {detailed_parts[1]}."
    else:
        detailed_script = f"{detailed_parts[0]}. {detailed_parts[1]}, and {detailed_parts[2]}."
    
    return {
        "name": random.choice(name_scripts),
        "simple": random.choice(simple_scripts),
        "detailed": detailed_script
    }

def generate_audio_with_retry(text: str, output_path: Path, max_retries=3) -> bool:
    """Generate audio using ElevenLabs with retry."""
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
                return True
            elif response.status_code == 429:
                wait_time = 3 * (attempt + 1)
                print(f"⏱️ Rate limit. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
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

def main():
    """Generate natural audio without overused excitement words."""
    print("🎤 Generating Natural Audio (Letting Facts Speak for Themselves)...")
    
    # Load data
    animals_file = Path(__file__).parent.parent / "src/data" / "animals_clean.json"
    facts_file = Path(__file__).parent.parent / "src/data" / "facts_clean.json"
    
    with open(animals_file, 'r', encoding='utf-8') as f:
        animals = json.load(f)
    
    with open(facts_file, 'r', encoding='utf-8') as f:
        facts = json.load(f)
    
    facts_lookup = {fact['name']: fact for fact in facts}
    
    # Check existing audio
    existing_audio = set()
    audio_dir = Path(__file__).parent.parent / "public" / "assets" / "audio" / "names"
    if audio_dir.exists():
        existing_audio = {f.stem for f in audio_dir.glob("*.mp3")}
    
    # Process animals in batches of 6
    batch_size = 6
    success_count = 0
    
    for batch_start in range(0, len(animals), batch_size):
        batch_end = min(batch_start + batch_size, len(animals))
        batch = animals[batch_start:batch_end]
        
        print(f"\n📦 Processing batch {batch_start//batch_size + 1}/{(len(animals)-1)//batch_size + 1}")
        
        # Process each animal in batch
        for i, animal in enumerate(batch):
            animal_id = slugify(animal["name"])
            
            # Skip if already exists
            if f"{animal_id}_name" in existing_audio:
                print(f"  ⏭️ Skipping {animal['name']} - already exists")
                continue
            
            print(f"  🦁 [{batch_start + i + 1}/{len(animals)}] Processing: {animal['name']}")
            
            # Get facts
            animal_facts = facts_lookup.get(animal["name"], {})
            
            # Generate natural script
            print("    🎨 Creating natural script...")
            scripts = create_natural_script(animal["name"], animal_facts)
            
            print(f"    📝 {scripts['name']}")
            print(f"    📝 {scripts['simple']}")
            print(f"    📝 {scripts['detailed']}")
            
            # Generate audio files
            assets_dir = Path(__file__).parent.parent / "public" / "assets"
            
            # Name audio
            if generate_audio_with_retry(scripts["name"], assets_dir / "audio" / "names" / f"{animal_id}_name.mp3"):
                print(f"    ✅ Name audio: {animal['name']}")
                success_count += 1
            
            # Simple fact
            if generate_audio_with_retry(scripts["simple"], assets_dir / "audio" / "facts" / f"{animal_id}_fact_simple.mp3"):
                print(f"    ✅ Simple fact: {animal['name']}")
                success_count += 1
            
            # Detailed fact
            if generate_audio_with_retry(scripts["detailed"], assets_dir / "audio" / "facts" / f"{animal_id}_fact_detailed.mp3"):
                print(f"    ✅ Detailed fact: {animal['name']}")
                success_count += 1
        
        # Brief pause between batches
        if batch_end < len(animals):
            print("  ⏸️ Brief pause between batches...")
            time.sleep(1)
    
    print(f"\n✅ Complete! Generated {success_count} audio files")

if __name__ == "__main__":
    main()
