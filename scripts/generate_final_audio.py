#!/usr/bin/env python3
"""
Generate final audio with enhanced fact-based scripts (no OpenAI dependency)
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

def create_exciting_script(animal_name: str, facts: dict) -> dict:
    """Create exciting scripts using facts with enhanced intonation."""
    
    # Get facts
    simple_fact = facts.get('fact_level_1', f"I'm a special {animal_name}!")
    size = facts.get('fact_level_2', {}).get('size_details', '')
    unique = facts.get('fact_level_2', {}).get('unique_fact', '')
    habitat = facts.get('fact_level_2', {}).get('habitat', '')
    
    # Name introductions
    name_scripts = [
        f"{animal_name.upper()}! Starts with {animal_name[0]}!",
        f"WOW! {animal_name.upper()}! Starts with {animal_name[0]}!",
        f"LOOK! {animal_name.upper()}! Can you say {animal_name}?",
        f"AMAZING {animal_name.upper()}! Starts with {animal_name[0]}!",
    ]
    
    # Transform simple fact into exciting statement
    simple_extras = [
        "WOW! ", "AMAZING! ", "GUESS WHAT? ", "INCREDIBLE! ", "LISTEN! "
    ]
    simple_script = random.choice(simple_extras) + simple_fact.upper() + "!"
    
    # Build detailed script with all facts
    detailed_parts = []
    
    # Size fact
    if size:
        size_variations = [
            f"I'm {size.lower()}! THAT'S {random.choice(['HUGE', 'BIG', 'MASSIVE', 'ENORMOUS'])}!",
            f"Can you believe? I'm {size.lower()}! WOW!",
            f"I grow to be {size.lower()}! AMAZING!",
            f"I can be {size.lower()}! INCREDIBLE!",
        ]
        detailed_parts.append(random.choice(size_variations))
    
    # Unique fact
    if unique:
        unique_variations = [
            f"And {unique.lower()}! THAT'S {random.choice(['CRAZY', 'WILD', 'UNBELIEVABLE', 'MIND-BLOWING'])}!",
            f"PLUS! {unique.lower()}! WOW!",
            f"HERE'S SOMETHING {random.choice(['COOL', 'AWESOME', 'FASCINATING'])}! {unique.upper()}!",
            f"BET YOU DIDN'T KNOW! {unique.lower()}! INCREDIBLE!",
        ]
        detailed_parts.append(random.choice(unique_variations))
    
    # Habitat fact
    if habitat:
        habitat_variations = [
            f"I live in {habitat.lower()}! {random.choice(['PERFECT', 'AWESOME', 'GREAT'])} home!",
            f"My home is in {habitat.lower()}! COOL!",
            f"You can find me in {habitat.lower()}! AMAZING!",
            f"I love living in {habitat.lower()}! THE BEST!",
        ]
        detailed_parts.append(random.choice(habitat_variations))
    
    # If no detailed facts, create category-specific content
    if not detailed_parts:
        animal_lower = animal_name.lower()
        if any(word in animal_lower for word in ["fish", "shark", "whale", "dolphin"]):
            detailed_parts = [
                "I swim SUPER fast in the ocean! WOW!",
                "I have fins and gills to breathe! AMAZING!",
                "The ocean is my playground! INCREDIBLE!"
            ]
        elif any(word in animal_lower for word in ["bird", "eagle", "hawk", "owl"]):
            detailed_parts = [
                "I can FLY high in the sky! WOW!",
                "I have feathers and wings! AMAZING!",
                "I can see everything from above! COOL!"
            ]
        elif any(word in animal_lower for word in ["crab", "lobster", "shrimp"]):
            detailed_parts = [
                "I walk sideways on the seafloor! WOW!",
                "I have a hard shell for protection! AMAZING!",
                "I love the ocean floor! PERFECT!"
            ]
        else:
            detailed_parts = [
                f"I'm an AMAZING {animal_name}! WOW!",
                f"I have special powers! INCREDIBLE!",
                f"I'm one of a kind! UNIQUE!"
            ]
    
    # Combine with exciting intro
    detailed_intros = [
        "GUESS WHAT? ",
        "WOW! LET ME TELL YOU! ",
        "AMAZING FACTS! ",
        "LISTEN TO THIS! ",
        "INCREDIBLE! ",
        "BET YOU DIDN'T KNOW! ",
    ]
    
    detailed_script = random.choice(detailed_intros) + " ".join(detailed_parts)
    
    return {
        "name": random.choice(name_scripts),
        "simple": simple_script,
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
    """Generate final audio with enhanced fact-based scripts."""
    print("🎤 Generating FINAL Audio with Enhanced Facts...")
    
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
            
            # Generate exciting script
            print("    🎨 Creating enhanced script...")
            scripts = create_exciting_script(animal["name"], animal_facts)
            
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
