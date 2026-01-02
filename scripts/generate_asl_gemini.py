import os
import json
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Google Gemini API Key (from .env)
GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_GEMINI_API_KEY not found in .env file")

# Use Gemini 2.5 Flash Image (Nano Banana) endpoint
API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent"

# Output directory
OUTPUT_DIR = Path("public/assets/images/asl")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_image(prompt, output_path):
    """Generate an image using Google Gemini API (Nano Banana)"""
    
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt}
            ]
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": "1:1"
            }
        }
    }
    
    print(f"Generating: {output_path.name}...")
    
    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract image data from response
            if "candidates" in data and len(data["candidates"]) > 0:
                parts = data["candidates"][0]["content"]["parts"]
                
                for part in parts:
                    if "inlineData" in part:
                        image_data = part["inlineData"]["data"]
                        
                        # Decode base64 and save
                        image_bytes = base64.b64decode(image_data)
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(output_path, "wb") as f:
                            f.write(image_bytes)
                        
                        print(f"✅ Saved: {output_path}")
                        return True
            
            print(f"❌ No image in response: {data}")
            return False
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def generate_sample_asl():
    """Generate 5 sample ASL images for testing"""
    
    # Sample words from different categories
    samples = [
        {
            "word": "more",
            "category": "basics",
            "prompt": "Educational illustration of American Sign Language (ASL) hand sign for 'MORE'. Show clear hand position with fingertips touching together. Clean white background, professional educational style, simple and clear for children to learn."
        },
        {
            "word": "cat",
            "category": "animals",
            "prompt": "Educational illustration of American Sign Language (ASL) hand sign for 'CAT'. Show hand making whisker motion near face. Clean white background, professional educational style, simple and clear for children to learn."
        },
        {
            "word": "happy",
            "category": "feelings",
            "prompt": "Educational illustration of American Sign Language (ASL) hand sign for 'HAPPY'. Show hands brushing upward on chest. Clean white background, professional educational style, simple and clear for children to learn."
        },
        {
            "word": "eat",
            "category": "food",
            "prompt": "Educational illustration of American Sign Language (ASL) hand sign for 'EAT'. Show hand moving to mouth. Clean white background, professional educational style, simple and clear for children to learn."
        },
        {
            "word": "mom",
            "category": "family",
            "prompt": "Educational illustration of American Sign Language (ASL) hand sign for 'MOM'. Show open hand tapping chin. Clean white background, professional educational style, simple and clear for children to learn."
        }
    ]
    
    print(f"🎨 Generating 5 Sample ASL Images (Gemini Nano Banana)...\n")
    
    success_count = 0
    for sample in samples:
        category_dir = OUTPUT_DIR / sample["category"]
        output_path = category_dir / f"{sample['word']}.png"
        
        if generate_image(sample["prompt"], output_path):
            success_count += 1
        
        print()  # Blank line between generations
    
    print(f"\n✅ Successfully generated {success_count}/{len(samples)} images")
    return success_count == len(samples)

if __name__ == "__main__":
    generate_sample_asl()
