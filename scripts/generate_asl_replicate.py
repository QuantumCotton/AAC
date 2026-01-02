"""
Generate ASL hand sign icons using Replicate.com's Stable Diffusion XL
This service is better for hands than DALL-E 3
"""
import os
import json
import requests
import base64
from pathlib import Path
import time

# Replicate API setup
# Get your API key from: https://replicate.com/account/api-tokens
REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY", "")

if not REPLICATE_API_KEY:
    print("⚠️  REPLICATE_API_KEY not found in .env")
    print("Get your key from: https://replicate.com/account/api-tokens")
    print("Add to .env: REPLICATE_API_KEY=r8_xxxxx")
    exit(1)

# Load ASL data
asl_data_path = Path(__file__).parent.parent / "src" / "data" / "asl_words.json"
with open(asl_data_path, 'r', encoding='utf-8') as f:
    asl_data = json.load(f)

# Category colors (solid hex backgrounds)
CATEGORY_COLORS = {
    "basics": "E9D5FF",      # Light purple
    "family": "FBCFE8",      # Light pink
    "food": "FED7AA",        # Light orange
    "animals": "BBF7D0",     # Light green
    "feelings": "FEF08A",    # Light yellow
    "actions": "BFDBFE",     # Light blue
    "things": "DDD6FE"       # Light lavender
}

def generate_asl_icon_replicate(word, category, output_path):
    """Generate ASL icon using Replicate's SDXL"""
    
    bg_color = CATEGORY_COLORS.get(category, "E5E7EB")
    
    # Simplified prompt for SDXL
    prompt = f"""simple flat icon illustration of ASL sign language hand gesture for '{word}', 
clean vector style, minimal design, educational icon, 
solid #{bg_color} background, centered composition,
clear hand shape, no face, no body, icon design, 
flat colors, bold outlines, children's learning app style"""
    
    negative_prompt = """photorealistic, photograph, realistic skin, shadows, 
complex background, gradient, pattern, multiple hands, face, body, 
text, watermark, blurry, distorted fingers"""
    
    print(f"🖐️  Generating '{word}' ({category})...")
    
    # Use Replicate's SDXL model
    headers = {
        "Authorization": f"Token {REPLICATE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",  # SDXL 1.0
        "input": {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": 1024,
            "height": 1024,
            "num_outputs": 1,
            "scheduler": "K_EULER",
            "num_inference_steps": 30,
            "guidance_scale": 7.5
        }
    }
    
    try:
        # Create prediction
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code != 201:
            print(f"   ❌ API Error {response.status_code}: {response.text}")
            return False
        
        prediction = response.json()
        prediction_id = prediction["id"]
        
        # Poll for completion
        max_wait = 60  # seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = requests.get(
                f"https://api.replicate.com/v1/predictions/{prediction_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"   ❌ Status check failed: {response.status_code}")
                return False
            
            result = response.json()
            status = result["status"]
            
            if status == "succeeded":
                # Download image
                image_url = result["output"][0]
                img_response = requests.get(image_url, timeout=30)
                
                if img_response.status_code == 200:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, "wb") as f:
                        f.write(img_response.content)
                    print(f"   ✅ Saved: {output_path.name}")
                    return True
                else:
                    print(f"   ❌ Failed to download image")
                    return False
            
            elif status == "failed":
                print(f"   ❌ Generation failed: {result.get('error', 'Unknown error')}")
                return False
            
            # Still processing
            time.sleep(2)
        
        print(f"   ❌ Timeout waiting for generation")
        return False
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_replicate():
    """Test Replicate with 3 sample ASL signs"""
    
    test_samples = [
        {"word": "hello", "category": "basics"},
        {"word": "eat", "category": "food"},
        {"word": "cat", "category": "animals"}
    ]
    
    OUTPUT_DIR = Path("public/assets/images/asl/test_replicate")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"🎨 Testing Replicate SDXL for ASL Icons\n")
    print(f"📁 Output: {OUTPUT_DIR}\n")
    
    success_count = 0
    for i, sample in enumerate(test_samples, 1):
        output_path = OUTPUT_DIR / f"{sample['word']}.png"
        
        print(f"[{i}/3] ", end="")
        if generate_asl_icon_replicate(sample["word"], sample["category"], output_path):
            success_count += 1
        
        if i < len(test_samples):
            print(f"   ⏳ Waiting 3 seconds...\n")
            time.sleep(3)
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully generated {success_count}/{len(test_samples)} icons")
    print(f"{'='*60}")
    
    if success_count == 0:
        print(f"\n⚠️  Replicate failed. Consider:")
        print(f"   1. Using pre-made ASL icon sets (guaranteed accuracy)")
        print(f"   2. Hiring an illustrator for custom icons")
        print(f"   3. Using Midjourney (requires Discord bot)")
    
    return success_count > 0

if __name__ == "__main__":
    test_replicate()
