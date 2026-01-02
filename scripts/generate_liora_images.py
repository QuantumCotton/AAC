#!/usr/bin/env python3
"""
Generate AAC symbol images for Liora using Stability AI.
Creates clear, high-contrast, child-friendly icons for each symbol.
"""

import os
import json
import time
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_MODEL = "stable-diffusion-xl-1024-v1-0"

BASE_DIR = Path(__file__).parent.parent
IMAGE_OUTPUT_DIR = BASE_DIR / "public" / "assets" / "images" / "liora"
SYMBOLS_FILE = BASE_DIR / "src" / "data" / "liora_symbols_full.json"

# AAC-optimized style prompt
AAC_STYLE = """
Simple, clear AAC communication symbol icon.
Bold black outlines, high contrast colors.
Flat design, no gradients or shadows.
Child-friendly, easily recognizable.
White or light solid background.
Centered composition, large and clear.
Professional AAC pictogram style like Proloquo2Go or TouchChat.
"""

# Category-specific color schemes
CATEGORY_COLORS = {
    "wants": "red and orange tones",
    "feelings": "blue and teal tones", 
    "food": "yellow and green tones",
    "actions": "green and cyan tones",
    "people": "purple and pink tones",
    "places": "blue and sky tones",
    "things": "orange and brown tones",
    "questions": "purple tones",
}

def ensure_dirs(categories):
    """Create output directories for each category."""
    IMAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for cat in categories:
        (IMAGE_OUTPUT_DIR / cat["id"]).mkdir(parents=True, exist_ok=True)

