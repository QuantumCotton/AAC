#!/usr/bin/env python3
"""
Generate images for ASL signs and World Places using Stability AI.
"""

import os
import json
import requests
import time
import base64
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_HOST = "https://api.stability.ai"

# Output directories
ASL_OUTPUT_DIR = Path(__file__).parent.parent / "public" / "assets" / "images" / "asl"
PLACES_OUTPUT_DIR = Path(__file__).parent.parent / "public" / "assets" / "images" / "places"

def slugify(text):
    """Convert text to filename-safe slug."""
    return text.lower().replace(" ", "_").replace("'", "").replace("-", "_")

def generate_image_stability(prompt: str, output_path: Path, width=512, height=512) -> bool:
    """Generate image using Stability AI."""
    if not STABILITY_API_KEY:
        print("No STABILITY_API_KEY found in environment")
        return False
    
    if output_path.exists():
        print(f"  ⏭️ Skipping {output_path.name} - already exists")
        return True

    engine_id = "stable-diffusion-xl-1024-v1-0"
    
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    body = {
        "text_prompts": [
            {"text": prompt, "weight": 1.0},
            {"text": "blurry, bad quality, text, watermark, scary, violent, realistic photo", "weight": -1.0}
        ],
        "cfg_scale": 7,
        "width": 1024,
        "height": 1024,
        "samples": 1,
        "steps": 30,
        "style_preset": "digital-art"
    }
    
    try:
        response = requests.post(
            f"{STABILITY_HOST}/v1/generation/{engine_id}/text-to-image",
            headers=headers,
            json=body,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            image_data = data["artifacts"][0]["base64"]
            image_bytes = base64.b64decode(image_data)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            print(f"  ✅ Generated: {output_path.name}")
            return True
        else:
            print(f"  ❌ Error {response.status_code}: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

def generate_asl_images():
    """Generate all ASL sign images."""
    prompts_path = Path(__file__).parent.parent / "stability_prompts_asl.json"
    
    with open(prompts_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    total = sum(len(cat["words"]) for cat in data["categories"])
    generated = 0
    skipped = 0
    
    print(f"\n🤟 Generating ASL Images ({total} total)")
    print("=" * 50)
    
    for category in data["categories"]:
        cat_dir = ASL_OUTPUT_DIR / category["id"]
        print(f"\n📁 Category: {category['name']} ({len(category['words'])} words)")
        
        for word_data in category["words"]:
            word = word_data["word"]
            prompt = word_data["prompt"]
            filename = f"{slugify(word)}.png"
            output_path = cat_dir / filename
            
            if output_path.exists():
                skipped += 1
                print(f"  ⏭️ {word} - exists")
                continue
            
            success = generate_image_stability(prompt, output_path)
            if success:
                generated += 1
            
            # Rate limit
            time.sleep(1.5)
    
    print(f"\n✅ ASL Complete: {generated} generated, {skipped} skipped")
    return generated

def generate_places_images():
    """Generate all Places images."""
    prompts_path = Path(__file__).parent.parent / "stability_prompts_places.json"
    
    with open(prompts_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    total = sum(len(cont["places"]) for cont in data["continents"])
    generated = 0
    skipped = 0
    
    print(f"\n🌍 Generating Places Images ({total} total)")
    print("=" * 50)
    
    for continent in data["continents"]:
        cont_dir = PLACES_OUTPUT_DIR / continent["id"]
        print(f"\n📁 Continent: {continent['name']} ({len(continent['places'])} places)")
        
        for place_data in continent["places"]:
            name = place_data["name"]
            prompt = place_data["prompt"]
            filename = f"{slugify(name)}.png"
            output_path = cont_dir / filename
            
            if output_path.exists():
                skipped += 1
                print(f"  ⏭️ {name} - exists")
                continue
            
            success = generate_image_stability(prompt, output_path)
            if success:
                generated += 1
            
            # Rate limit
            time.sleep(1.5)
    
    print(f"\n✅ Places Complete: {generated} generated, {skipped} skipped")
    return generated

def main():
    if not STABILITY_API_KEY:
        print("❌ STABILITY_API_KEY not found in .env file!")
        print("Please add your Stability AI API key to .env")
        return
    
    print("🎨 Liora Image Generator - ASL & Places")
    print("=" * 50)
    
    # Generate ASL images first
    asl_count = generate_asl_images()
    
    # Then Places images
    places_count = generate_places_images()
    
    print("\n" + "=" * 50)
    print(f"🎉 All done! Generated {asl_count + places_count} new images")

if __name__ == "__main__":
    main()
