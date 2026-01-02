#!/usr/bin/env python3
"""Add emoji icons to all symbols in liora_symbols_full.json"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SYMBOLS_FILE = BASE_DIR / "src" / "data" / "liora_symbols_full.json"

# Mapping of symbol IDs to emoji icons
ICON_MAP = {
    # Core Words
    "core_i": "👤", "core_you": "👉", "core_want": "🙋", "core_need": "🆘",
    "core_like": "👍", "core_dont_like": "👎", "core_more": "➕", "core_all_done": "✅",
    "core_help": "🤝", "core_stop": "✋", "core_go": "🚀", "core_yes": "✓",
    "core_no": "❌", "core_please": "🙏", "core_thank_you": "💝", "core_sorry": "😔",
    "core_look": "👀", "core_get": "✊", "core_put": "📥", "core_give": "🎁",
    "core_take": "🤲", "core_make": "🔨", "core_do": "⚡", "core_have": "💎",
    
    # Feelings
    "feel_happy": "😊", "feel_sad": "😢", "feel_angry": "😠", "feel_scared": "😨",
    "feel_tired": "😴", "feel_sick": "🤒", "feel_hurt": "🤕", "feel_love": "❤️",
    "feel_excited": "🤩", "feel_bored": "😑", "feel_hungry": "🍽️", "feel_thirsty": "💧",
    "feel_cold": "🥶", "feel_hot": "🥵", "feel_nervous": "😰", "feel_confused": "😕",
    "feel_frustrated": "😤", "feel_calm": "😌", "feel_proud": "🏆", "feel_silly": "🤪",
    
    # Food & Drink
    "food_eat": "🍴", "food_drink": "🥤", "food_water": "💧", "food_milk": "🥛",
    "food_juice": "🧃", "food_apple": "🍎", "food_banana": "🍌", "food_orange": "🍊",
    "food_grapes": "🍇", "food_strawberry": "🍓", "food_cookie": "🍪", "food_crackers": "🥨",
    "food_chips": "🍟", "food_candy": "🍬", "food_ice_cream": "🍦", "food_bread": "🍞",
    "food_rice": "🍚", "food_noodles": "🍜", "food_chicken": "🍗", "food_fish": "🐟",
    "food_meat": "🥩", "food_egg": "🥚", "food_cheese": "🧀", "food_pizza": "🍕",
    "food_sandwich": "🥪", "food_soup": "🍲", "food_vegetables": "🥦", "food_cereal": "🥣",
    "food_yogurt": "🥛", "food_snack": "🍿",
    
    # Actions
    "act_play": "🎮", "act_read": "📖", "act_watch": "📺", "act_listen": "👂",
    "act_sleep": "😴", "act_wake_up": "⏰", "act_bath": "🛁", "act_brush_teeth": "🪥",
    "act_potty": "🚽", "act_wash_hands": "🧼", "act_walk": "🚶", "act_run": "🏃",
    "act_jump": "🦘", "act_sit": "🪑", "act_stand": "🧍", "act_hug": "🤗",
    "act_kiss": "💋", "act_wave": "👋", "act_sing": "🎤", "act_dance": "💃",
    "act_draw": "🖍️", "act_color": "🎨", "act_write": "✏️", "act_cut": "✂️",
    "act_open": "📂", "act_close": "📁", "act_push": "👐", "act_pull": "🤏",
    "act_throw": "🤾", "act_catch": "🧤",
    
    # People
    "ppl_me": "👤", "ppl_you": "👉", "ppl_mama": "👩", "ppl_dada": "👨",
    "ppl_mommy": "👩‍👧", "ppl_daddy": "👨‍👧", "ppl_baby": "👶", "ppl_sister": "👧",
    "ppl_brother": "👦", "ppl_grandma": "👵", "ppl_grandpa": "👴", "ppl_aunt": "👩‍🦱",
    "ppl_uncle": "👨‍🦱", "ppl_cousin": "👫", "ppl_friend": "🧑‍🤝‍🧑", "ppl_teacher": "👩‍🏫",
    "ppl_doctor": "👨‍⚕️", "ppl_therapist": "🧑‍⚕️", "ppl_helper": "🙋‍♀️", "ppl_boy": "👦",
    "ppl_girl": "👧", "ppl_man": "👨", "ppl_woman": "👩", "ppl_everyone": "👥",
    
    # Places
    "place_home": "🏠", "place_school": "🏫", "place_park": "🏞️", "place_store": "🏪",
    "place_mall": "🛒", "place_restaurant": "🍽️", "place_hospital": "🏥", "place_church": "⛪",
    "place_car": "🚗", "place_bus": "🚌", "place_outside": "🌳", "place_inside": "🏠",
    "place_bedroom": "🛏️", "place_bathroom": "🚿", "place_kitchen": "🍳", "place_living_room": "🛋️",
    "place_yard": "🌿", "place_pool": "🏊", "place_beach": "🏖️", "place_playground": "🛝",
    
    # Things
    "thing_toy": "🧸", "thing_ball": "⚽", "thing_blocks": "🧱", "thing_doll": "🎎",
    "thing_car_toy": "🚙", "thing_puzzle": "🧩", "thing_book": "📚", "thing_phone": "📱",
    "thing_tablet": "📲", "thing_tv": "📺", "thing_music": "🎵", "thing_blanket": "🛏️",
    "thing_pillow": "🛏️", "thing_bed": "🛏️", "thing_chair": "🪑", "thing_table": "🪑",
    "thing_shoes": "👟", "thing_clothes": "👕", "thing_diaper": "🩲", "thing_cup": "🥤",
    "thing_plate": "🍽️", "thing_spoon": "🥄", "thing_bag": "🎒", "thing_crayons": "🖍️",
    "thing_paper": "📄",
    
    # Descriptors
    "desc_big": "🔺", "desc_small": "🔹", "desc_hot": "🔥", "desc_cold": "❄️",
    "desc_fast": "⚡", "desc_slow": "🐢", "desc_loud": "🔊", "desc_quiet": "🤫",
    "desc_good": "👍", "desc_bad": "👎", "desc_yucky": "🤢", "desc_yummy": "😋",
    "desc_pretty": "✨", "desc_funny": "😂", "desc_scary": "👻", "desc_soft": "☁️",
    "desc_hard": "🪨", "desc_wet": "💦", "desc_dry": "☀️", "desc_dirty": "💩",
    
    # Time
    "time_now": "⏰", "time_later": "⏳", "time_wait": "⌛", "time_again": "🔄",
    "time_today": "📅", "time_tomorrow": "📆", "time_yesterday": "◀️", "time_morning": "🌅",
    "time_afternoon": "☀️", "time_night": "🌙", "time_before": "⏪", "time_after": "⏩",
    "time_first": "1️⃣", "time_next": "➡️", "time_last": "🏁",
    
    # Questions
    "q_what": "❓", "q_where": "📍", "q_who": "🤔", "q_when": "🕐",
    "q_why": "💭", "q_how": "🔧", "q_which": "👆", "q_can_i": "🙋",
    "q_whats_this": "❔", "q_where_is": "🔍",
    
    # Social
    "soc_hi": "👋", "soc_bye": "👋", "soc_good_morning": "🌅", "soc_good_night": "🌙",
    "soc_how_are_you": "🤗", "soc_im_fine": "👍", "soc_excuse_me": "🙏", "soc_im_sorry": "😔",
    "soc_its_okay": "👌", "soc_i_love_you": "❤️", "soc_my_turn": "🙋", "soc_your_turn": "👉",
    "soc_lets_play": "🎮", "soc_come_here": "🤙", "soc_look_at_me": "👀",
    
    # Body
    "body_head": "🗣️", "body_eyes": "👀", "body_ears": "👂", "body_nose": "👃",
    "body_mouth": "👄", "body_teeth": "🦷", "body_hair": "💇", "body_hand": "🖐️",
    "body_arm": "💪", "body_leg": "🦵", "body_foot": "🦶", "body_tummy": "🫃",
    "body_back": "🔙", "body_bottom": "🍑", "body_finger": "👆",
}

def main():
    print("Adding icons to symbols...")
    
    with open(SYMBOLS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    updated = 0
    for category in data["categories"]:
        for symbol in category["symbols"]:
            symbol_id = symbol["id"]
            if symbol_id in ICON_MAP:
                symbol["icon"] = ICON_MAP[symbol_id]
                updated += 1
            elif "icon" not in symbol:
                symbol["icon"] = "💬"  # Default fallback
                updated += 1
    
    with open(SYMBOLS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Updated {updated} symbols with icons")

if __name__ == "__main__":
    main()
