import requests
import time

API_KEY = "AQ.Ab8RN6JlwHr_BIEOrmYf5V7wBWPkd4d8SEC4DC7E9w1UCUiblQ"

ENDPOINTS = [
    "https://api.nanobanana.ai/v1/images/generations",
    "https://api.nanobanana.run/v1/images/generations",
    "https://api.nanobanana.ai/v1/generate",
    "https://api.nanobanana.run/v1/generate",
    # Try OpenAI compatible format
    "https://api.nanobanana.ai/v1/chat/completions",
]

def test_endpoint(url):
    print(f"Testing {url}...")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Try Image Gen body
    body_image = {
        "prompt": "test image of a banana",
        "n": 1,
        "size": "1024x1024"
    }
    
    try:
        response = requests.post(url, headers=headers, json=body_image, timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✅ SUCCESS! Response: {response.text[:200]}")
            return True
        elif response.status_code != 404:
             print(f"  Result: {response.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
    
    return False

def main():
    print("Probing Nano Banana API endpoints...")
    for url in ENDPOINTS:
        if test_endpoint(url):
            print(f"\n🎉 Found working endpoint: {url}")
            break

if __name__ == "__main__":
    main()
