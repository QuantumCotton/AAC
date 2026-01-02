#!/usr/bin/env python3
"""
Replace placeholder images with real AI-generated images
"""

import os
import json
import requests
import base64
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_MODEL = os.getenv("STABILITY_MODEL", "stable-diffusion-xl-1024-v1-0")

def slugify(name: str) -> str:
    """Convert animal name to URL-friendly slug."""
    return name.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')

def is_placeholder_image(file_path: Path) -> bool:
    """Check if image is a placeholder (small file size)."""
    if not file_path.exists():
        return False
    return file_path.stat().st_size < 50000  # Less than 50KB is likely placeholder

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
            print(f"✅ Generated real image: {output_path.name} ({len(image_bytes)} bytes)")
            return True
        else:
            print(f"❌ Image generation failed for {output_path.name}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error generating image for {output_path.name}: {e}")
        return False

def main():
    """Replace placeholder images with real AI-generated images."""
    print("🎨 Replacing Placeholder Images with Real AI Images...")
    
    # Load animals list
    animals_file = Path(__file__).parent.parent / "src/data" / "animals_clean.json"
    with open(animals_file, 'r', encoding='utf-8') as f:
        animals = json.load(f)
    
    # Create directories
    base_dir = Path(__file__).parent.parent
    assets_dir = base_dir / "public" / "assets"
    
    dirs = [
        assets_dir / "images" / "toy_mode",
        assets_dir / "images" / "real_mode",
    ]
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Check balance
    if STABILITY_API_KEY:
        balance_url = "https://api.stability.ai/v1/user/balance"
        balance_headers = {"Authorization": f"Bearer {STABILITY_API_KEY}"}
        balance_response = requests.get(balance_url, headers=balance_headers)
        
        if balance_response.status_code == 200:
            credits = balance_response.json()['credits']
            print(f"💰 Current credits: {credits}")
            
            # Calculate how many we can generate (3 credits per image)
            max_images = int(credits // 6)  # 6 credits per animal (2 images)
            print(f"📈 Can generate real images for up to {max_images} animals")
    
    # Find animals with placeholder images
    placeholders = []
    for animal in animals:
        animal_id = slugify(animal["name"])
        toy_path = assets_dir / "images" / "toy_mode" / f"{animal_id}.webp"
        
        if is_placeholder_image(toy_path):
            placeholders.append(animal)
    
    print(f"🎯 Found {len(placeholders)} animals with placeholder images")
    
    # Generate real images for placeholders (limit to what we can afford)
    to_process = placeholders[:min(len(placeholders), max_images if 'max_images' in locals() else len(placeholders))]
    
    print(f"📝 Will generate real images for {len(to_process)} animals")
    
    # Generate images
    success_count = 0
    for i, animal in enumerate(to_process):
        animal_id = slugify(animal["name"])
        category = animal.get("category", "General")
        
        print(f"\n🦁 [{i+1}/{len(to_process)}] Processing: {animal['name']}")
        
        # Generate prompts based on category
        if category == "Farm":
            toy_prompt = f"Realistic {animal['name']}, friendly cartoon style with rounded features, big friendly eyes, educational children's book illustration, red barn background, white isolated, suitable for kids aged 3-8, professional illustration quality"
            real_prompt = f"Realistic {animal['name']}, photorealistic farm setting, soft warm lighting, educational children's book illustration, white isolated, suitable for kids aged 3-8, professional photography style"
        elif category == "Domestic":
            toy_prompt = f"Realistic {animal['name']}, cute cartoon pet style, friendly expression, colorful collar or accessory, home environment background, white isolated, suitable for kids aged 3-8, professional illustration quality"
            real_prompt = f"Realistic {animal['name']}, photorealistic pet photography, warm indoor lighting, educational children's book illustration, white isolated, suitable for kids aged 3-8, professional photography style"
        elif category in ["Jungle", "Forest"]:
            toy_prompt = f"Realistic {animal['name']}, friendly jungle cartoon style, lush green leaves background, big friendly eyes, educational children's book illustration, white isolated, suitable for kids aged 3-8, professional illustration quality"
            real_prompt = f"Realistic {animal['name']}, photorealistic in natural habitat, dappled sunlight through trees, educational children's book illustration, white isolated, suitable for kids aged 3-8, professional photography style"
        elif category == "Arctic":
            toy_prompt = f"Realistic {animal['name']}, cute cartoon in snowy setting, blue and white colors, friendly expression, educational children's book illustration, white isolated, suitable for kids aged 3-8, professional illustration quality"
            real_prompt = f"Realistic {animal['name']}, photorealistic arctic environment, soft blue light on snow, educational children's book illustration, white isolated, suitable for kids aged 3-8, professional photography style"
        elif category in ["Shallow Water", "Coral Reef"]:
            toy_prompt = f"Realistic {animal['name']}, colorful cartoon underwater style, coral and bubbles background, friendly expression, educational children's book illustration, white isolated, suitable for kids aged 3-8, professional illustration quality"
            real_prompt = f"Realistic {animal['name']}, photorealistic underwater scene, sunlight filtering through water, educational children's book illustration, white isolated, suitable for kids aged 3-8, professional photography style"
        elif category in ["Deep Sea", "Ultra Deep Sea"]:
            toy_prompt = f"Realistic {animal['name']}, bioluminescent cartoon style, glowing effects, dark ocean background, friendly expression, educational children's book illustration, white isolated, suitable for kids aged 3-8, professional illustration quality"
            real_prompt = f"Realistic {animal['name']}, photorealistic deep sea with bioluminescence, dark mysterious lighting, educational children's book illustration, white isolated, suitable for kids aged 3-8, professional photography style"
        else:
            toy_prompt = f"Realistic {animal['name']}, friendly cartoon style, big friendly eyes, educational children's book illustration, white background isolated, suitable for kids aged 3-8, professional illustration quality"
            real_prompt = f"Realistic {animal['name']}, photorealistic but soft lighting, educational children's book illustration, white background isolated, suitable for kids aged 3-8, professional photography style"
        
        # Generate toy mode image
        if generate_image(toy_prompt, assets_dir / "images" / "toy_mode" / f"{animal_id}.webp"):
            success_count += 1
        
        # Small delay between images
        import time
        time.sleep(1)
        
        # Generate real mode image
        if generate_image(real_prompt, assets_dir / "images" / "real_mode" / f"{animal_id}.webp"):
            success_count += 1
        
        time.sleep(1)
        
        # Check credits periodically
        if (i + 1) % 10 == 0 and 'balance_headers' in locals():
            balance_response = requests.get(balance_url, headers=balance_headers)
            if balance_response.status_code == 200:
                credits = balance_response.json()['credits']
                print(f"💰 Credits remaining: {credits}")
                if credits < 6:
                    print("⚠️ Low credits, stopping generation")
                    break
    
    print("\n✅ Real image generation complete!")
    print(f"📊 Generated real images for {success_count // 2} animals ({success_count} total images)")
    print(f"📁 Check {assets_dir / 'images'} for generated files")

if __name__ == "__main__":
    main()
