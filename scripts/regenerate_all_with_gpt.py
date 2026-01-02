#!/usr/bin/env python3
"""
Delete all existing audio and regenerate everything with GPT
"""

import os
import json
import time
import shutil
from pathlib import Path
from typing import Dict, List, Any
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure APIs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_monolingual_v1")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def slugify(name: str) -> str:
    """Convert animal name to URL-friendly slug."""
    return name.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')

def delete_all_audio():
    """Delete all existing audio files."""
    print("🗑️ Deleting all existing audio files...")
    
    audio_dirs = [
        Path(__file__).parent.parent / "public" / "assets" / "audio" / "names",
        Path(__file__).parent.parent / "public" / "assets" / "audio" / "facts",
    ]
    
    deleted_count = 0
    for audio_dir in audio_dirs:
        if audio_dir.exists():
            for file in audio_dir.glob("*.mp3"):
                file.unlink()
                deleted_count += 1
            print(f"  Deleted {len(list(audio_dir.glob('*.mp3')))} files from {audio_dir.name}")
    
    print(f"✅ Deleted {deleted_count} audio files")
    return deleted_count

def generate_gpt_script(animal_name: str, facts: dict) -> dict:
    """Generate exciting scripts using GPT."""
    
    # Get facts
    simple_fact = facts.get('fact_level_1', f"I'm a special {animal_name}!")
    size = facts.get('fact_level_2', {}).get('size_details', '')
    unique = facts.get('fact_level_2', {}).get('unique_fact', '')
    habitat = facts.get('fact_level_2', {}).get('habitat', '')
    
    # Create prompt for GPT
    prompt = f"""
Create THREE exciting audio scripts for kids aged 3-8 about a {animal_name}.

Facts to work with:
- Simple: {simple_fact}
- Size: {size}
- Special: {unique}
- Home: {habitat}

IMPORTANT: Add these intonation markers for ElevenLabs to make it animated:
- Use ! for excitement
- Use ... for pauses
- Use ALL CAPS for emphasis on key words
- Use ? for questions
- Keep sentences SHORT and punchy
- Make it sound like a fun cartoon character

RULES:
1. Transform the facts into something AMAZING and SURPRISING!
2. For simple script: focus on the MOST interesting fact
3. For detailed script: combine facts into a WOW moment
4. Make kids go "WOW I didn't know that!"

Format as JSON:
{{
  "name": "Short intro with excitement",
  "simple": "Most interesting simple fact",
  "detailed": "Combined amazing facts"
}}

Example for Blue Jay:
{{
  "name": "BLUE JAY! Starts with B!",
  "simple": "I can MIMIC hawk calls to scare other birds! WOW!",
  "detailed": "I'm SUPER smart - I can remember 200 different hiding spots for my food! And I paint my feathers with ants for FUN! We live in forests all over!"
}}

Make it UNIQUE and amazing!
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=200
        )
        
        script_text = response.choices[0].message.content.strip()
        
        # Clean up response
        if script_text.startswith("```json"):
            script_text = script_text[7:]
        if script_text.endswith("```"):
            script_text = script_text[:-3]
        
        scripts = json.loads(script_text)
        return scripts
    except Exception as e:
        print(f"⚠️ GPT error for {animal_name}: {str(e)[:50]}...")
        # Use the facts directly with excitement
        detailed_parts = []
        if size:
            detailed_parts.append(f"I'm {size.lower()}! THAT'S HUGE!")
        if unique:
            detailed_parts.append(f"And {unique.lower()}! INCREDIBLE!")
        if habitat:
            detailed_parts.append(f"I live in {habitat.lower()}! AMAZING!")
        
        if not detailed_parts:
            detailed_parts = [f"I'm an AMAZING {animal_name} with SUPER special powers!"]
        
        return {
            "name": f"{animal_name.upper()}! Starts with {animal_name[0]}!",
            "simple": f"WOW! {simple_fact.upper()}!",
            "detailed": f"GUESS WHAT? {' '.join(detailed_parts)}!"
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
    """Delete all audio and regenerate with GPT."""
    print("🎤 DELETING and REGENERATING All Audio with GPT...")
    
    # First delete all existing audio
    deleted_count = delete_all_audio()
    
    # Load data
    animals_file = Path(__file__).parent.parent / "src/data" / "animals_clean.json"
    facts_file = Path(__file__).parent.parent / "src/data" / "facts_clean.json"
    
    with open(animals_file, 'r', encoding='utf-8') as f:
        animals = json.load(f)
    
    with open(facts_file, 'r', encoding='utf-8') as f:
        facts = json.load(f)
    
    facts_lookup = {fact['name']: fact for fact in facts}
    
    # Process ALL animals (no skipping since we deleted everything)
    batch_size = 6
    success_count = 0
    
    for batch_start in range(0, len(animals), batch_size):
        batch_end = min(batch_start + batch_size, len(animals))
        batch = animals[batch_start:batch_end]
        
        print(f"\n📦 Processing batch {batch_start//batch_size + 1}/{(len(animals)-1)//batch_size + 1}")
        
        # Process each animal in batch
        for i, animal in enumerate(batch):
            animal_id = slugify(animal["name"])
            
            print(f"  🦁 [{batch_start + i + 1}/{len(animals)}] Processing: {animal['name']}")
            
            # Get facts
            animal_facts = facts_lookup.get(animal["name"], {})
            
            # Generate scripts with GPT
            print("    🤖 Creating script with GPT...")
            scripts = generate_gpt_script(animal["name"], animal_facts)
            
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
    
    print(f"\n✅ Complete! Deleted {deleted_count} old files, Generated {success_count} new audio files")

if __name__ == "__main__":
    main()
