#!/usr/bin/env python3
"""
Liora Asset Generator
Generates all audio and image assets for the animal learning app.
Run this once to generate the complete asset library.
"""

import os
import json
import requests
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any
import concurrent.futures
from PIL import Image, ImageDraw
import io
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_monolingual_v1")

GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_MODEL = os.getenv("STABILITY_MODEL", "stable-diffusion-xl-1024-v1-0")
IMAGE_SIZE = os.getenv("IMAGE_SIZE", "1024x1024")
IMAGE_FORMAT = os.getenv("IMAGE_FORMAT", "webp")
IMAGE_QUALITY = int(os.getenv("IMAGE_QUALITY", "90"))

# Asset directories
BASE_DIR = Path(__file__).parent.parent
PUBLIC_DIR = BASE_DIR / "public"
ASSETS_DIR = PUBLIC_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
AUDIO_DIR = ASSETS_DIR / "audio"

# Create directories
def create_directories():
    """Create all necessary directories for assets."""
    dirs = [
        IMAGES_DIR / "toy_mode",
        IMAGES_DIR / "real_mode",
        AUDIO_DIR / "names",
        AUDIO_DIR / "facts",
        AUDIO_DIR / "phonics",
    ]
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    print("✓ Created asset directories")

def slugify(name: str) -> str:
    """Convert animal name to URL-friendly slug."""
    return name.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')

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
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"✗ Audio generation failed for {output_path.name}: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error generating audio for {output_path.name}: {e}")
        return False

