import os
import json
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv
import time

load_dotenv()

# Google Imagen API Key
IMAGEN_API_KEY = os.getenv("GOOGLE_IMAGEN_API_KEY")

print(f"🔑 Testing Google Imagen API Key...")
print(f"Key: {IMAGEN_API_KEY[:10]}...{IMAGEN_API_KEY[-10:] if IMAGEN_API_KEY and len(IMAGEN_API_KEY) > 20 else ''}")
print()

if not IMAGEN_API_KEY:
    print("❌ GOOGLE_IMAGEN_API_KEY not found in .env file")
    exit(1)

# Output directory
OUTPUT_DIR = Path("public/assets/images/asl/test_samples")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Try multiple possible endpoints for Google Imagen
ENDPOINTS = [
    {
        "name": "Vertex AI Imagen 3",
        "url": "https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT/locations/us-central1/publishers/google/models/imagen-3.0-generate-001:predict",
        "auth_header": "Authorization",
        "auth_value": f"Bearer {IMAGEN_API_KEY}"
    },
    {
        "name": "AI Studio Imagen",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:generateContent",
        "auth_header": "x-goog-api-key",
        "auth_value": IMAGEN_API_KEY
    },
    {
        "name": "Direct Imagen API",
        "url": "https://imagen.googleapis.com/v1/images:generate",
        "auth_header": "Authorization",
        "auth_value": f"Bearer {IMAGEN_API_KEY}"
    },
    {
        "name": "Imagen API with x-api-key",
        "url": "https://imagen.googleapis.com/v1/images:generate",
        "auth_header": "x-api-key",
        "auth_value": IMAGEN_API_KEY
    }
]

def test_endpoint(endpoint_config, prompt):
    """Test a specific endpoint configuration"""
    
    print(f"🧪 Testing: {endpoint_config['name']}")
    print(f"   URL: {endpoint_config['url']}")
    
    headers = {
        endpoint_config['auth_header']: endpoint_config['auth_value'],
        "Content-Type": "application/json"
    }
    
    # Try different payload formats
    payloads = [
        {
            "prompt": prompt,
            "num_images": 1,
            "aspect_ratio": "1:1"
        },
        {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "1:1"
            }
        },
        {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseModalities": ["image"]
            }
        }
    ]
    
    for i, payload in enumerate(payloads, 1):
        try:
            print(f"   Payload format {i}/3...", end=" ")
            response = requests.post(
                endpoint_config['url'],
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ SUCCESS!")
                return True, response
            else:
                print(f"❌ {response.status_code}")
                if response.status_code in [401, 403]:
                    error_data = response.json() if 'application/json' in response.headers.get('content-type', '') else response.text
                    print(f"   Auth Error: {json.dumps(error_data, indent=6)[:200]}")
                    
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
    
    print()
    return False, None

def generate_sample_asl():
    """Test Google Imagen API with a simple ASL prompt"""
    
    prompt = "A professional educational photograph showing a single hand performing the American Sign Language (ASL) sign for 'HELLO'. The hand is raised near the forehead with fingers together, palm facing outward, making a small saluting motion. Clean, well-lit studio photography with a soft pastel blue gradient background. The hand is clearly visible with natural skin tones. Educational illustration style, perfect for children's learning materials."
    
    print(f"🎨 Testing Google Imagen API for ASL Hand Signs\n")
    print(f"📝 Test prompt: ASL sign for 'HELLO'\n")
    print(f"{'='*60}\n")
    
    for endpoint in ENDPOINTS:
        success, response = test_endpoint(endpoint, prompt)
        if success:
            print(f"\n🎉 Found working endpoint: {endpoint['name']}")
            print(f"✅ Response received successfully!")
            
            # Try to save the image
            try:
                data = response.json()
                print(f"\n📦 Response structure:")
                print(json.dumps(data, indent=2)[:500])
                
                # Try to extract image data from various possible response formats
                image_data = None
                
                if "predictions" in data and len(data["predictions"]) > 0:
                    pred = data["predictions"][0]
                    if "bytesBase64Encoded" in pred:
                        image_data = pred["bytesBase64Encoded"]
                    elif "image" in pred:
                        image_data = pred["image"]
                
                elif "candidates" in data and len(data["candidates"]) > 0:
                    cand = data["candidates"][0]
                    if "content" in cand and "parts" in cand["content"]:
                        for part in cand["content"]["parts"]:
                            if "inlineData" in part:
                                image_data = part["inlineData"]["data"]
                                break
                
                elif "images" in data and len(data["images"]) > 0:
                    image_data = data["images"][0].get("data") or data["images"][0].get("base64")
                
                if image_data:
                    output_path = OUTPUT_DIR / "hello_test.png"
                    image_bytes = base64.b64decode(image_data)
                    with open(output_path, "wb") as f:
                        f.write(image_bytes)
                    print(f"\n✅ Image saved to: {output_path}")
                else:
                    print(f"\n⚠️  Could not find image data in response")
                    
            except Exception as e:
                print(f"\n❌ Error processing response: {e}")
            
            return True
    
    print(f"\n{'='*60}")
    print(f"❌ No working endpoint found for Google Imagen API")
    print(f"{'='*60}")
    print(f"\n💡 The API key format suggests this might be a custom/wrapper service.")
    print(f"   Please verify:")
    print(f"   1. The correct API endpoint URL")
    print(f"   2. The authentication method (Bearer, x-api-key, etc.)")
    print(f"   3. The expected request payload format")
    print(f"\n   Once you correct the key in .env, this script will work.")
    
    return False

if __name__ == "__main__":
    generate_sample_asl()
