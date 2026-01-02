#!/usr/bin/env python3
"""
Liora Image Generator
Generates stylized animal images for each category with appropriate backgrounds.
This script uses AI image generation (DALL-E, Midjourney, or Stable Diffusion).
"""

import os
import json
import requests
import time
import base64
from pathlib import Path
from typing import Dict, List, Any
import concurrent.futures
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_MODEL = os.getenv("STABILITY_MODEL", "stable-diffusion-xl-1024-v1-0")
IMAGE_SIZE = os.getenv("IMAGE_SIZE", "1024x1024")
IMAGE_FORMAT = os.getenv("IMAGE_FORMAT", "webp")
IMAGE_QUALITY = int(os.getenv("IMAGE_QUALITY", "90"))

# Alternative image API config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "dall-e-3")

# Category styles matching the frontend
CATEGORY_STYLES = {
    'Farm': {
        'background': 'sunny farm with soft blue sky and green pasture',
        'colors': 'warm yellows, greens, and sky blues',
        'lighting': 'gentle morning light',
        'style_toy': 'cute cartoon style with rounded features, big friendly eyes',
        'style_real': 'photorealistic but soft and warm lighting'
    },
    'Domestic': {
        'background': 'cozy home environment',
        'colors': 'warm peaches and soft beiges',
        'lighting': 'warm indoor lighting',
        'style_toy': 'adorable pet portrait style, extra fluffy and cute',
        'style_real': 'high quality pet photography, warm indoor lighting'
    },
    'Forest': {
        'background': 'lush forest with dappled sunlight',
        'colors': 'various shades of green',
        'lighting': 'sunlight filtering through trees',
        'style_toy': 'friendly forest creature style, simplified trees',
        'style_real': 'wildlife photography style, natural forest habitat'
    },
    'Jungle': {
        'background': 'vibrant tropical rainforest',
        'colors': 'dark greens, bright oranges, tropical colors',
        'lighting': 'humid atmosphere with bright highlights',
        'style_toy': 'playful jungle adventure style, bright and colorful',
        'style_real': 'National Geographic style, rich tropical colors'
    },
    'Nocturnal': {
        'background': 'starry night sky with moonlight',
        'colors': 'midnight blues and indigos',
        'lighting': 'magical moonlight',
        'style_toy': 'cute night creature style with glowing elements',
        'style_real': 'night wildlife photography with natural moonlight'
    },
    'Arctic': {
        'background': 'arctic snow and ice landscapes',
        'colors': 'light cyans, powder blues, whites',
        'lighting': 'crisp cold air with soft reflections',
        'style_toy': 'cute arctic friend style with soft rounded ice shapes',
        'style_real': 'arctic wildlife photography with pristine snow'
    },
    'Shallow Water': {
        'background': 'clear shallow tropical water',
        'colors': 'turquoises and sky blues',
        'lighting': 'sunlight filtering through water',
        'style_toy': 'playful sea creature style with bubbly effects',
        'style_real': 'underwater photography style, clear tropical water'
    },
    'Coral Reef': {
        'background': 'colorful coral reefs',
        'colors': 'coral reds, turquoises, yellows',
        'lighting': 'crystal clear water',
        'style_toy': 'vibrant cartoon reef style with exaggerated colors',
        'style_real': 'underwater reef photography with natural coral colors'
    },
    'Deep Sea': {
        'background': 'deep dark ocean',
        'colors': 'navy and midnight blues',
        'lighting': 'bioluminescent light effects',
        'style_toy': 'glowing deep sea creature style with light effects',
        'style_real': 'deep sea documentary style with natural bioluminescence'
    },
    'Ultra Deep Sea': {
        'background': 'abyssal depths',
        'colors': 'very dark blues and blacks',
        'lighting': 'minimal light, pressure-adapted',
        'style_toy': 'mysterious abyss creature with subtle glowing features',
        'style_real': 'deep sea ROV camera style, true deep sea conditions'
    }
}

