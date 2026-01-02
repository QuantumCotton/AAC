import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Key from .env
API_KEY = os.getenv("OPENAI_API_KEY")

def test_openai_dalle():
    print(f"Testing OpenAI Key: {API_KEY[:10]}...{API_KEY[-4:]}")
    
    url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    try:
        # First test listing models (cheap)
        r = requests.get(url, headers=headers, timeout=10)
        print(f"List Models Status: {r.status_code}")
        if r.status_code == 200:
            print("✅ Key works for listing models!")
            
            # Now test image gen
            print("Testing Image Generation (DALL-E 3)...")
            img_url = "https://api.openai.com/v1/images/generations"
            body = {
                "model": "dall-e-3",
                "prompt": "test image of a banana",
                "n": 1,
                "size": "1024x1024"
            }
            img_r = requests.post(img_url, headers=headers, json=body, timeout=30)
            print(f"Image Gen Status: {img_r.status_code}")
            if img_r.status_code == 200:
                print("✅ DALL-E 3 Generation Successful!")
                return True
            else:
                print(f"❌ Image Gen Failed: {img_r.text}")
        else:
            print(f"❌ Key invalid or quota exceeded: {r.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False

if __name__ == "__main__":
    test_openai_dalle()
