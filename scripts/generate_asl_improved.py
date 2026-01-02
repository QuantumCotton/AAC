import os
import json
import requests
from pathlib import Path
import time

# Read OpenAI key directly from .env file
def read_openai_key():
    env_path = Path(__file__).parent.parent / ".env"
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('OPENAI_API_KEY=') and 'sk-proj-' in line:
                key = line.split('=', 1)[1].strip()
                return key
    return None

OPENAI_API_KEY = read_openai_key()

if not OPENAI_API_KEY:
    print("❌ Could not read OPENAI_API_KEY from .env file")
    exit(1)

# Load ASL words data
asl_data_path = Path(__file__).parent.parent / "src" / "data" / "asl_words.json"
with open(asl_data_path, 'r', encoding='utf-8') as f:
    asl_data = json.load(f)

# Category colors (consistent hex backgrounds)
CATEGORY_COLORS = {
    "basics": "#E9D5FF",      # Light purple
    "family": "#FBCFE8",      # Light pink
    "food": "#FED7AA",        # Light orange
    "animals": "#BBF7D0",     # Light green
    "feelings": "#FEF08A",    # Light yellow
    "actions": "#BFDBFE",     # Light blue
    "things": "#DDD6FE"       # Light lavender
}

# Detailed ASL sign descriptions for AAC device icons
ASL_DESCRIPTIONS = {
    # Basics & Manners
    "hello": "Simple icon: One hand held up at head level, palm facing forward, fingers together in a flat hand shape. This is a waving gesture. Single hand only.",
    "please": "Simple icon: One hand with palm flat against the chest, making a small circular motion. Single hand only, shown from the front.",
    "thank you": "Simple icon: One hand starting at the chin/mouth area with fingertips touching the lips, then moving forward and slightly down. Single hand only.",
    "sorry": "Simple icon: One hand in a fist shape making a circular rubbing motion on the chest. Single hand only, front view.",
    "yes": "Simple icon: One hand in a fist shape (like holding something), moving up and down in a nodding motion. Single hand only.",
    "no": "Simple icon: One hand with index and middle fingers extended, tapping together with the thumb (like a mouth closing). Single hand only.",
    "help": "Simple icon: One hand (fist) placed on top of the other hand (flat palm facing up), both hands lifting upward together. Two hands shown clearly.",
    "more": "Simple icon: Both hands with fingertips touching together in front of the body, forming a peak shape. Two hands, front view, fingertips meeting.",
    
    # Family & People
    "mom": "Simple icon: One hand with thumb extended, tapping the chin area. Single hand only, side view showing the chin tap.",
    "dad": "Simple icon: One hand with thumb extended, tapping the forehead area. Single hand only, side view showing the forehead tap.",
    "baby": "Simple icon: Both arms crossed in a cradling motion, as if rocking a baby. Two hands/arms shown.",
    "friend": "Simple icon: Two index fingers hooking together, then switching positions. Show both hands with index fingers extended and hooked.",
    "boy": "Simple icon: One hand at the forehead making a cap-grabbing motion. Single hand only.",
    "girl": "Simple icon: One hand at the chin/jaw area with thumb tracing along the jawline. Single hand only.",
    
    # Food & Drink
    "eat": "Simple icon: One hand with fingertips together, moving toward the mouth. Single hand only, side view.",
    "drink": "Simple icon: One hand in a C-shape (like holding a cup) moving toward the mouth. Single hand only.",
    "milk": "Simple icon: One hand making a squeezing/milking motion (fist opening and closing). Single hand only.",
    "water": "Simple icon: One hand forming a 'W' shape (three fingers up) tapping the chin. Single hand only.",
    "apple": "Simple icon: One hand in a fist with knuckle of index finger twisting at the cheek. Single hand only.",
    "cookie": "Simple icon: One hand with fingertips making a twisting motion on the other palm (like a cookie cutter). Two hands shown.",
    
    # Animals
    "cat": "Simple icon: One hand with thumb and index finger pinched, making a whisker-pulling motion from the cheek outward. Single hand only.",
    "dog": "Simple icon: One hand patting the thigh and snapping fingers (calling a dog). Single hand only.",
    "bird": "Simple icon: One hand at the mouth with index finger and thumb opening and closing (like a beak). Single hand only.",
    "fish": "Simple icon: One hand flat, moving in a swimming motion forward. Single hand only.",
    
    # Feelings & Emotions
    "happy": "Simple icon: One hand with palm flat, brushing upward on the chest in a circular motion. Single hand only.",
    "sad": "Simple icon: Both hands with fingers spread, moving downward in front of the face (like tears falling). Two hands shown.",
    "love": "Simple icon: Both hands in fists crossed over the chest in an X shape. Two hands shown clearly.",
    "angry": "Simple icon: One hand with fingers spread like claws, pulling away from the face. Single hand only.",
    
    # Actions & Verbs
    "go": "Simple icon: Both hands with index fingers pointing, moving forward in the same direction. Two hands, index fingers extended.",
    "stop": "Simple icon: One hand flat (like a stop sign) with palm facing forward, held up at shoulder height. Single hand only.",
    "play": "Simple icon: Both hands with thumbs and pinkies extended (Y-shape), twisting back and forth. Two hands shown.",
    "sleep": "Simple icon: One hand flat, placed against the side of the tilted head. Single hand only.",
    "look": "Simple icon: One hand with index and middle fingers extended (V-shape), pointing from the eyes forward. Single hand only.",
    "listen": "Simple icon: One hand cupped behind the ear. Single hand only.",
}

