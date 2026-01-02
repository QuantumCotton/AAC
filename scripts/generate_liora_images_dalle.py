#!/usr/bin/env python3
"""
Generate AAC symbol images for Liora using OpenAI DALL-E 3.
Creates clear, high-contrast, child-friendly icons for each symbol.
"""

import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

BASE_DIR = Path(__file__).parent.parent
IMAGE_OUTPUT_DIR = BASE_DIR / "public" / "assets" / "images" / "liora"
SYMBOLS_FILE = BASE_DIR / "src" / "data" / "liora_symbols_full.json"

# AAC-optimized style prompt for DALL-E 3
AAC_STYLE = """Create a simple AAC (Augmentative and Alternative Communication) symbol icon.
Style requirements:
- Bold black outlines
- Flat, solid colors (no gradients)
- White or very light solid background
- Centered, large, and immediately recognizable
- Child-friendly and clear
- Professional pictogram style similar to Proloquo2Go or SymbolStix
- NO text, words, or letters in the image
- Simple shapes, minimal detail
- High contrast for visibility"""

AAC_CONSTRAINTS = """Critical constraints (must follow):
- Depict ONE concrete object OR ONE clear human action only.
- No abstract logos or generic app icons.
- Do NOT draw a rounded-square app icon background.
- Do NOT add decorative sparkles, plus signs, medical crosses, badges, UI elements.
- Do NOT use 3D, gradients, shadows, glassmorphism, skeuomorphic effects.
- Do NOT include any text, letters, numbers, punctuation.
- Use a plain white background.
"""

def _bg_instruction() -> str:
    bg = os.getenv("BG_COLOR_HEX", "").strip()
    if not bg:
        return "Use a flat solid white background."
    return f"Use a flat solid background color {bg}. No gradient."

def ensure_dirs(categories):
    """Create output directories for each category."""
    IMAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for cat in categories:
        (IMAGE_OUTPUT_DIR / cat["id"]).mkdir(parents=True, exist_ok=True)