def generate_image(prompt: str, output_path: Path, negative_prompt: str = "") -> bool:
    """Generate image using Stability AI API."""
    if output_path.exists():
        print(f"  ⏭️  Skipping (exists): {output_path.name}")
        return True
    
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # AAC-optimized generation settings
    data = {
        "text_prompts": [
            {
                "text": prompt,
                "weight": 1.0
            },
            {
                "text": negative_prompt or "realistic, photographic, complex background, gradients, shadows, 3D, text, words, letters, watermark, blurry, detailed, intricate",
                "weight": -1.0
            }
        ],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30,
        "style_preset": "comic-book"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("artifacts"):
                image_data = base64.b64decode(result["artifacts"][0]["base64"])
                with open(output_path, "wb") as f:
                    f.write(image_data)
                print(f"  ✅ Generated: {output_path.name}")
                return True
            else:
                print(f"  ❌ No artifacts in response")
                return False
        else:
            print(f"  ❌ Error {response.status_code}: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

def build_symbol_prompt(symbol: dict, category: dict) -> str:
    """Build an AAC-optimized prompt for a symbol."""
    text = symbol["text"]
    cat_id = category["id"]
    cat_name = category["name"]
    colors = CATEGORY_COLORS.get(cat_id, "bright colors")
    
    # Symbol-specific prompt enhancements
    symbol_hints = {
        # Wants
        "want_more": "plus sign icon, addition symbol",
        "want_help": "hand reaching up, help gesture",
        "want_stop": "stop hand gesture, palm facing forward",
        "want_go": "arrow pointing right, movement",
        "want_yes": "checkmark, thumbs up",
        "want_no": "X mark, crossed out",
        "want_please": "praying hands gesture",
        "want_thank": "heart with hands",
        
        # Feelings
        "feel_happy": "smiling face, happy expression",
        "feel_sad": "crying face, tears",
        "feel_angry": "angry face, furrowed brows",
        "feel_scared": "frightened face, wide eyes",
        "feel_tired": "sleepy face, yawning",
        "feel_sick": "sick face, thermometer",
        "feel_hurt": "bandage, injured",
        "feel_love": "heart symbol, love",
        "feel_excited": "excited face, stars",
        "feel_bored": "bored face, unamused",
        
        # Food
        "food_eat": "person eating, fork and knife",
        "food_drink": "drinking cup, beverage",
        "food_water": "water droplet, glass of water",
        "food_milk": "milk carton, white liquid",
        "food_juice": "juice box, fruit drink",
        "food_apple": "red apple fruit",
        "food_banana": "yellow banana fruit",
        "food_cookie": "chocolate chip cookie",
        "food_bread": "loaf of bread, slice",
        "food_rice": "bowl of white rice",
        "food_chicken": "chicken drumstick",
        "food_egg": "egg, oval shape",
        
        # Actions
        "act_play": "child playing, toys",
        "act_read": "open book, reading",
        "act_watch": "TV screen, watching",
        "act_sleep": "sleeping person, bed",
        "act_bath": "bathtub, bubbles",
        "act_potty": "toilet, bathroom",
        "act_walk": "person walking, legs moving",
        "act_hug": "two people hugging",
        "act_sing": "person singing, music notes",
        "act_draw": "crayon drawing, art",
        
        # People
        "ppl_mama": "mother figure, woman",
        "ppl_dada": "father figure, man",
        "ppl_baby": "baby, infant",
        "ppl_sister": "girl, sister figure",
        "ppl_brother": "boy, brother figure",
        "ppl_grandma": "grandmother, elderly woman",
        "ppl_grandpa": "grandfather, elderly man",
        "ppl_friend": "two friends together",
        "ppl_teacher": "teacher at board",
        
        # Places
        "place_home": "house, home building",
        "place_school": "school building",
        "place_park": "playground, park trees",
        "place_store": "store front, shop",
        "place_car": "car vehicle",
        "place_outside": "outdoors, trees sun",
        "place_bed": "bed furniture",
        "place_kitchen": "kitchen, stove",
        
        # Things
        "thing_toy": "teddy bear toy",
        "thing_ball": "round ball",
        "thing_book": "book, pages",
        "thing_phone": "smartphone device",
        "thing_tablet": "tablet device",
        "thing_blanket": "soft blanket",
        "thing_shoes": "pair of shoes",
        "thing_clothes": "shirt clothing",
        
        # Questions
        "q_what": "question mark, wondering",
        "q_where": "location pin, searching",
        "q_who": "person silhouette with question",
        "q_when": "clock, time",
        "q_why": "thinking bubble",
        "q_how": "tool, method",
    }
    
    hint = symbol_hints.get(symbol["id"], text)
    
    prompt = f"{AAC_STYLE}\n\nSymbol for '{text}': {hint}.\nUse {colors}."
    return prompt

def generate_symbol_image(symbol: dict, category: dict):
    """Generate image for a single symbol."""
    symbol_id = symbol["id"]
    cat_id = category["id"]
    
    output_path = IMAGE_OUTPUT_DIR / cat_id / f"{symbol_id}.png"
    prompt = build_symbol_prompt(symbol, category)
    
    success = generate_image(prompt, output_path)
    
    # Rate limiting - Stability AI has limits
    time.sleep(1.0)
    
    return success

def main():
    print("🎨 Liora AAC Image Generator")
    print("=" * 50)
    
    if not STABILITY_API_KEY:
        print("❌ STABILITY_API_KEY not found in .env")
        return
    
    # Load symbols
    with open(SYMBOLS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    categories = data.get("categories", [])
    
    # Create output directories
    ensure_dirs(categories)
    
    # Count total
    total_symbols = sum(len(cat["symbols"]) for cat in categories)
    print(f"\n📊 Found {total_symbols} symbols in {len(categories)} categories")
    print(f"📊 Will generate {total_symbols} images\n")
    
    generated = 0
    failed = 0
    
    # Generate images
    for cat in categories:
        print(f"\n🏷️  Category: {cat['name']} ({cat['emoji']})")
        for symbol in cat["symbols"]:
            if generate_symbol_image(symbol, cat):
                generated += 1
            else:
                failed += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Generated: {generated}")
    print(f"❌ Failed: {failed}")
    print(f"📂 Output: {IMAGE_OUTPUT_DIR}")

if __name__ == "__main__":
    main()
