import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import time

load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

# Output directory
OUTPUT_DIR = Path("public/assets/images/asl")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_image_dalle(prompt, output_path):
    """Generate an image using DALL-E 3"""
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "quality": "standard"
    }
    
    print(f"Generating: {output_path.name}...")
    
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
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, "wb") as f:
                    f.write(img_response.content)
                
                print(f"✅ Saved: {output_path}")
                return True
            else:
                print(f"❌ Failed to download image")
                return False
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def generate_sample_asl():
    """Generate 5 sample ASL images for testing"""
    
    # Sample words with enhanced prompts for DALL-E 3
    samples = [
        {
            "word": "more",
            "category": "basics",
            "prompt": "A clean, professional educational illustration showing two hands performing the American Sign Language (ASL) sign for 'MORE'. Both hands have fingertips touching together in front of the body. The hands are clearly visible against a soft pastel purple background. The illustration style is simple, clear, and perfect for children's educational materials. Photorealistic hands, well-lit, front view."
        },
        {
            "word": "cat",
            "category": "animals",
            "prompt": "A clean, professional educational illustration showing a hand performing the American Sign Language (ASL) sign for 'CAT'. The hand is making a whisker-pulling motion near the cheek. The hand is clearly visible against a soft pastel green background. The illustration style is simple, clear, and perfect for children's educational materials. Photorealistic hand, well-lit, side view showing the motion."
        },
        {
            "word": "happy",
            "category": "feelings",
            "prompt": "A clean, professional educational illustration showing hands performing the American Sign Language (ASL) sign for 'HAPPY'. Both hands are brushing upward on the chest in a circular motion. The hands are clearly visible against a soft pastel yellow background. The illustration style is simple, clear, and perfect for children's educational materials. Photorealistic hands, well-lit, front view."
        },
        {
            "word": "eat",
            "category": "food",
            "prompt": "A clean, professional educational illustration showing a hand performing the American Sign Language (ASL) sign for 'EAT'. The hand is moving toward the mouth with fingers together. The hand is clearly visible against a soft pastel orange background. The illustration style is simple, clear, and perfect for children's educational materials. Photorealistic hand, well-lit, side view."
        },
        {
            "word": "mom",
            "category": "family",
            "prompt": "A clean, professional educational illustration showing a hand performing the American Sign Language (ASL) sign for 'MOM'. The open hand with thumb extended is tapping the chin. The hand is clearly visible against a soft pastel pink background. The illustration style is simple, clear, and perfect for children's educational materials. Photorealistic hand, well-lit, front view."
        }
    ]
    
    print(f"🎨 Generating 5 Sample ASL Images (DALL-E 3)...\n")
    
    success_count = 0
    for i, sample in enumerate(samples):
        category_dir = OUTPUT_DIR / sample["category"]
        output_path = category_dir / f"{sample['word']}.png"
        
        if generate_image_dalle(sample["prompt"], output_path):
            success_count += 1
        
        # Rate limit: DALL-E 3 allows ~5 requests per minute
        if i < len(samples) - 1:
            print("Waiting 15 seconds (rate limit)...")
            time.sleep(15)
        
        print()  # Blank line between generations
    
    print(f"\n✅ Successfully generated {success_count}/{len(samples)} images")
    return success_count == len(samples)

if __name__ == "__main__":
    generate_sample_asl()