def generate_image(prompt: str, output_path: Path) -> bool:
    """Generate image using OpenAI DALL-E 3 API."""
    if output_path.exists():
        print(f"  ⏭️  Skipping (exists): {output_path.name}")
        return True
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        
        # Download the image
        img_response = requests.get(image_url, timeout=30)
        if img_response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(img_response.content)
            print(f"  ✅ Generated: {output_path.name}")
            return True
        else:
            print(f"  ❌ Download failed: {img_response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

# Symbol-specific visual descriptions for better DALL-E results
SYMBOL_VISUALS = {
    # Core Words
    "core_i": "A simple pictogram of a child pointing to their own chest (self)",
    "core_you": "A simple pictogram of a hand pointing outward toward another person",
    "core_want": "A simple pictogram of two hands reaching toward a cookie",
    "core_need": "A simple pictogram of a child reaching for water (urgent need)",
    "core_like": "A simple pictogram of a thumbs up hand gesture",
    "core_dont_like": "A simple pictogram of a thumbs down hand gesture",
    "core_more": "A simple pictogram of an empty bowl being refilled (more)",
    "core_all_done": "A simple pictogram of empty hands held up to show finished (all done)",
    "core_help": "A pictogram of one hand helping/lifting another hand",
    "core_stop": "A pictogram of an open palm facing forward, stop gesture",
    "core_go": "A pictogram of an arrow pointing right, movement forward",
    "core_yes": "A simple pictogram of a child nodding yes",
    "core_no": "A simple pictogram of a child shaking head no",
    "core_please": "A pictogram of hands pressed together in please gesture",
    "core_thank_you": "A pictogram of hand touching chin moving outward, gratitude",
    "core_sorry": "A pictogram of person with apologetic expression, hand on chest",
    "core_look": "A pictogram of eyes looking, attention symbol",
    "core_get": "A pictogram of hand grasping/grabbing motion",
    "core_put": "A pictogram of hand placing something down",
    "core_give": "A pictogram of hands offering/giving gesture",
    "core_take": "A pictogram of hand taking/receiving gesture",
    "core_make": "A pictogram of hands crafting/building",
    "core_do": "A pictogram of active hands doing an action",
    "core_have": "A pictogram of hands holding something close",
    
    # Feelings
    "feel_happy": "A pictogram of a smiling face with upturned mouth",
    "feel_sad": "A pictogram of a sad face with downturned mouth and teardrop",
    "feel_angry": "A pictogram of an angry face with furrowed brows",
    "feel_scared": "A pictogram of a frightened face with wide eyes",
    "feel_tired": "A pictogram of a sleepy face with drooping eyes",
    "feel_sick": "A pictogram of a sick face, green tinge, thermometer",
    "feel_hurt": "A pictogram of a face with bandage, pain expression",
    "feel_love": "A pictogram of a red heart symbol",
    "feel_excited": "A pictogram of an excited face with stars around it",
    "feel_bored": "A pictogram of a bored face with flat expression",
    "feel_hungry": "A pictogram of a person with hand on empty stomach",
    "feel_thirsty": "A pictogram of a person reaching for a glass of water",
    "feel_cold": "A pictogram of a person shivering with cold lines",
    "feel_hot": "A pictogram of a person fanning themselves, heat waves",
    "feel_nervous": "A pictogram of a worried face with sweat drop",
    "feel_confused": "A pictogram of a face with question marks around it",
    "feel_frustrated": "A pictogram of a frustrated face with steam",
    "feel_calm": "A pictogram of a peaceful serene face",
    "feel_proud": "A pictogram of a person standing tall with pride",
    "feel_silly": "A pictogram of a playful goofy face sticking tongue out",
    
    # Food & Drink
    "food_eat": "A pictogram of a person eating, fork to mouth",
    "food_drink": "A pictogram of a person drinking from a cup",
    "food_water": "A pictogram of a glass of clear water with droplet",
    "food_milk": "A pictogram of a milk carton and glass of white milk",
    "food_juice": "A pictogram of a juice box with straw",
    "food_apple": "A pictogram of a red apple with leaf",
    "food_banana": "A pictogram of a yellow banana",
    "food_orange": "A pictogram of an orange citrus fruit",
    "food_grapes": "A pictogram of a bunch of purple grapes",
    "food_strawberry": "A pictogram of a red strawberry",
    "food_cookie": "A pictogram of a chocolate chip cookie",
    "food_crackers": "A pictogram of square crackers",
    "food_chips": "A pictogram of potato chips in a bag",
    "food_candy": "A pictogram of wrapped candy",
    "food_ice_cream": "A pictogram of an ice cream cone",
    "food_bread": "A pictogram of a loaf of bread",
    "food_rice": "A pictogram of a bowl of white rice",
    "food_noodles": "A pictogram of a bowl of noodles with chopsticks",
    "food_chicken": "A pictogram of a chicken drumstick",
    "food_fish": "A pictogram of a cooked fish on a plate",
    "food_meat": "A pictogram of a steak or meat portion",
    "food_egg": "A pictogram of an egg, sunny side up",
    "food_cheese": "A pictogram of a wedge of yellow cheese",
    "food_pizza": "A pictogram of a pizza slice",
    "food_sandwich": "A pictogram of a sandwich",
    "food_soup": "A pictogram of a bowl of soup with steam",
    "food_vegetables": "A pictogram of vegetables (carrot, broccoli)",
    "food_cereal": "A pictogram of a bowl of cereal",
    "food_yogurt": "A pictogram of a yogurt cup with spoon",
    "food_snack": "A pictogram of snack foods",
    
    # Actions
    "act_play": "A pictogram of a child playing with toys",
    "act_read": "A pictogram of a person reading an open book",
    "act_watch": "A pictogram of a person watching a TV screen",
    "act_listen": "A pictogram of a person with hand to ear listening",
    "act_sleep": "A pictogram of a person sleeping with ZZZ",
    "act_wake_up": "A pictogram of a person waking up stretching",
    "act_bath": "A pictogram of a bathtub with bubbles",
    "act_brush_teeth": "A pictogram of toothbrush brushing teeth",
    "act_potty": "A pictogram of a toilet",
    "act_wash_hands": "A pictogram of hands being washed with water",
    "act_walk": "A pictogram of a person walking",
    "act_run": "A pictogram of a person running",
    "act_jump": "A pictogram of a person jumping",
    "act_sit": "A pictogram of a person sitting in a chair",
    "act_stand": "A pictogram of a person standing upright",
    "act_hug": "A pictogram of two people hugging",
    "act_kiss": "A pictogram of lips or kiss gesture",
    "act_wave": "A pictogram of a hand waving hello/goodbye",
    "act_sing": "A pictogram of a person singing with music notes",
    "act_dance": "A pictogram of a person dancing",
    "act_draw": "A pictogram of a hand drawing with crayon",
    "act_color": "A pictogram of crayons coloring",
    "act_write": "A pictogram of a hand writing with pencil",
    "act_cut": "A pictogram of scissors cutting",
    "act_open": "A pictogram of a door or box opening",
    "act_close": "A pictogram of a door or box closing",
    "act_push": "A pictogram of hands pushing forward",
    "act_pull": "A pictogram of hands pulling back",
    "act_throw": "A pictogram of a person throwing a ball",
    "act_catch": "A pictogram of hands catching a ball",
    
    # People
    "ppl_me": "A pictogram of a person pointing to themselves",
    "ppl_you": "A pictogram of a hand pointing outward",
    "ppl_mama": "A pictogram of a mother figure, woman with caring pose",
    "ppl_dada": "A pictogram of a father figure, man",
    "ppl_mommy": "A pictogram of a mother with child",
    "ppl_daddy": "A pictogram of a father with child",
    "ppl_baby": "A pictogram of a baby in diaper",
    "ppl_sister": "A pictogram of a girl, sister figure",
    "ppl_brother": "A pictogram of a boy, brother figure",
    "ppl_grandma": "A pictogram of an elderly woman, grandmother",
    "ppl_grandpa": "A pictogram of an elderly man, grandfather",
    "ppl_aunt": "A pictogram of a woman, aunt figure",
    "ppl_uncle": "A pictogram of a man, uncle figure",
    "ppl_cousin": "A pictogram of children together, cousins",
    "ppl_friend": "A pictogram of two friends together",
    "ppl_teacher": "A pictogram of a teacher at a board",
    "ppl_doctor": "A pictogram of a doctor with stethoscope",
    "ppl_therapist": "A pictogram of a therapist/helper",
    "ppl_helper": "A pictogram of a caregiver/helper",
    "ppl_boy": "A pictogram of a boy",
    "ppl_girl": "A pictogram of a girl",
    "ppl_man": "A pictogram of an adult man",
    "ppl_woman": "A pictogram of an adult woman",
    "ppl_everyone": "A pictogram of a group of people together",
    
    # Places
    "place_home": "A pictogram of a house with roof and door",
    "place_school": "A pictogram of a school building",
    "place_park": "A pictogram of a playground with trees",
    "place_store": "A pictogram of a store/shop building",
    "place_mall": "A pictogram of a shopping mall",
    "place_restaurant": "A pictogram of a restaurant with table",
    "place_hospital": "A pictogram of a hospital with cross symbol",
    "place_church": "A pictogram of a church building",
    "place_car": "A pictogram of a car vehicle",
    "place_bus": "A pictogram of a bus",
    "place_outside": "A pictogram of outdoor scene with sun and trees",
    "place_inside": "A pictogram of indoor room",
    "place_bedroom": "A pictogram of a bedroom with bed",
    "place_bathroom": "A pictogram of a bathroom",
    "place_kitchen": "A pictogram of a kitchen with stove",
    "place_living_room": "A pictogram of a living room with couch",
    "place_yard": "A pictogram of a backyard with grass",
    "place_pool": "A pictogram of a swimming pool",
    "place_beach": "A pictogram of a beach with waves and sand",
    "place_playground": "A pictogram of playground equipment",
    
    # Things
    "thing_toy": "A pictogram of a teddy bear toy",
    "thing_ball": "A pictogram of a round colorful ball",
    "thing_blocks": "A pictogram of stacking blocks",
    "thing_doll": "A pictogram of a doll",
    "thing_car_toy": "A pictogram of a toy car",
    "thing_puzzle": "A pictogram of puzzle pieces",
    "thing_book": "A pictogram of a closed book",
    "thing_phone": "A pictogram of a smartphone",
    "thing_tablet": "A pictogram of a tablet device",
    "thing_tv": "A pictogram of a television screen",
    "thing_music": "A pictogram of music notes",
    "thing_blanket": "A pictogram of a soft blanket",
    "thing_pillow": "A pictogram of a pillow",
    "thing_bed": "A pictogram of a bed",
    "thing_chair": "A pictogram of a chair",
    "thing_table": "A pictogram of a table",
    "thing_shoes": "A pictogram of a pair of shoes",
    "thing_clothes": "A pictogram of a shirt/clothing",
    "thing_diaper": "A pictogram of a diaper",
    "thing_cup": "A pictogram of a drinking cup",
    "thing_plate": "A pictogram of a plate",
    "thing_spoon": "A pictogram of a spoon",
    "thing_bag": "A pictogram of a bag/backpack",
    "thing_crayons": "A pictogram of crayons",
    "thing_paper": "A pictogram of paper sheets",
    
    # Descriptors
    "desc_big": "A pictogram showing big/large with expanding arrows",
    "desc_small": "A pictogram showing small/little with shrinking arrows",
    "desc_hot": "A pictogram of something hot with heat waves",
    "desc_cold": "A pictogram of something cold with ice crystals",
    "desc_fast": "A pictogram showing speed with motion lines",
    "desc_slow": "A pictogram showing slow movement, turtle",
    "desc_loud": "A pictogram of loud sound with big sound waves",
    "desc_quiet": "A pictogram of finger to lips, shush gesture",
    "desc_good": "A pictogram of thumbs up, positive",
    "desc_bad": "A pictogram of thumbs down, negative",
    "desc_yucky": "A pictogram of disgusted face",
    "desc_yummy": "A pictogram of happy face licking lips",
    "desc_pretty": "A pictogram of a flower or star, beautiful",
    "desc_funny": "A pictogram of laughing face",
    "desc_scary": "A pictogram of scared face with ghost",
    "desc_soft": "A pictogram of fluffy cloud or pillow",
    "desc_hard": "A pictogram of a rock or hard surface",
    "desc_wet": "A pictogram of water drops, wet",
    "desc_dry": "A pictogram of sun drying, dry",
    "desc_dirty": "A pictogram of muddy/dirty spots",
    
    # Time
    "time_now": "A pictogram of a clock with NOW emphasis",
    "time_later": "A pictogram of a clock with future arrow",
    "time_wait": "A pictogram of hourglass or person waiting",
    "time_again": "A pictogram of circular arrow, repeat",
    "time_today": "A pictogram of calendar with today marked",
    "time_tomorrow": "A pictogram of calendar with tomorrow arrow",
    "time_yesterday": "A pictogram of calendar with back arrow",
    "time_morning": "A pictogram of sunrise",
    "time_afternoon": "A pictogram of sun high in sky",
    "time_night": "A pictogram of moon and stars",
    "time_before": "A pictogram of arrow pointing backward",
    "time_after": "A pictogram of arrow pointing forward",
    "time_first": "A pictogram of number 1 or first position",
    "time_next": "A pictogram of arrow to next item",
    "time_last": "A pictogram of final/end marker",
    
    # Questions
    "q_what": "A pictogram of a large question mark",
    "q_where": "A pictogram of a location pin with question",
    "q_who": "A pictogram of a person silhouette with question",
    "q_when": "A pictogram of a clock with question mark",
    "q_why": "A pictogram of thinking bubble with question",
    "q_how": "A pictogram of gears/tools with question",
    "q_which": "A pictogram of multiple options with question",
    "q_can_i": "A pictogram of person raising hand asking",
    "q_whats_this": "A pictogram of pointing at object with question",
    "q_where_is": "A pictogram of searching/looking with question",
    
    # Social
    "soc_hi": "A pictogram of a hand waving hello",
    "soc_bye": "A pictogram of a hand waving goodbye",
    "soc_good_morning": "A pictogram of sunrise with happy face",
    "soc_good_night": "A pictogram of moon with sleepy face",
    "soc_how_are_you": "A pictogram of person with question asking about feelings",
    "soc_im_fine": "A pictogram of happy person with thumbs up",
    "soc_excuse_me": "A pictogram of polite hand gesture",
    "soc_im_sorry": "A pictogram of apologetic expression",
    "soc_its_okay": "A pictogram of reassuring gesture, OK sign",
    "soc_i_love_you": "A pictogram of heart with person",
    "soc_my_turn": "A pictogram of person pointing to self",
    "soc_your_turn": "A pictogram of person pointing outward",
    "soc_lets_play": "A pictogram of two people playing together",
    "soc_come_here": "A pictogram of beckoning gesture",
    "soc_look_at_me": "A pictogram of pointing to eyes",
    
    # Body
    "body_head": "A pictogram of a head",
    "body_eyes": "A pictogram of pair of eyes",
    "body_ears": "A pictogram of an ear",
    "body_nose": "A pictogram of a nose",
    "body_mouth": "A pictogram of a mouth/lips",
    "body_teeth": "A pictogram of teeth/smile",
    "body_hair": "A pictogram of hair on head",
    "body_hand": "A pictogram of a hand",
    "body_arm": "A pictogram of an arm",
    "body_leg": "A pictogram of a leg",
    "body_foot": "A pictogram of a foot",
    "body_tummy": "A pictogram of stomach/belly",
    "body_back": "A pictogram of a back",
    "body_bottom": "A pictogram indicating bottom/seat",
    "body_finger": "A pictogram of a pointing finger",
}

def build_prompt(symbol_id: str, symbol_text: str) -> str:
    """Build the full prompt for DALL-E 3."""
    visual_desc = SYMBOL_VISUALS.get(symbol_id, f"A simple pictogram representing the meaning of '{symbol_text}'")
    return f"{AAC_STYLE}\n\n{AAC_CONSTRAINTS}\n\nBackground: {_bg_instruction()}\n\nCreate: {visual_desc}"

def generate_symbol_image(symbol: dict, category: dict) -> bool:
    """Generate image for a single symbol."""
    symbol_id = symbol["id"]
    cat_id = category["id"]
    
    output_path = IMAGE_OUTPUT_DIR / cat_id / f"{symbol_id}.png"
    prompt = build_prompt(symbol_id, symbol["text"])
    
    success = generate_image(prompt, output_path)
    
    # Rate limiting - DALL-E 3 has rate limits
    time.sleep(1.5)
    
    return success

def main():
    print("🎨 Liora AAC Image Generator (DALL-E 3)")
    print("=" * 50)
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not found in .env")
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
    print(f"📊 Will generate {total_symbols} images with DALL-E 3\n")
    
    generated = 0
    failed = 0
    
    preview_ids_raw = os.getenv("PREVIEW_IDS", "").strip()
    preview_ids = [s.strip() for s in preview_ids_raw.split(",") if s.strip()] if preview_ids_raw else None

    only_categories = os.getenv("ONLY_CATEGORIES", "").strip()
    limit_per_category = os.getenv("LIMIT_PER_CATEGORY", "").strip()
    only_set = set([c.strip() for c in only_categories.split(",") if c.strip()]) if only_categories else None
    limit_n = int(limit_per_category) if limit_per_category else None

    # Generate images
    for cat in categories:
        if only_set is not None and cat["id"] not in only_set:
            continue
        print(f"\n🏷️  Category: {cat['name']} ({cat['emoji']})")
        symbols_iter = cat["symbols"]
        if limit_n is not None:
            symbols_iter = symbols_iter[:limit_n]

        for symbol in symbols_iter:
            if preview_ids is not None and symbol["id"] not in preview_ids:
                continue
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
