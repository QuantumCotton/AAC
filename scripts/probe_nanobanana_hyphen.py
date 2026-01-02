import requests
import time

API_KEY = "AQ.Ab8RN6JlwHr_BIEOrmYf5V7wBWPkd4d8SEC4DC7E9w1UCUiblQ"

# Try hyphenated domains based on search results for "nano-banana.ai"
ENDPOINTS = [
    "https://api.nano-banana.ai/v1/images/generations",
    "https://api.nano-banana.ai/v1/generate",
    "https://api.nano-banana.run/v1/images/generations",
    "https://api.nano-banana.com/v1/images/generations",
    # Try generic base
    "https://api.nano-banana.ai/"
]

def test_endpoint(url):
    print(f"Testing {url}...")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    body = {
        "prompt": "test",
        "n": 1,
        "size": "1024x1024"
    }
    
    try:
        if url.endswith("/"):
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, headers=headers, json=body, timeout=5)
            
        print(f"  Status: {response.status_code}")
        if response.status_code != 404 and response.status_code != 0:
            print(f"  Response: {response.text[:200]}")
            return True
            
    except Exception as e:
        print(f"  Error: {e}")
    
    return False

if __name__ == "__main__":
    for url in ENDPOINTS:
        test_endpoint(url)
