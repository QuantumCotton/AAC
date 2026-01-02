#!/usr/bin/env python3
"""
Generate images for ASL signs and World Places using DALL-E 3.
Higher quality than Stability AI for educational illustrations.
"""

import os
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Output directories
ASL_OUTPUT_DIR = Path(__file__).parent.parent / "public" / "assets" / "images" / "asl"
PLACES_OUTPUT_DIR = Path(__file__).parent.parent / "public" / "assets" / "images" / "places"

def slugify(text):
    """Convert text to filename-safe slug."""
    return text.lower().replace(" ", "_").replace("'", "").replace("-", "_")

def generate_image_dalle(prompt: str, output_path: Path) -> bool:
    """Generate image using DALL-E 3."""
    if not OPENAI_API_KEY:
        print("No OPENAI_API_KEY found in environment")
        return False
    
    if output_path.exists():
        print(f"  ⏭️ Skipping {output_path.name} - already exists")
        return True

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Enhanced prompt for kid-friendly educational style
    enhanced_prompt = f"{prompt}, digital illustration, clean simple design, bright cheerful colors, white or solid color background, no text, child-friendly, educational"
    
    body = {
        "model": "dall-e-3",
        "prompt": enhanced_prompt,
        "n": 1,
        "size": "1024x1024",
        "quality": "standard",
        "style": "vivid"
    }
    
    try:
        print(f"  🎨 Generating: {output_path.stem}...")
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=body,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            image_url = data["data"][0]["url"]
            
            # Download the image
            img_response = requests.get(image_url, timeout=60)
            if img_response.status_code == 200:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(img_response.content)
                print(f"  ✅ Generated: {output_path.name}")
                return True
            else:
                print(f"  ❌ Failed to download image")
                return False
        else:
            error = response.json().get("error", {}).get("message", response.text[:200])
            print(f"  ❌ Error: {error}")
            return False
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