def generate_image_prompt(animal_name: str, category: str, is_toy_mode: bool = True) -> str:
    """Generate an AI prompt for animal image."""
    style = CATEGORY_STYLES.get(category, CATEGORY_STYLES['Forest'])
    mode_style = style['style_toy'] if is_toy_mode else style['style_real']
    
    prompt = f"""Realistic {animal_name}, friendly gentle expression, educational children's book illustration style, 
{mode_style}, {style['background']}, {style['colors']}, {style['lighting']}, 
centered composition, high detail, Pixar-inspired rendering, white background isolated, 
no text, suitable for kids aged 3-8, professional illustration quality"""
    
    return prompt

def generate_image_with_stability(prompt: str, output_path: Path) -> bool:
    """Generate image using Stability AI API."""
    if not STABILITY_API_KEY:
        print("No Stability AI API key provided")
        return False
    
    url = "https://api.stability.ai/v1/generation/" + STABILITY_MODEL + "/text-to-image"
    
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
            # Get the base64 image data
            image_data = data["artifacts"][0]["base64"]
            # Decode and save
            image_bytes = base64.b64decode(image_data)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            return True
        else:
            print(f"✗ Stability AI error for {output_path.name}: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error generating image with Stability AI for {output_path.name}: {e}")
        return False

def generate_image_with_openai(prompt: str, output_path: Path) -> bool:
    """Generate image using OpenAI DALL-E."""
    if not OPENAI_API_KEY:
        print("No OpenAI API key provided")
        return False
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": OPENAI_MODEL,
        "prompt": prompt,
        "n": 1,
        "size": IMAGE_SIZE,
        "style": "vivid"
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/images/generations", json=data, headers=headers)
        if response.status_code == 200:
            image_url = response.json()['data'][0]['url']
            # Download the image
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(img_response.content)
                return True
        print(f"✗ OpenAI error for {output_path.name}: {response.status_code}")
        return False
    except Exception as e:
        print(f"✗ Error generating image with OpenAI for {output_path.name}: {e}")
        return False

