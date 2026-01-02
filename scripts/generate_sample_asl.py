import os
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# We will use DALL-E 3 as the fallback high-quality generator
# since Nano Banana endpoints are not resolving/authenticating.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OUTPUT_DIR = Path("public/assets/images/asl_sample")

def generate_sample_dalle(prompt, filename):
    if not OPENAI_API_KEY:
        print("❌ No OpenAI API key found")
        return False
        
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Enhanced prompt for educational illustration style
    enhanced = f"{prompt}, flat vector art style, educational illustration, simple clean design, solid background, high quality, kid-friendly"
    
    body = {
        "model": "dall-e-3",
        "prompt": enhanced,
        "n": 1,
        "size": "1024x1024",
        "quality": "standard",
        "style": "vivid"
    }
    
    print(f"Generating {filename}...")
    try:
        response = requests.post(url, headers=headers, json=body, timeout=60)
        if response.status_code == 200:
            img_url = response.json()['data'][0]['url']
            img_data = requests.get(img_url).content
            
            with open(filename, 'wb') as f:
                f.write(img_data)
            print(f"✅ Saved to {filename}")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
    # 5 Sample Prompts from our list
    samples = [
        ("more", "child's hands making ASL sign for MORE, fingers touching together, soft pink background #FF6B6B"),
        ("cat", "child's hands making ASL sign for CAT, whisker motion from face, mint green background #95E1D3"),
        ("tree", "child's arm making ASL sign for TREE, arm up and hand waving, nature background"),
        ("happy", "child's hands making ASL sign for HAPPY, brushing up chest, orange background #F8B500"),
        ("book", "child's hands making ASL sign for BOOK, hands opening like a book, blue background")
    ]
    
    print("🎨 Generating 5 Sample ASL Images (DALL-E 3)...")
    for name, prompt in samples:
        filename = OUTPUT_DIR / f"{name}.png"
        generate_sample_dalle(prompt, filename)
        time.sleep(1) # Mild rate limit

if __name__ == "__main__":
    main()
