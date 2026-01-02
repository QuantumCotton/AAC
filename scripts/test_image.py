#!/usr/bin/env python3
"""
Test script for image generation APIs
"""

import os
import json
import requests
import base64
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_MODEL = os.getenv("STABILITY_MODEL", "stable-diffusion-xl-1024-v1-0")

def test_stability_ai():
    """Test generating image with Stability AI"""
    if not STABILITY_API_KEY:
        print("❌ No Stability AI API key found in .env")
        return False
    
    print("🎨 Testing Stability AI image generation...")
    
    url = f"https://api.stability.ai/v1/generation/{STABILITY_MODEL}/text-to-image"
    
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Test prompt for a lion
    prompt = "A friendly cartoon lion with big eyes, sitting in a sunny African savanna, children's book illustration style, vibrant colors, white background"
    
    body = {
        "text_prompts": [
            {
                "text": prompt,
                "weight": 1
            }
        ],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30
    }
    
    try:
        response = requests.post(url, json=body, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Get the base64 image data
            image_data = data["artifacts"][0]["base64"]
            
            # Decode and save
            image_bytes = base64.b64decode(image_data)
            output_dir = Path("test_output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / "test_lion_stability.webp"
            
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            
            print(f"✅ Success! Image saved to {output_path}")
            print(f"📊 File size: {output_path.stat().st_size} bytes")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_account_balance():
    """Check Stability AI account balance"""
    if not STABILITY_API_KEY:
        return
    
    print("\n💰 Checking account balance...")
    
    url = "https://api.stability.ai/v1/user/balance"
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            balance = response.json()
            print(f"✅ Credits: {balance['credits']}")
        else:
            print(f"❌ Error checking balance: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception checking balance: {e}")

if __name__ == "__main__":
    test_account_balance()
    test_stability_ai()