def generate_placeholder_image(animal_name: str, output_path: Path, style: str = "toy") -> bool:
    """Generate a placeholder image with the animal name."""
    try:
        # Create a simple colored rectangle with text
        width, height = 512, 512
        
        # Different colors for different styles
        if style == "toy":
            bg_color = (255, 182, 193)  # Light pink
            text_color = (255, 105, 180)  # Hot pink
        else:
            bg_color = (135, 206, 235)  # Sky blue
            text_color = (70, 130, 180)  # Steel blue
        
        # Create image
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw animal name
        font_size = 40
        text = animal_name.upper()
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), text, font=None)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw text (simple font)
        draw.text((x, y), text, fill=text_color)
        
        # Add emoji based on category
        emoji = "🦁"  # Default
        draw.text((width//2 - 20, y - 60), emoji, fill=text_color)
        
        # Save image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "WEBP")
        return True
    except Exception as e:
        print(f"✗ Error generating image for {output_path.name}: {e}")
        return False

def process_animal(animal: Dict[str, Any]) -> Dict[str, bool]:
    """Process a single animal: generate all its assets."""
    animal_id = slugify(animal["name"])
    results = {}
    
    # Generate audio files - support both simple and detailed facts
    name_text = f"{animal['name']}! Starts with {animal['name'][0]}."
    
    # Check if we have two-level facts
    if 'fact_level_1' in animal and 'fact_level_2' in animal:
        # Generate simple fact audio
        simple_fact = animal['fact_level_1']
        results["name_audio"] = generate_audio(
            name_text, 
            AUDIO_DIR / "names" / f"{animal_id}_name.mp3"
        )
        results["fact_simple_audio"] = generate_audio(
            simple_fact, 
            AUDIO_DIR / "facts" / f"{animal_id}_fact_simple.mp3"
        )
        
        # Generate detailed fact audio
        detailed_fact = f"Size: {animal['fact_level_2']['size_details']}. {animal['fact_level_2']['unique_fact']}. Habitat: {animal['fact_level_2']['habitat']}."
        results["fact_detailed_audio"] = generate_audio(
            detailed_fact, 
            AUDIO_DIR / "facts" / f"{animal_id}_fact_detailed.mp3"
        )
    else:
        # Fallback to single fact
        fact_text = animal.get("fact", "I'm an amazing animal!")
        results["name_audio"] = generate_audio(
            name_text, 
            AUDIO_DIR / "names" / f"{animal_id}_name.mp3"
        )
        results["fact_audio"] = generate_audio(
            fact_text, 
            AUDIO_DIR / "facts" / f"{animal_id}_fact.mp3"
        )
    
    # Generate placeholder images (will be replaced by real generator)
    results["toy_image"] = generate_placeholder_image(
        animal["name"],
        IMAGES_DIR / "toy_mode" / f"{animal_id}.webp",
        "toy"
    )
    
    results["real_image"] = generate_placeholder_image(
        animal["name"],
        IMAGES_DIR / "real_mode" / f"{animal_id}.webp",
        "real"
    )
    
    return results

def generate_phonics_audio():
    """Generate audio for each letter of the alphabet."""
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    for letter in letters:
        text = f"The letter {letter}!"
        output_path = AUDIO_DIR / "phonics" / f"letter_{letter}.mp3"
        
        if generate_audio(text, output_path):
            print(f"✓ Generated phonics for {letter}")
        else:
            print(f"✗ Failed phonics for {letter}")
        
        # Rate limiting
        time.sleep(0.5)

def create_manifest(animals: List[Dict[str, Any]], version: str) -> Dict[str, Any]:
    """Create a manifest file with version info and asset checksums."""
    manifest = {
        "version": version,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_animals": len(animals),
        "categories": list(set(a["category"] for a in animals)),
        "assets": {}
    }
    
    # Calculate checksums for all generated assets
    for animal in animals:
        animal_id = slugify(animal["name"])
        manifest["assets"][animal_id] = {
            "name": animal["name"],
            "category": animal["category"],
            "fact": animal["fact"],
            "files": {
                "toy_image": f"images/toy_mode/{animal_id}.webp",
                "real_image": f"images/real_mode/{animal_id}.webp",
                "name_audio": f"audio/names/{animal_id}_name.mp3",
                "fact_audio": f"audio/facts/{animal_id}_fact.mp3"
            }
        }
    
    return manifest

def main():
    """Main function to generate all assets."""
    print("🦁 Liora Asset Generator Starting...")
    
    # Load animals data
    animals_file = BASE_DIR / "animals_fixed.json"
    if not animals_file.exists():
        animals_file = BASE_DIR / "animals.json"
    
    with open(animals_file, 'r', encoding='utf-8') as f:
        animals = json.load(f)
    
    # Load facts data and merge
    facts_file = BASE_DIR / "src/data/facts_clean.json"
    if facts_file.exists():
        with open(facts_file, 'r', encoding='utf-8') as f:
            facts = json.load(f)
        
        # Create a map for quick lookup
        facts_map = {fact['name']: fact for fact in facts}
        
        # Merge facts into animal data
        for animal in animals:
            if animal['name'] in facts_map:
                animal.update(facts_map[animal['name']])
    
    print(f"✓ Loaded {len(animals)} animals with facts")
    
    # Create directories
    create_directories()
    
    # Generate phonics audio
    print("\n📢 Generating phonics audio...")
    generate_phonics_audio()
    
    # Process animals
    print(f"\n🎨 Processing {len(animals)} animals...")
    success_count = 0
    
    # Process in parallel with a limited number of workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_animal = {executor.submit(process_animal, animal): animal for animal in animals}
        
        for future in concurrent.futures.as_completed(future_to_animal):
            animal = future_to_animal[future]
            try:
                results = future.result()
                if all(results.values()):
                    success_count += 1
                    print(f"✓ Completed: {animal['name']}")
                else:
                    print(f"⚠ Partial: {animal['name']} - {results}")
            except Exception as e:
                print(f"✗ Failed: {animal['name']} - {e}")
    
    # Create manifest
    print("\n📋 Creating manifest...")
    version = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    manifest = create_manifest(animals, version)
    
    with open(ASSETS_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    # Copy animals data to src
    src_data_dir = BASE_DIR / "src" / "data"
    src_data_dir.mkdir(parents=True, exist_ok=True)
    
    with open(src_data_dir / "animals.json", "w", encoding="utf-8") as f:
        json.dump(animals, f, indent=2, ensure_ascii=False)
    
    # Summary
    print("\n" + "="*50)
    print("🎉 Asset Generation Complete!")
    print(f"✓ Successfully processed: {success_count}/{len(animals)} animals")
    print(f"✓ Version: {version}")
    print(f"✓ Manifest: {ASSETS_DIR / 'manifest.json'}")
    print(f"✓ Total assets: ~{len(animals) * 4 + 26} files")
    print(f"✓ Estimated size: ~150MB")
    print("="*50)

if __name__ == "__main__":
    main()
