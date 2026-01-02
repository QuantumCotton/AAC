#!/usr/bin/env python3
"""
Generate assets for priority animals only
"""

import os
import json
import requests
import time
import base64
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_monolingual_v1")

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_MODEL = os.getenv("STABILITY_MODEL", "stable-diffusion-xl-1024-v1-0")

# Priority animals - 2-3 per category for initial launch
PRIORITY_ANIMALS = [
    # Farm
    {"name": "Cow", "category": "Farm"},
    {"name": "Pig", "category": "Farm"},
    {"name": "Chicken", "category": "Farm"},
    
    # Domestic
    {"name": "Dog", "category": "Domestic"},
    {"name": "Cat", "category": "Domestic"},
    {"name": "Hamster", "category": "Domestic"},
    
    # Forest
    {"name": "Deer", "category": "Forest"},
    {"name": "Fox", "category": "Forest"},
    {"name": "Owl", "category": "Forest"},
    
    # Jungle
    {"name": "Lion", "category": "Jungle"},
    {"name": "Elephant", "category": "Jungle"},
    {"name": "Monkey", "category": "Jungle"},
    
    # Nocturnal
    {"name": "Bat", "category": "Nocturnal"},
    {"name": "Raccoon", "category": "Nocturnal"},
    {"name": "Firefly", "category": "Nocturnal"},
    
    # Arctic
    {"name": "Polar Bear", "category": "Arctic"},
    {"name": "Penguin", "category": "Arctic"},
    {"name": "Seal", "category": "Arctic"},
    
    # Shallow Water
    {"name": "Dolphin", "category": "Shallow Water"},
    {"name": "Turtle", "category": "Shallow Water"},
    {"name": "Crab", "category": "Shallow Water"},
    
    # Coral Reef
    {"name": "Clownfish", "category": "Coral Reef"},
    {"name": "Starfish", "category": "Coral Reef"},
    {"name": "Octopus", "category": "Coral Reef"},
    
    # Deep Sea
    {"name": "Anglerfish", "category": "Deep Sea"},
    {"name": "Jellyfish", "category": "Deep Sea"},
    {"name": "Squid", "category": "Deep Sea"},
    
    # Ultra Deep Sea
    {"name": "Giant Squid", "category": "Ultra Deep Sea"},
    {"name": "Sea Cucumber", "category": "Ultra Deep Sea"},
]

def slugify(name: str) -> str:
    """Convert animal name to URL-friendly slug."""
    return name.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')

def retry_with_backoff(func, *args, max_retries=3, base_delay=2, **kwargs):
    """Retry function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            result = func(*args, **kwargs)
            if result:
                return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
        
        if attempt < max_retries - 1:
            delay = base_delay * (2 ** attempt)
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)
    
    return False

def generate_audio(text: str, output_path: Path) -> bool:
    """Generate audio using ElevenLabs API."""
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
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
        return True
    elif response.status_code == 429:
        print(f"Rate limited for {output_path.name}")
        return False
    else:
        print(f"❌ Audio generation failed for {output_path.name}: {response.status_code}")
        return False

def generate_image(prompt: str, output_path: Path) -> bool:
    """Generate image using Stability AI."""
    url = f"https://api.stability.ai/v1/generation/{STABILITY_MODEL}/text-to-image"
    
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    body = {
        "text_prompts": [
            {
                "text": prompt,
                "weight": 1
            }
        ],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30
    }
    
    response = requests.post(url, json=body, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        image_data = data["artifacts"][0]["base64"]
        image_bytes = base64.b64decode(image_data)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        return True
    else:
        print(f"❌ Image generation failed for {output_path.name}: {response.status_code}")
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
    """Generate priority assets."""
    print("🎨 Generating Priority Assets for Liora...")
    print(f"📊 Processing {len(PRIORITY_ANIMALS)} priority animals")
    
    # Create directories
    base_dir = Path(__file__).parent.parent
    assets_dir = base_dir / "public" / "assets"
    
    dirs = [
        assets_dir / "images" / "toy_mode",
        assets_dir / "images" / "real_mode",
        assets_dir / "audio" / "names",
        assets_dir / "audio" / "facts",
    ]
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Process each animal
    success_count = 0
    for i, animal in enumerate(PRIORITY_ANIMALS):
        animal_id = slugify(animal["name"])
        print(f"\n🦁 [{i+1}/{len(PRIORITY_ANIMALS)}] Processing: {animal['name']}")
        
        # Load facts
        facts = load_facts_for_animal(animal["name"])
        
        # Generate audio with retry
        name_text = f"{animal['name']}! Starts with {animal['name'][0]}."
        
        if retry_with_backoff(generate_audio, name_text, assets_dir / "audio" / "names" / f"{animal_id}_name.mp3"):
            print(f"✅ Name audio: {animal['name']}")
        
        # Generate fact audio if available
        if facts:
            if 'fact_level_1' in facts and retry_with_backoff(generate_audio, facts['fact_level_1'], assets_dir / "audio" / "facts" / f"{animal_id}_fact_simple.mp3"):
                print(f"✅ Simple fact audio: {animal['name']}")
            
            if 'fact_level_2' in facts:
                detailed_fact = f"Size: {facts['fact_level_2']['size_details']}. {facts['fact_level_2']['unique_fact']}. Habitat: {facts['fact_level_2']['habitat']}."
                if retry_with_backoff(generate_audio, detailed_fact, assets_dir / "audio" / "facts" / f"{animal_id}_fact_detailed.mp3"):
                    print(f"✅ Detailed fact audio: {animal['name']}")
        
        # Generate images with Stability AI
        toy_prompt = f"Realistic {animal['name']}, friendly gentle expression, cute cartoon style with rounded features, big friendly eyes, educational children's book illustration style, white background isolated, no text, suitable for kids aged 3-8, professional illustration quality"
        real_prompt = f"Realistic {animal['name']}, photorealistic but soft lighting, educational children's book illustration style, white background isolated, no text, suitable for kids aged 3-8, professional illustration quality"
        
        # Check if we have enough credits
        if STABILITY_API_KEY:
            # Check balance first
            balance_url = "https://api.stability.ai/v1/user/balance"
            balance_headers = {"Authorization": f"Bearer {STABILITY_API_KEY}"}
            balance_response = requests.get(balance_url, headers=balance_headers)
            
            if balance_response.status_code == 200:
                credits = balance_response.json()['credits']
                if credits >= 6:  # Need 6 credits for 2 images
                    if generate_image(toy_prompt, assets_dir / "images" / "toy_mode" / f"{animal_id}.webp"):
                        print(f"✅ Toy image: {animal['name']}")
                    if generate_image(real_prompt, assets_dir / "images" / "real_mode" / f"{animal_id}.webp"):
                        print(f"✅ Real image: {animal['name']}")
                else:
                    print(f"⚠️ Low credits ({credits}), skipping images for {animal['name']}")
            else:
                print(f"⚠️ Could not check balance, skipping images")
        
        success_count += 1
        time.sleep(3)  # Conservative delay between animals
    
    print("\n✅ Priority generation complete!")
    print(f"📊 Processed: {success_count}/{len(PRIORITY_ANIMALS)} animals")
    print(f"📁 Check {assets_dir} for generated files")

if __name__ == "__main__":
    main()