def generate_asl_prompt(word, category):
    """Generate an improved DALL-E prompt for AAC-style ASL icons"""
    
    # Get description or use generic
    description = ASL_DESCRIPTIONS.get(word, 
        f"Simple icon: Hand gesture for the ASL sign '{word}'. Clear, simple hand position shown from the best angle for recognition.")
    
    # Get category color
    bg_color = CATEGORY_COLORS.get(category, "#E5E7EB")
    
    prompt = f"""Create a simple, clear icon illustration for an AAC (Augmentative and Alternative Communication) learning device.

SUBJECT: American Sign Language (ASL) sign for the word '{word.upper()}'
DESCRIPTION: {description}

STYLE REQUIREMENTS:
- Simple, clean vector-style illustration
- Solid flat background color: {bg_color}
- Hand(s) should be simplified but anatomically clear
- Neutral skin tone (light peachy beige)
- No face, no body - just hand(s) and minimal arm if needed
- Clear, bold outlines
- Front view or side view (whichever shows the sign most clearly)
- Icon should be centered in the frame
- Educational, child-friendly style
- Similar to AAC device icons or sign language flashcards

AVOID:
- Photorealistic hands
- Complex backgrounds or gradients
- Multiple hand positions or motion blur
- Faces or full bodies
- Shadows or complex lighting
- Text or labels

This is for a children's learning app, so clarity and simplicity are most important."""

    return prompt

def generate_image_dalle(word, category, output_path):
    """Generate an image using DALL-E 3"""
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = generate_asl_prompt(word, category)
    
    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "quality": "standard",
        "style": "natural"  # Use natural style for cleaner, simpler images
    }
    
    print(f"🖐️  Generating ASL icon for '{word.upper()}' ({category})...")
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            image_url = data["data"][0]["url"]
            
            # Download the image
            img_response = requests.get(image_url, timeout=30)
            if img_response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(img_response.content)
                
                print(f"   ✅ Saved: {output_path.name}")
                return True
            else:
                print(f"   ❌ Failed to download image")
                return False
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"   ❌ API Error {response.status_code}:")
            print(f"   {json.dumps(error_data, indent=2)}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def generate_sample_asl():
    """Generate 5 improved sample ASL images for testing"""
    
    # Test with 5 diverse signs (different hand configurations)
    test_samples = [
        {"word": "hello", "category": "basics"},
        {"word": "more", "category": "basics"},
        {"word": "eat", "category": "food"},
        {"word": "cat", "category": "animals"},
        {"word": "love", "category": "feelings"}
    ]
    
    OUTPUT_DIR = Path("public/assets/images/asl/test_improved")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"🎨 Generating 5 Improved ASL Icons with DALL-E 3")
    print(f"📋 Using detailed descriptions and consistent backgrounds\n")
    print(f"📁 Output directory: {OUTPUT_DIR}\n")
    
    success_count = 0
    for i, sample in enumerate(test_samples, 1):
        output_path = OUTPUT_DIR / f"{sample['word']}.png"
        
        print(f"[{i}/5] ", end="")
        if generate_image_dalle(sample["word"], sample["category"], output_path):
            success_count += 1
        
        # Rate limit: DALL-E 3 allows ~5 requests per minute
        if i < len(test_samples):
            print(f"   ⏳ Waiting 15 seconds (rate limit)...\n")
            time.sleep(15)
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully generated {success_count}/{len(test_samples)} improved ASL icons")
    print(f"{'='*60}")
    
    if success_count > 0:
        print(f"\n📂 Images saved to: {OUTPUT_DIR.absolute()}")
        print(f"\n💡 Check the images to verify:")
        print(f"   - Hands are clear and anatomically correct")
        print(f"   - Backgrounds are solid colors (no gradients/patterns)")
        print(f"   - Signs are recognizable and simple")
        print(f"   - Style is consistent across all icons")
    
    return success_count == len(test_samples)

if __name__ == "__main__":
    success = generate_sample_asl()
    
    if not success:
        print(f"\n⚠️  Some images failed. Consider alternative services:")
        print(f"   1. Midjourney API (best for illustrations)")
        print(f"   2. Stable Diffusion with ControlNet (hand pose control)")
        print(f"   3. Replicate.com (various models available)")
        print(f"   4. Manual illustration or stock ASL icon sets")
