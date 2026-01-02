"""
Generate ASL hand sign icons using Google Gemini 3 Pro Image Preview (Nano Banana Pro)
Uses the official Google GenAI SDK with conversational image generation
"""
import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
import time

load_dotenv()

# Read Google Gemini API key from .env
def read_gemini_key():
    env_path = Path(__file__).parent.parent / ".env"
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('GOOGLE_GEMINI_API_KEY='):
                key = line.split('=', 1)[1].strip()
                return key
    return None

GEMINI_API_KEY = read_gemini_key()

if not GEMINI_API_KEY:
    print("❌ GOOGLE_GEMINI_API_KEY not found in .env file")
    exit(1)

print(f"🔑 Google Gemini API Key loaded ({len(GEMINI_API_KEY)} characters)")
print()

# Try to import the Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    SDK_AVAILABLE = True
    print("✅ Google GenAI SDK available")
except ImportError:
    SDK_AVAILABLE = False
    print("⚠️  Google GenAI SDK not installed")
    print("   Install with: pip install google-genai")
    print("   Falling back to REST API...")

# Load ASL data
asl_data_path = Path(__file__).parent.parent / "src" / "data" / "asl_words.json"
with open(asl_data_path, 'r', encoding='utf-8') as f:
    asl_data = json.load(f)

# Category colors (solid hex backgrounds)
CATEGORY_COLORS = {
    "basics": "#E9D5FF",      # Light purple
    "family": "#FBCFE8",      # Light pink
    "food": "#FED7AA",        # Light orange
    "animals": "#BBF7D0",     # Light green
    "feelings": "#FEF08A",    # Light yellow
    "actions": "#BFDBFE",     # Light blue
    "things": "#DDD6FE"       # Light lavender
}

# Detailed ASL descriptions for AAC icons
ASL_DESCRIPTIONS = {
    "hello": "One hand raised at head level, palm facing forward, fingers together in a flat hand shape (waving gesture). Single hand only, front view.",
    "please": "One hand with palm flat against the chest, making a small circular motion. Single hand only, front view.",
    "thank you": "One hand starting at the chin/mouth with fingertips touching lips, then moving forward. Single hand only, side view.",
    "more": "Both hands with all fingertips touching together in front of body, forming a peak. Two hands clearly shown, front view.",
    "eat": "One hand with fingertips together, moving toward the mouth. Single hand only, side view.",
    "cat": "One hand with thumb and index finger pinched, making a whisker-pulling motion from cheek. Single hand only, side view.",
    "love": "Both hands in fists crossed over the chest in an X shape. Two hands clearly shown, front view.",
    "mom": "One hand with thumb extended, tapping the chin. Single hand only, side view.",
    "dad": "One hand with thumb extended, tapping the forehead. Single hand only, side view.",
    "help": "One fist on top of flat palm, both lifting upward. Two hands clearly shown, front view.",
}

def generate_asl_prompt(word, category):
    """Generate Gemini-optimized prompt for AAC-style ASL icons"""
    
    description = ASL_DESCRIPTIONS.get(word, 
        f"Hand gesture for ASL sign '{word}'. Clear, simple hand position.")
    
    bg_color = CATEGORY_COLORS.get(category, "#E5E7EB")
    
    prompt = f"""Create a simple, clean icon for an AAC learning device showing the American Sign Language (ASL) sign for '{word.upper()}'.

HAND DESCRIPTION: {description}

STYLE REQUIREMENTS:
- Flat, simple vector illustration style
- Solid background color: {bg_color} (no gradients, patterns, or frames)
- Hand(s) should be simplified but anatomically correct
- Neutral peachy-beige skin tone
- NO face, NO body, NO text - ONLY hand(s)
- Clear bold outlines around hands
- Centered composition
- Icon should look like an educational flashcard
- Similar to AAC device icons or sign language teaching materials

CRITICAL:
- Background must be completely solid {bg_color} color
- No shadows, gradients, or decorative elements
- Focus entirely on the hand gesture clarity
- Suitable for children ages 3-8"""

    return prompt