def generate_asl_images():
    """Generate ASL sign images - simplified prompts for DALL-E."""
    total = 0
    generated = 0
    skipped = 0
    
    # Simplified ASL prompts for DALL-E 3
    asl_categories = {
        "core": {
            "name": "Core & Manners",
            "color": "#FF6B6B",
            "words": {
                "more": "cute cartoon hands making 'more' sign, fingertips touching together, pastel pink background",
                "please": "friendly cartoon child with hand on chest making please gesture, soft pink background",
                "thank_you": "smiling cartoon child touching chin then moving hand outward, thank you gesture",
                "help": "cartoon hands with thumbs up on open palm, helping gesture, friendly style",
                "yes": "happy cartoon fist nodding yes, bright cheerful style",
                "no": "cartoon fingers pinching together for no sign, simple clean design",
                "sorry": "cartoon hand making circular motion on chest, apologetic expression",
                "i_love_you": "cartoon hand with pinky index and thumb extended, I love you sign language",
                "hello": "friendly cartoon hand waving hello, bright cheerful background",
                "goodbye": "cute cartoon hand waving goodbye, warm friendly style"
            }
        },
        "family": {
            "name": "Family & People", 
            "color": "#4ECDC4",
            "words": {
                "mom": "cartoon hand with thumb touching chin, mom sign, teal background",
                "dad": "cartoon hand with thumb touching forehead, dad sign, teal background",
                "baby": "cartoon arms cradling motion for baby sign, cute style",
                "grandma": "cartoon thumb bouncing from chin, grandma sign",
                "grandpa": "cartoon thumb bouncing from forehead, grandpa sign",
                "friend": "cartoon hooked index fingers linking together, friendship sign",
                "teacher": "cartoon hands moving from temples outward, teacher sign",
                "family": "cartoon F hands moving in circle, family sign"
            }
        },
        "food": {
            "name": "Food & Drink",
            "color": "#FFE66D", 
            "words": {
                "eat": "cartoon hand bringing food to mouth, eating gesture, yellow background",
                "drink": "cartoon hand shaped like cup moving to mouth, drinking gesture",
                "water": "cartoon W hand tapping chin, water sign",
                "milk": "cartoon hand squeezing motion, milk sign",
                "apple": "cartoon hand twisting on cheek, apple sign",
                "banana": "cartoon hands peeling motion, banana sign",
                "cookie": "cartoon hand twisting on palm, cookie sign",
                "hungry": "cartoon C hand moving down chest, hungry sign"
            }
        },
        "animals": {
            "name": "Animals",
            "color": "#95E1D3",
            "words": {
                "dog": "cartoon hand patting thigh then snapping, dog sign, mint green background",
                "cat": "cartoon fingers pulling whiskers from face, cat sign",
                "bird": "cartoon hand making beak opening motion at mouth, bird sign",
                "fish": "cartoon hand swimming sideways, fish sign",
                "elephant": "cartoon hand tracing trunk from nose, elephant sign",
                "monkey": "cartoon hands scratching sides, monkey sign",
                "butterfly": "cartoon thumbs linked with fingers flapping, butterfly sign"
            }
        },
        "feelings": {
            "name": "Feelings",
            "color": "#F8B500",
            "words": {
                "happy": "cartoon hands brushing up on chest, happy sign, orange background",
                "sad": "cartoon hands drooping down face, sad expression sign",
                "angry": "cartoon claw hands pulling from face, angry sign",
                "scared": "cartoon hands opening outward from chest, scared sign",
                "tired": "cartoon hands drooping on chest, tired sign",
                "love": "cartoon arms crossed hugging chest, love sign"
            }
        },
        "colors": {
            "name": "Colors & Numbers",
            "color": "#AA96DA",
            "words": {
                "red": "cartoon finger brushing down from lip, red sign, purple background",
                "blue": "cartoon B hand shaking, blue sign",
                "yellow": "cartoon Y hand shaking, yellow sign",
                "green": "cartoon G hand shaking, green sign",
                "one": "cartoon hand showing one finger up",
                "two": "cartoon hand showing peace sign, number two",
                "three": "cartoon hand with thumb index middle fingers up, number three",
                "five": "cartoon open hand showing all five fingers"
            }
        }
    }
    
    print(f"\n🤟 Generating ASL Images with DALL-E 3")
    print("=" * 50)
    
    for cat_id, cat_data in asl_categories.items():
        cat_dir = ASL_OUTPUT_DIR / cat_id
        print(f"\n📁 {cat_data['name']} ({len(cat_data['words'])} words)")
        
        for word_slug, prompt in cat_data["words"].items():
            total += 1
            filename = f"{word_slug}.png"
            output_path = cat_dir / filename
            
            if output_path.exists():
                skipped += 1
                continue
            
            success = generate_image_dalle(prompt, output_path)
            if success:
                generated += 1
            
            # Rate limit - DALL-E has limits
            time.sleep(2)
    
    print(f"\n✅ ASL Complete: {generated} generated, {skipped} skipped, {total} total")
    return generated

