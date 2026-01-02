import requests
import json
import time
import os

API_KEY = "AQ.Ab8RN6JlwHr_BIEOrmYf5V7wBWPkd4d8SEC4DC7E9w1UCUiblQ"
ENDPOINT = "https://api.nanobananaapi.ai/api/v1/nanobanana/generate-pro"

def test_generate(prompt, output_file):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Based on docs: https://docs.nanobananaapi.ai/nanobanana-api/generate-image-pro
    body = {
        "prompt": prompt,
        "imageUrls": [],
        "resolution": "1K",  # Options: 1K, 2K, 4K
        # "callBackUrl": "" # Optional
    }
    
    print(f"Sending request to {ENDPOINT} for '{prompt}'...")
    try:
        response = requests.post(ENDPOINT, headers=headers, json=body, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Data: {json.dumps(data, indent=2)}")
            
            # The API might return a URL directly or a task ID. 
            # Docs say "callback mechanism eliminates need to poll", suggesting it might be async.
            # However, if no callback is provided, maybe it returns synchronously or gives a task ID to poll?
            # Let's inspect the response.
            
            # Assuming it might return a 'data' field with url, or similar.
            # If it returns a task ID, we might need another endpoint to check status.
            
            # For now, let's see what we get.
            return data
        else:
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None

if __name__ == "__main__":
    if not os.path.exists("public/assets/images/asl_test"):
        os.makedirs("public/assets/images/asl_test")

    # Test with one prompt
    prompt = "A cute cartoon cat is eating, educational illustration style, flat vector art, simple background"
    result = test_generate(prompt, "public/assets/images/asl_test/test_cat_nano.png")