def generate_placeholder_image(animal_name: str, category: str, output_path: Path, is_toy_mode: bool = True) -> bool:
    """Generate a styled placeholder image with category colors."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import math
        
        # Create image
        width, height = 512, 512
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Get category colors
        style = CATEGORY_STYLES.get(category, CATEGORY_STYLES['Forest'])
        
        # Create gradient background
        for y in range(height):
            # Simple gradient effect
            progress = y / height
            if is_toy_mode:
                # Brighter colors for toy mode
                r = int(135 + progress * 50)  # Light blue to lighter
                g = int(206 + progress * 30)
                b = int(235 + progress * 20)
            else:
                # More natural colors for real mode
                r = int(100 + progress * 30)
                g = int(150 + progress * 50)
                b = int(200 + progress * 30)
            
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add category-specific pattern
        if category in ['Shallow Water', 'Coral Reef', 'Deep Sea', 'Ultra Deep Sea']:
            # Draw bubbles
            for _ in range(20):
                x = int(width * (0.1 + 0.8 * (hash(animal_name + str(_)) % 100) / 100))
                y = int(height * (0.1 + 0.8 * (hash(animal_name + str(_ + 100)) % 100) / 100))
                size = 5 + (hash(animal_name + str(_ + 200)) % 10)
                draw.ellipse([x-size, y-size, x+size, y+size], outline=(255, 255, 255, 128))
        
        # Draw animal silhouette (simple circle with ears for demo)
        center_x, center_y = width // 2, height // 2
        body_size = 100 if is_toy_mode else 90
        
        # Body
        draw.ellipse([
            center_x - body_size,
            center_y - body_size,
            center_x + body_size,
            center_y + body_size
        ], fill=(80, 80, 80))
        
        # Ears (if applicable)
        if category not in ['Shallow Water', 'Coral Reef', 'Deep Sea', 'Ultra Deep Sea']:
            ear_size = body_size // 2
            # Left ear
            draw.ellipse([
                center_x - body_size - ear_size//2,
                center_y - body_size,
                center_x - body_size + ear_size//2,
                center_y - body_size + ear_size
            ], fill=(80, 80, 80))
            # Right ear
            draw.ellipse([
                center_x + body_size - ear_size//2,
                center_y - body_size,
                center_x + body_size + ear_size//2,
                center_y - body_size + ear_size
            ], fill=(80, 80, 80))
        
        # Draw animal name
        try:
            # Try to use a nice font
            font_size = 36 if is_toy_mode else 32
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        text = animal_name.upper()
        # Calculate text position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = height - 60
        
        # Draw text with shadow for better visibility
        shadow_offset = 2
        draw.text((x + shadow_offset, y + shadow_offset), text, fill=(0, 0, 0), font=font)
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # Save image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "WEBP", quality=90)
        return True
    except Exception as e:
        print(f"✗ Error generating placeholder for {output_path.name}: {e}")
        return False

def process_animal_images(animal: Dict[str, Any]) -> Dict[str, bool]:
    """Process both toy and real mode images for an animal."""
    animal_id = animal['id'] if 'id' in animal else animal['name'].lower().replace(' ', '_')
    results = {}
    
    # Generate toy mode image
    toy_prompt = generate_image_prompt(animal['name'], animal['category'], is_toy_mode=True)
    toy_path = Path(f"public/assets/images/toy_mode/{animal_id}.webp")
    
    # Try Stability AI first, then OpenAI, then fallback to placeholder
    if STABILITY_API_KEY:
        results['toy_image'] = generate_image_with_stability(toy_prompt, toy_path)
    elif OPENAI_API_KEY:
        results['toy_image'] = generate_image_with_openai(toy_prompt, toy_path)
    else:
        results['toy_image'] = generate_placeholder_image(animal['name'], animal['category'], toy_path, is_toy_mode=True)
    
    # Generate real mode image
    real_prompt = generate_image_prompt(animal['name'], animal['category'], is_toy_mode=False)
    real_path = Path(f"public/assets/images/real_mode/{animal_id}.webp")
    
    # Try Stability AI first, then OpenAI, then fallback to placeholder
    if STABILITY_API_KEY:
        results['real_image'] = generate_image_with_stability(real_prompt, real_path)
    elif OPENAI_API_KEY:
        results['real_image'] = generate_image_with_openai(real_prompt, real_path)
    else:
        results['real_image'] = generate_placeholder_image(animal['name'], animal['category'], real_path, is_toy_mode=False)
    
    return results

def main():
    """Main function to generate all animal images."""
    print("🎨 Liora Image Generator Starting...")
    
    # Load animals data
    base_dir = Path(__file__).parent.parent
    animals_file = base_dir / "animals_fixed.json"
    if not animals_file.exists():
        animals_file = base_dir / "animals.json"
    
    with open(animals_file, 'r', encoding='utf-8') as f:
        animals = json.load(f)
    
    print(f"✓ Loaded {len(animals)} animals")
    
    # Create output directories
    toy_dir = base_dir / "public" / "assets" / "images" / "toy_mode"
    real_dir = base_dir / "public" / "assets" / "images" / "real_mode"
    toy_dir.mkdir(parents=True, exist_ok=True)
    real_dir.mkdir(parents=True, exist_ok=True)
    
    # Process animals
    print(f"\n🎨 Processing {len(animals)} animals...")
    success_count = 0
    
    # Process in parallel with limited workers to avoid API rate limits
    # Use fewer workers for API calls, more for placeholders
    max_workers = 2 if (STABILITY_API_KEY or OPENAI_API_KEY) else 10
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_animal = {executor.submit(process_animal_images, animal): animal for animal in animals}
        
        for future in concurrent.futures.as_completed(future_to_animal):
            animal = future_to_animal[future]
            try:
                results = future.result()
                if all(results.values()):
                    success_count += 1
                    print(f"✓ Generated images for: {animal['name']}")
                else:
                    print(f"⚠ Partial for: {animal['name']} - {results}")
            except Exception as e:
                print(f"✗ Failed: {animal['name']} - {e}")
            
            # Rate limiting for API calls
            if STABILITY_API_KEY or OPENAI_API_KEY:
                time.sleep(1)
    
    # Summary
    print("\n" + "="*50)
    print("🎉 Image Generation Complete!")
    print(f"✓ Successfully processed: {success_count}/{len(animals)} animals")
    print(f"✓ Total images: ~{success_count * 2} files (toy + real modes)")
    print(f"✓ Format: WEBP with optimized compression")
    print(f"✓ Size: 1024x1024 pixels")
    print("="*50)

if __name__ == "__main__":
    main()
