import requests
import json

API_KEY = "AQ.Ab8RN6JlwHr_BIEOrmYf5V7wBWPkd4d8SEC4DC7E9w1UCUiblQ"
BASE_URL = "https://api.nanobananaapi.ai/api/v1"

ENDPOINTS = [
    "/nanobanana/generate",
    "/nanobanana/generate-fast",
    "/nanobanana/image-gen",
    "/user/info",
    "/user/profile",
    "/user/credits",
    "/system/health"
]

def test_endpoint(ep):
    url = BASE_URL + ep
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "prompt": "test",
        "resolution": "1K"
    }
    
    print(f"Testing {ep}...")
    try:
        # Try both GET and POST
        if "user" in ep or "health" in ep:
            resp = requests.get(url, headers=headers, timeout=10)
        else:
            resp = requests.post(url, headers=headers, json=body, timeout=10)
            
        print(f"  Status: {resp.status_code}")
        print(f"  Response: {resp.text[:200]}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                if data.get("code") == 401:
                    print("  ❌ API Permission Error inside 200 OK")
                else:
                    print("  ✅ Endpoint might be valid!")
            except:
                pass
                
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    for ep in ENDPOINTS:
        test_endpoint(ep)
