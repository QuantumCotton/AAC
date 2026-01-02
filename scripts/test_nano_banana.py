import os
import json
import requests
import base64
from pathlib import Path
import time

# User provided API key
API_KEY = "AQ.Ab8RN6JlwHr_BIEOrmYf5V7wBWPkd4d8SEC4DC7E9w1UCUiblQ"

# Possible endpoints/models
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
# Based on search results, "Nano Banana" might be mapped to a specific model ID
# We will try the likely candidates for the new Imagen 3 / Gemini Image models
MODELS_TO_TRY = [
    "imagen-3.0-generate-001",
    "gemini-3.0-pro-image",
    "nano-banana-pro",
    "nano-banana"
]

OUTPUT_DIR = Path("public/assets/images/asl_test")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_image_google(prompt, model, output_path):
    url = f"{BASE_URL}/models/{model}:predict"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }
    
    # Standard format for Google's predict endpoint (Vertex AI style often used in these APIs)
    # Or the specific generateImages method for AI Studio
    
    # Try the specific method for AI Studio image generation
    # https://ai.google.dev/api/rest/v1beta/models/predict
    
    body = {
        "instances": [
            {
                "prompt": prompt
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "1:1"
        }
    }

    try:
        print(f"Testing model: {model}...")
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code == 200:
            result = response.json()
            # Handle response structure - often predictions[0].bytesBase64Encoded or similar
            if "predictions" in result:
                b64_data = result["predictions"][0].get("bytesBase64Encoded")
                if not b64_data:
                    # Try alternate structure
                     b64_data = result["predictions"][0].get("image", {}).get("bytesBase64Encoded")
                
                if b64_data:
                    with open(output_path, "wb") as f:
                        f.write(base64.b64decode(b64_data))
                    print(f"✅ Success with {model}")
                    return True
            
            print(f"❌ Response format unexpected: {result.keys()}")
            return False
        else:
            print(f"❌ Failed {model}: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception with {model}: {e}")
        return False

def test_samples():
    # 5 Sample ASL prompts
    samples = [
        {"name": "test_more", "prompt": "child's hands making ASL sign for MORE, fingers touching together, soft pink background, educational illustration style"},
        {"name": "test_cat", "prompt": "child's hands making ASL sign for CAT, whisker motion from face, mint green background, educational illustration"},
        {"name": "test_tree", "prompt": "child's arm making ASL sign for TREE, arm up and hand waving, nature background, educational illustration"},
        {"name": "test_happy", "prompt": "child's hands making ASL sign for HAPPY, brushing up chest, orange background, educational illustration"},
        {"name": "test_book", "prompt": "child's hands making ASL sign for BOOK, hands opening like a book, blue background, educational illustration"}
    ]

    # Find working model first
    working_model = None
    for model in MODELS_TO_TRY:
        test_file = OUTPUT_DIR / f"model_check_{model}.png"
        if generate_image_google("test prompt", model, test_file):
            working_model = model
            break
            
    if not working_model:
        print("Could not find a working model endpoint.")
        return

    print(f"Using working model: {working_model}")

    for sample in samples:
        output_path = OUTPUT_DIR / f"{sample['name']}.png"
        print(f"Generating {sample['name']}...")
        success = generate_image_google(sample['prompt'], working_model, output_path)
        if success:
            print(f"Saved to {output_path}")
        else:
            print(f"Failed to generate {sample['name']}")
        time.sleep(1)

if __name__ == "__main__":
    test_samples()
