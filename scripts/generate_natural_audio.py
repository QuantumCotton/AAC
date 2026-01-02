#!/usr/bin/env python3
"""
Generate natural audio scripts with Gemini, then create audio files with ElevenLabs
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import google.generativeai as genai
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure APIs
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_monolingual_v1")

genai.configure(api_key=GOOGLE_GEMINI_API_KEY)

def slugify(name: str) -> str:
    """Convert animal name to URL-friendly slug."""
    return name.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')

def generate_natural_script(animal_name: str, facts: dict, model) -> dict:
    """Generate natural, conversational scripts using Gemini."""
    
    prompt = f"""
Create THREE exciting audio scripts for kids about {animal_name}!

Facts to include:
- Simple: {facts.get('fact_level_1', 'No simple fact')}
- Size: {facts.get('fact_level_2', {}).get('size_details', 'No size info')}
- Special: {facts.get('fact_level_2', {}).get('unique_fact', 'No unique fact')}
- Home: {facts.get('fact_level_2', {}).get('habitat', 'No habitat info')}

Make each script different! Use fun words like "Wow!", "Guess what?", "Amazing!".
Keep it simple for 3-8 year olds.

Return JSON:
{{
  "name": "Short intro",
  "simple": "Simple fact with excitement",
  "detailed": "All facts in fun way"
}}

Example:
{{
  "name": "Lion! Starts with L, king of the jungle!",
  "simple": "Wow! I have a big furry mane and I roar super loud to say hi!",
  "detailed": "Guess what? I weigh as much as 50 kids! My roar travels 5 miles! We live in sunny Africa where we nap all day!"
}}
"""

    try:
        response = model.generate_content(prompt)
        script_text = response.text.strip()
        
        # Clean up response
        if script_text.startswith("```json"):
            script_text = script_text[7:]
        if script_text.endswith("```"):
            script_text = script_text[:-3]
        
        scripts = json.loads(script_text)
        return scripts
    except Exception as e:
        print(f"⚠️ Using fallback for {animal_name}")
        return {
            "name": f"{animal_name}! Starts with {animal_name[0]}!",
            "simple": facts.get('fact_level_1', f"I'm a {animal_name}!"),
            "detailed": f"I'm a {animal_name}! {facts.get('fact_level_2', {}).get('unique_fact', '')}"
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
                wait_time = 5 * (attempt + 1)
                print(f"⏱️ Rate limit. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                print(f"❌ Failed: {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                continue
        except Exception as e:
            print(f"❌ Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
            continue
    
    return False

def main():
    """Generate natural audio for all animals."""
    print("🎤 Generating Natural Audio with Gemini + ElevenLabs...")
    
    # Initialize models
    gemini_model = genai.GenerativeModel('gemini-2.5-flash')
    
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
    
    # Process animals
    success_count = 0
    for i, animal in enumerate(animals):
        animal_id = slugify(animal["name"])
        
        # Skip if already exists
        if f"{animal_id}_name" in existing_audio:
            print(f"⏭️ Skipping {animal['name']} - already exists")
            continue
        
        print(f"\n🦁 [{i+1}/{len(animals)}] Processing: {animal['name']}")
        
        # Get facts
        animal_facts = facts_lookup.get(animal["name"], {})
        
        # Generate natural scripts
        print("📝 Writing scripts...")
        scripts = generate_natural_script(animal["name"], animal_facts, gemini_model)
        
        # Generate audio files
        assets_dir = Path(__file__).parent.parent / "public" / "assets"
        
        # Name audio
        if generate_audio_with_retry(scripts["name"], assets_dir / "audio" / "names" / f"{animal_id}_name.mp3"):
            print(f"✅ Name audio: {animal['name']}")
            success_count += 1
        
        # Simple fact
        if generate_audio_with_retry(scripts["simple"], assets_dir / "audio" / "facts" / f"{animal_id}_fact_simple.mp3"):
            print(f"✅ Simple fact: {animal['name']}")
            success_count += 1
        
        # Detailed fact
        if generate_audio_with_retry(scripts["detailed"], assets_dir / "audio" / "facts" / f"{animal_id}_fact_detailed.mp3"):
            print(f"✅ Detailed fact: {animal['name']}")
            success_count += 1
        
        # Brief pause every 3 animals (rate limit)
        if (i + 1) % 3 == 0:
            print("⏸️ Brief pause...")
            time.sleep(5)
    
    print(f"\n✅ Complete! Generated {success_count} audio files")

if __name__ == "__main__":
    main()
