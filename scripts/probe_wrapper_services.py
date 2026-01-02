import requests

API_KEY = "AQ.Ab8RN6JlwHr_BIEOrmYf5V7wBWPkd4d8SEC4DC7E9w1UCUiblQ"

DOMAINS_TO_TEST = [
    "https://nanobananaapi.ai",
    "https://api.nanobananaapi.ai",
    "https://api.kie.ai",
    "https://kie.ai/api",
    "https://api.banana.dev",
]

def probe(url):
    print(f"Probing {url}...")
    try:
        resp = requests.get(url, timeout=5)
        print(f"  Status: {resp.status_code}")
    except Exception as e:
        print(f"  Error: {e}")

def probe_endpoint(base_url):
    endpoints = ["/v1/images/generations", "/v1/generate", "/api/generate"]
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    body = {"prompt": "test", "model": "nano-banana"}
    
    for ep in endpoints:
        full_url = base_url + ep
        print(f"Testing POST {full_url}...")
        try:
            resp = requests.post(full_url, headers=headers, json=body, timeout=5)
            print(f"  Status: {resp.status_code} - {resp.text[:100]}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    for d in DOMAINS_TO_TEST:
        probe(d)
        probe_endpoint(d)