def generate_places_images():
    """Generate Places images with DALL-E 3."""
    total = 0
    generated = 0
    skipped = 0
    
    # Simplified places prompts for DALL-E 3
    places_continents = {
        "africa": {
            "name": "Africa",
            "places": {
                "sahara_desert": "beautiful golden sand dunes of Sahara Desert, bright sun, cartoon illustration style",
                "victoria_falls": "majestic Victoria Falls waterfall with rainbow mist, illustration style",
                "pyramids": "ancient Egyptian pyramids with sphinx, clear blue sky, kid-friendly illustration",
                "kilimanjaro": "snow-capped Mount Kilimanjaro with African savanna, cartoon style",
                "serengeti": "Serengeti plains with zebras and acacia trees, colorful illustration"
            }
        },
        "asia": {
            "name": "Asia",
            "places": {
                "great_wall": "Great Wall of China winding through green mountains, illustration style",
                "taj_mahal": "beautiful white Taj Mahal with reflecting pool, kid-friendly illustration",
                "mount_everest": "snow-covered Mount Everest peak above clouds, cartoon style",
                "tokyo": "colorful Tokyo cityscape with cherry blossoms and Tokyo Tower, illustration",
                "panda_forest": "bamboo forest with cute panda, Chinese mountains, cartoon style"
            }
        },
        "europe": {
            "name": "Europe",
            "places": {
                "eiffel_tower": "iconic Eiffel Tower in Paris with flowers, cheerful illustration style",
                "big_ben": "Big Ben clock tower London with red bus, cartoon illustration",
                "colosseum": "ancient Roman Colosseum on sunny day, kid-friendly illustration",
                "alps": "beautiful snowy Alps mountains with green valleys, cartoon style",
                "castle": "fairy tale European castle on hilltop, magical illustration style"
            }
        },
        "north_america": {
            "name": "North America",
            "places": {
                "statue_of_liberty": "Statue of Liberty holding torch, New York Harbor, illustration",
                "grand_canyon": "colorful layered Grand Canyon rock formations, cartoon style",
                "yellowstone": "Old Faithful geyser erupting at Yellowstone, illustration style",
                "niagara_falls": "powerful Niagara Falls with rainbow, kid-friendly illustration",
                "new_york": "New York City skyline with Empire State Building, cartoon style"
            }
        },
        "south_america": {
            "name": "South America",
            "places": {
                "amazon": "lush Amazon rainforest with colorful parrots and river, illustration",
                "machu_picchu": "ancient Machu Picchu ruins in misty mountains, cartoon style",
                "rio": "Rio de Janeiro with Christ the Redeemer and beach, illustration",
                "galapagos": "Galapagos Islands with giant tortoise and blue water, cartoon style",
                "iguazu_falls": "spectacular Iguazu Falls surrounded by jungle, illustration"
            }
        },
        "oceania": {
            "name": "Oceania",
            "places": {
                "great_barrier_reef": "colorful Great Barrier Reef with tropical fish and coral, illustration",
                "sydney_opera": "Sydney Opera House with harbor bridge, cartoon illustration style",
                "uluru": "red Uluru rock at sunset in Australian outback, illustration",
                "koala": "cute koala in eucalyptus tree, Australian wildlife, cartoon style"
            }
        },
        "antarctica": {
            "name": "Antarctica",
            "places": {
                "south_pole": "South Pole with penguins and ice, aurora lights, illustration style",
                "icebergs": "beautiful blue Antarctic icebergs with penguins, cartoon style",
                "penguin_colony": "adorable emperor penguin colony on ice, kid-friendly illustration"
            }
        }
    }
    
    print(f"\n🌍 Generating Places Images with DALL-E 3")
    print("=" * 50)
    
    for cont_id, cont_data in places_continents.items():
        cont_dir = PLACES_OUTPUT_DIR / cont_id
        print(f"\n📁 {cont_data['name']} ({len(cont_data['places'])} places)")
        
        for place_slug, prompt in cont_data["places"].items():
            total += 1
            filename = f"{place_slug}.png"
            output_path = cont_dir / filename
            
            if output_path.exists():
                skipped += 1
                continue
            
            success = generate_image_dalle(prompt, output_path)
            if success:
                generated += 1
            
            time.sleep(2)
    
    print(f"\n✅ Places Complete: {generated} generated, {skipped} skipped, {total} total")
    return generated

def main():
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not found in .env file!")
        return
    
    print("🎨 Liora Image Generator - DALL-E 3")
    print("=" * 50)
    
    # Clear old bad Stability images first
    import shutil
    for d in [ASL_OUTPUT_DIR, PLACES_OUTPUT_DIR]:
        if d.exists():
            shutil.rmtree(d)
            print(f"🗑️ Cleared old images: {d}")
    
    asl_count = generate_asl_images()
    places_count = generate_places_images()
    
    print("\n" + "=" * 50)
    print(f"🎉 Done! Generated {asl_count + places_count} images with DALL-E 3")

if __name__ == "__main__":
    main()
