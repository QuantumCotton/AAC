import requests
import json

API_KEY = "AQ.Ab8RN6JlwHr_BIEOrmYf5V7wBWPkd4d8SEC4DC7E9w1UCUiblQ"
ENDPOINT = "https://api.nanobananaapi.ai/api/v1/nanobanana/generate-pro"

HEADER_VARIANTS = [
    {"Authorization": f"Bearer {API_KEY}"},
    {"Authorization": f"Key {API_KEY}"},
    {"Authorization": API_KEY},
    {"x-api-key": API_KEY},
    {"X-API-KEY": API_KEY},
    {"apikey": API_KEY},
    {"key": API_KEY},
    {"token": API_KEY}
]

def test_headers():
    body = {
        "prompt": "test image",
        "resolution": "1K",
        "imageUrls": []
    }
    
    print(f"Target: {ENDPOINT}")
    
    for headers in HEADER_VARIANTS:
        # Add content type
        h = headers.copy()
        h["Content-Type"] = "application/json"
        
        try:
            print(f"Testing headers: {list(headers.keys())}")
            resp = requests.post(ENDPOINT, headers=h, json=body, timeout=10)
            
            print(f"  Status: {resp.status_code}")
            print(f"  Body: {resp.text[:100]}")
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200 or "data" in data or "url" in data:
                    print("  ✅ SUCCESS POSSIBLE!")
                    return True
        except Exception as e:
            print(f"  Error: {e}")
            
    return False

if __name__ == "__main__":
    test_headers()
