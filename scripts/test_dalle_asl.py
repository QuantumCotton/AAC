import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import time

load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print(f"🔑 Testing OpenAI API Key...")
print(f"Key length: {len(OPENAI_API_KEY) if OPENAI_API_KEY else 0} characters")
print(f"Key prefix: {OPENAI_API_KEY[:20]}..." if OPENAI_API_KEY else "No key found")
print()

if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY not found in .env file")
    exit(1)

# Output directory
OUTPUT_DIR = Path("public/assets/images/asl/test_samples")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_image_dalle(word, prompt, output_path):
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
    
    print(f"🖐️  Generating ASL sign for '{word.upper()}'...")
    
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
    """Generate 5 sample ASL hand sign images for testing"""
    
    # 5 common ASL signs that DALL-E should know well
    samples = [
        {
            "word": "hello",
            "prompt": "A professional educational photograph showing a single hand performing the American Sign Language (ASL) sign for 'HELLO'. The hand is raised near the forehead with fingers together, palm facing outward, making a small saluting motion. Clean, well-lit studio photography with a soft pastel blue gradient background. The hand is clearly visible with natural skin tones. Educational illustration style, perfect for children's learning materials."
        },
        {
            "word": "thank_you",
            "prompt": "A professional educational photograph showing a single hand performing the American Sign Language (ASL) sign for 'THANK YOU'. The hand starts at the chin with fingers touching the lips, then moves forward and down. Clean, well-lit studio photography with a soft pastel pink gradient background. The hand is clearly visible with natural skin tones. Educational illustration style, perfect for children's learning materials."
        },
        {
            "word": "love",
            "prompt": "A professional educational photograph showing two hands performing the American Sign Language (ASL) sign for 'LOVE'. Both hands are crossed over the chest in fists, forming an X shape. Clean, well-lit studio photography with a soft pastel red gradient background. The hands are clearly visible with natural skin tones. Educational illustration style, perfect for children's learning materials."
        },
        {
            "word": "please",
            "prompt": "A professional educational photograph showing a single hand performing the American Sign Language (ASL) sign for 'PLEASE'. The hand is flat with palm facing down, making a circular rubbing motion on the chest. Clean, well-lit studio photography with a soft pastel purple gradient background. The hand is clearly visible with natural skin tones. Educational illustration style, perfect for children's learning materials."
        },
        {
            "word": "yes",
            "prompt": "A professional educational photograph showing a single hand performing the American Sign Language (ASL) sign for 'YES'. The hand is in a fist shape, moving up and down like a nodding head. Clean, well-lit studio photography with a soft pastel green gradient background. The hand is clearly visible with natural skin tones. Educational illustration style, perfect for children's learning materials."
        }
    ]
    
    print(f"🎨 Generating 5 Sample ASL Hand Signs with DALL-E 3\n")
    print(f"📁 Output directory: {OUTPUT_DIR}\n")
    
    success_count = 0
    for i, sample in enumerate(samples, 1):
        output_path = OUTPUT_DIR / f"{sample['word']}.png"
        
        print(f"[{i}/5] ", end="")
        if generate_image_dalle(sample["word"], sample["prompt"], output_path):
            success_count += 1
        
        # Rate limit: DALL-E 3 allows ~5 requests per minute on free tier
        if i < len(samples):
            print(f"   ⏳ Waiting 15 seconds (rate limit)...\n")
            time.sleep(15)
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully generated {success_count}/{len(samples)} ASL hand sign images")
    print(f"{'='*60}")
    
    if success_count > 0:
        print(f"\n📂 Images saved to: {OUTPUT_DIR.absolute()}")
    
    return success_count == len(samples)

if __name__ == "__main__":
    generate_sample_asl()
