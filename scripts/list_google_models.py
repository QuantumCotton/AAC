import requests
import os

API_KEY = "AQ.Ab8RN6JlwHr_BIEOrmYf5V7wBWPkd4d8SEC4DC7E9w1UCUiblQ"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

def list_models():
    url = f"{BASE_URL}/models?key={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"Found {len(models)} models:")
            for m in models:
                print(f" - {m['name']} ({m.get('displayName', '')})")
                print(f"   Supported generation methods: {m.get('supportedGenerationMethods', [])}")
        else:
            print(f"Error listing models: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    list_models()