def generate_with_sdk(word, category, output_path):
    """Generate using Google GenAI SDK"""
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = generate_asl_prompt(word, category)
    
    print(f"🖐️  Generating ASL icon for '{word.upper()}' ({category})...")
    
    try:
        # Use the correct API structure for Gemini image generation
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[prompt],
            config={
                "response_modalities": ["IMAGE"],
                "image_config": {
                    "aspect_ratio": "1:1",
                    "image_size": "1K"
                }
            }
        )
        
        for part in response.parts:
            if part.inline_data is not None:
                image = part.as_image()
                output_path.parent.mkdir(parents=True, exist_ok=True)
                image.save(output_path)
                print(f"   ✅ Saved: {output_path.name}")
                return True
        
        print(f"   ❌ No image in response")
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_with_rest(word, category, output_path):
    """Generate using REST API (fallback)"""
    import requests
    
    prompt = generate_asl_prompt(word, category)
    
    print(f"🖐️  Generating ASL icon for '{word.upper()}' ({category})...")
    
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": "1:1",
                "imageSize": "1K"
            }
        }
    }
    
    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract image from response
            if "candidates" in data and len(data["candidates"]) > 0:
                parts = data["candidates"][0]["content"]["parts"]
                for part in parts:
                    if "inlineData" in part:
                        image_data = part["inlineData"]["data"]
                        image_bytes = base64.b64decode(image_data)
                        
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(output_path, "wb") as f:
                            f.write(image_bytes)
                        
                        print(f"   ✅ Saved: {output_path.name}")
                        return True
            
            print(f"   ❌ No image in response")
            return False
        else:
            print(f"   ❌ API Error {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_gemini_pro():
    """Test Gemini 3 Pro Image with 5 sample ASL signs"""
    
    test_samples = [
        {"word": "hello", "category": "basics"},
        {"word": "more", "category": "basics"},
        {"word": "eat", "category": "food"},
        {"word": "cat", "category": "animals"},
        {"word": "love", "category": "feelings"}
    ]
    
    OUTPUT_DIR = Path("public/assets/images/asl/test_gemini_pro")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"🎨 Generating 5 ASL Icons with Gemini 3 Pro Image (Nano Banana Pro)")
    print(f"📋 Using solid color backgrounds and detailed hand descriptions\n")
    print(f"📁 Output directory: {OUTPUT_DIR}\n")
    
    # Force REST API since SDK doesn't support image_config yet
    generate_func = generate_with_rest
    
    success_count = 0
    for i, sample in enumerate(test_samples, 1):
        output_path = OUTPUT_DIR / f"{sample['word']}.png"
        
        print(f"[{i}/5] ", end="")
        if generate_func(sample["word"], sample["category"], output_path):
            success_count += 1
        
        # Rate limit
        if i < len(test_samples):
            print(f"   ⏳ Waiting 10 seconds...\n")
            time.sleep(10)
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully generated {success_count}/{len(test_samples)} ASL icons")
    print(f"{'='*60}")
    
    if success_count > 0:
        print(f"\n📂 Images saved to: {OUTPUT_DIR.absolute()}")
        print(f"\n💡 Check the images:")
        print(f"   - Hands should be anatomically correct")
        print(f"   - Backgrounds should be solid colors (no gradients)")
        print(f"   - Signs should be clear and recognizable")
        print(f"   - Style should be consistent")
    else:
        print(f"\n⚠️  All generations failed. Check:")
        print(f"   1. API key is valid: {GEMINI_API_KEY[:20]}...")
        print(f"   2. Gemini 3 Pro Image Preview is available in your region")
        print(f"   3. API quota/billing is enabled")
    
    return success_count == len(test_samples)

if __name__ == "__main__":
    test_gemini_pro()
