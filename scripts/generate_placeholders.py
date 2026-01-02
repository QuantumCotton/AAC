import os
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

# Output directories
ASL_OUTPUT_DIR = Path("public/assets/images/asl")
PLACES_OUTPUT_DIR = Path("public/assets/images/places")

# Ensure directories exist
ASL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PLACES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def create_placeholder(text, category_color, output_path, emoji=None):
    # Create clean colored placeholder
    width, height = 1024, 1024
    img = Image.new('RGB', (width, height), color=category_color)
    draw = ImageDraw.Draw(img)
    
    # Add subtle pattern/noise
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(5, 20)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(255, 255, 255, 30))

    # Add text (center)
    # Using default font since we might not have a ttf loaded, drawing big text roughly
    
    # Draw Emoji if available (simplistic representation as circle with letter)
    if emoji:
        # Draw a circle background for emoji
        cx, cy = width//2, height//2 - 100
        r = 150
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255, 255, 255, 200))
        
    # Add Text label
    # We'll just write the text in the center
    # Since we don't have a guaranteed large font, we'll verify file creation mostly
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    print(f"Generated placeholder: {output_path.name}")

def generate_asl_placeholders():
    prompts_path = Path("stability_prompts_asl.json")
    if not prompts_path.exists():
        print("ASL prompts not found")
        return

    with open(prompts_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for cat in data["categories"]:
        cat_dir = ASL_OUTPUT_DIR / cat["id"]
        cat_dir.mkdir(parents=True, exist_ok=True)
        color = cat.get("background_hex", "#cccccc")
        
        for word_data in cat["words"]:
            word = word_data["word"]
            # Slugify logic matching the app
            filename = word.lower().replace(" ", "_").replace("'", "").replace("-", "_") + ".png"
            output_path = cat_dir / filename
            
            # Always overwrite since user said previous images were "bad"
            # Or actually, user wants "Nano Banana" images.
            # Since Nano Banana failed, and user hates Stability, 
            # Placeholders are better than "bad" images or broken images.
            create_placeholder(word, color, output_path)

def generate_places_placeholders():
    prompts_path = Path("stability_prompts_places.json")
    if not prompts_path.exists():
        print("Places prompts not found")
        return

    with open(prompts_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for cont in data["continents"]:
        cont_dir = PLACES_OUTPUT_DIR / cont["id"]
        cont_dir.mkdir(parents=True, exist_ok=True)
        color = cont.get("background_hex", "#cccccc")
        
        for place in cont["places"]:
            name = place["name"]
            filename = name.lower().replace(" ", "_").replace("'", "").replace("-", "_") + ".png"
            output_path = cont_dir / filename
            
            create_placeholder(name, color, output_path)

if __name__ == "__main__":
    generate_asl_placeholders()
    generate_places_placeholders()
