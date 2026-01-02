#!/usr/bin/env python3
"""
Generate audio with interesting facts using templates and the actual facts data
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

def generate_exciting_script(animal_name: str, facts: dict) -> dict:
    """Generate exciting scripts using the actual facts with intonation markers."""
    
    # Get facts
    simple_fact = facts.get('fact_level_1', f"I'm a special {animal_name}!")
    size = facts.get('fact_level_2', {}).get('size_details', '')
    unique = facts.get('fact_level_2', {}).get('unique_fact', '')
    habitat = facts.get('fact_level_2', {}).get('habitat', '')
    
    # Create exciting variations of the facts
    animal_lower = animal_name.lower()
    
    # Name introductions with excitement
    name_intros = [
        f"{animal_name.upper()}! Starts with {animal_name[0]}!",
        f"WOW! It's a {animal_name.upper()}! Starts with {animal_name[0]}!",
        f"LOOK! A {animal_name.upper()}! Can you say {animal_name}?",
        f"AMAZING {animal_name.upper()}! Starts with {animal_name[0]}!",
    ]
    
    # Transform simple facts into exciting statements
    simple_variations = [
        f"WOW! {simple_fact.upper()}!",
        f"GUESS WHAT? {simple_fact.upper()}!",
        f"AMAZING! {simple_fact.upper()}!",
        f"LISTEN TO THIS! {simple_fact.upper()}!",
        f"INCREDIBLE! {simple_fact.upper()}!",
    ]
    
    # Build detailed script with actual facts
    detailed_parts = []
    
    # Add size fact if available
    if size:
        size_excitement = [
            f"I'm {size.lower()}! That's HUGE!",
            f"Can you believe it? I'm {size.lower()}!",
            f"WOW! I can grow to be {size.lower()}!",
            f"AMAZING! I'm {size.lower()}!",
        ]
        detailed_parts.append(random.choice(size_excitement))
    
    # Add unique fact if available
    if unique:
        unique_excitement = [
            f"And {unique.lower()}! INCREDIBLE!",
            f"PLUS! {unique.lower()}! WOW!",
            f"HERE'S SOMETHING COOL! {unique.lower()}!",
            f"BET YOU DIDN'T KNOW! {unique.lower()}!",
        ]
        detailed_parts.append(random.choice(unique_excitement))
    
    # Add habitat if available
    if habitat:
        habitat_excitement = [
            f"I live in {habitat.lower()}! AMAZING!",
            f"My home is in {habitat.lower()}! COOL!",
            f"You can find me in {habitat.lower()}! WOW!",
            f"I love living in {habitat.lower()}! PERFECT!",
        ]
        detailed_parts.append(random.choice(habitat_excitement))
    
    # If no detailed facts, create something based on animal type
    if not detailed_parts:
        if "fish" in animal_lower or "shark" in animal_lower or "whale" in animal_lower:
            detailed_parts = [
                "I swim SUPER fast in the ocean! WOW!",
                "I have fins and gills to breathe underwater! AMAZING!",
                "I live in the BIG blue ocean! INCREDIBLE!"
            ]
        elif "bird" in animal_lower:
            detailed_parts = [
                "I can FLY high in the sky! WOW!",
                "I have feathers and wings! AMAZING!",
                "I build nests in trees! COOL!"
            ]
        elif "crab" in animal_lower or "lobster" in animal_lower:
            detailed_parts = [
                "I walk SIDEWAYS on the beach! WOW!",
                "I have big claws to pinch! AMAZING!",
                "I live in shells I find! COOL!"
            ]
        else:
            detailed_parts = [
                f"I'm an AMAZING {animal_name}! WOW!",
                f"I have SUPER special powers! INCREDIBLE!",
                f"I'm one of a kind! AMAZING!"
            ]
    
    # Combine with random intros
    detailed_intros = [
        "GUESS WHAT? ",
        "WOW! LET ME TELL YOU! ",
        "AMAZING FACTS ABOUT ME! ",
        "LISTEN TO THIS! ",
        "INCREDIBLE! ",
    ]
    
    detailed_script = random.choice(detailed_intros) + " ".join(detailed_parts)
    
    return {
        "name": random.choice(name_intros),
        "simple": random.choice(simple_variations),
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
    """Generate audio with exciting facts."""
    print("🎤 Generating Audio with EXCITING Facts (No OpenAI Needed)...")
    
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
            
            # Skip if already exists (remove this to regenerate all)
            if f"{animal_id}_name" in existing_audio:
                print(f"  ⏭️ Skipping {animal['name']} - already exists")
                continue
            
            print(f"  🦁 [{batch_start + i + 1}/{len(animals)}] Processing: {animal['name']}")
            
            # Get facts
            animal_facts = facts_lookup.get(animal["name"], {})
            
            # Generate exciting scripts
            print("    🎨 Creating exciting script...")
            scripts = generate_exciting_script(animal["name"], animal_facts)
            
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
