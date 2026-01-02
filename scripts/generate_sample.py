#!/usr/bin/env python3
"""
Generate a small sample of assets to test the full pipeline
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

# Sample animals for testing
SAMPLE_ANIMALS = [
    {
        "name": "Lion",
        "category": "Jungle",
        "fact_level_1": "I am the king of the jungle! I have a big mane and I roar loudly!",
        "fact_level_2": {
            "size_details": "Male: 400 lbs, Female: 280 lbs",
            "unique_fact": "A lion's roar can be heard from 5 miles away",
            "habitat": "African savanna and grasslands"
        }
    },
    {
        "name": "Elephant",
        "category": "Jungle",
        "fact_level_1": "I have a long trunk and big ears! I am the largest land animal.",
        "fact_level_2": {
            "size_details": "Up to 13 feet tall, 15,000 lbs",
            "unique_fact": "They can 'hear' with their feet through ground vibrations",
            "habitat": "African forests and savannas"
        }
    },
    {
        "name": "Penguin",
        "category": "Arctic",
        "fact_level_1": "I can't fly but I am an excellent swimmer! I waddle when I walk.",
        "fact_level_2": {
            "size_details": "2-4 feet tall, 2-88 lbs depending on species",
            "unique_fact": "Emperor penguins can dive to 1,800 feet deep",
            "habitat": "Antarctica and southern hemisphere"
        }
    }
]

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
            print(f"✅ Generated audio: {output_path.name}")
            return True
        else:
            print(f"❌ Audio generation failed for {output_path.name}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error generating audio for {output_path.name}: {e}")
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
    
    try:
        response = requests.post(url, json=body, headers=headers)
        if response.status_code == 200:
            data = response.json()
            image_data = data["artifacts"][0]["base64"]
            image_bytes = base64.b64decode(image_data)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            print(f"✅ Generated image: {output_path.name}")
            return True
        else:
            print(f"❌ Image generation failed for {output_path.name}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error generating image for {output_path.name}: {e}")
        return False

def main():
    """Generate sample assets."""
    print("🎨 Generating Sample Assets for Liora...")
    
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
    for animal in SAMPLE_ANIMALS:
        animal_id = slugify(animal["name"])
        print(f"\n🦁 Processing: {animal['name']}")
        
        # Generate audio
        name_text = f"{animal['name']}! Starts with {animal['name'][0]}."
        generate_audio(name_text, assets_dir / "audio" / "names" / f"{animal_id}_name.mp3")
        
        # Simple fact audio
        generate_audio(animal['fact_level_1'], assets_dir / "audio" / "facts" / f"{animal_id}_fact_simple.mp3")
        
        # Detailed fact audio
        detailed_fact = f"Size: {animal['fact_level_2']['size_details']}. {animal['fact_level_2']['unique_fact']}. Habitat: {animal['fact_level_2']['habitat']}."
        generate_audio(detailed_fact, assets_dir / "audio" / "facts" / f"{animal_id}_fact_detailed.mp3")
        
        # Generate toy mode image
        toy_prompt = f"Realistic {animal['name']}, friendly gentle expression, cute cartoon style with rounded features, big friendly eyes, educational children's book illustration style, white background isolated, no text, suitable for kids aged 3-8, professional illustration quality"
        generate_image(toy_prompt, assets_dir / "images" / "toy_mode" / f"{animal_id}.webp")
        
        # Generate real mode image
        real_prompt = f"Realistic {animal['name']}, photorealistic but soft and warm lighting, educational children's book illustration style, white background isolated, no text, suitable for kids aged 3-8, professional illustration quality"
        generate_image(real_prompt, assets_dir / "images" / "real_mode" / f"{animal_id}.webp")
        
        # Rate limiting
        time.sleep(2)
    
    print("\n✅ Sample generation complete!")
    print(f"📁 Check {assets_dir} for generated files")

if __name__ == "__main__":
    main()
