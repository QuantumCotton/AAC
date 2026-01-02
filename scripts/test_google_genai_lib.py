import google.generativeai as genai
import os
import time

# API Key provided by user
API_KEY = "AQ.Ab8RN6JlwHr_BIEOrmYf5V7wBWPkd4d8SEC4DC7E9w1UCUiblQ"

def test_key_and_models():
    print(f"Configuring with key: {API_KEY[:5]}...")
    try:
        genai.configure(api_key=API_KEY)
        
        print("Listing models...")
        models = list(genai.list_models())
        
        image_models = []
        for m in models:
            print(f" - {m.name} | {m.display_name} | {m.supported_generation_methods}")
            if 'generateImages' in m.supported_generation_methods or 'image' in m.name.lower():
                image_models.append(m.name)
        
        if not image_models:
            print("\n⚠️ No obvious image generation models found in list.")
            # Try specific known image models anyway
            image_models = ["models/imagen-3.0-generate-001", "models/gemini-pro-vision"]
        
        print(f"\nPotential image models to test: {image_models}")
        return image_models

    except Exception as e:
        print(f"❌ Error configuring or listing models: {e}")
        return []

if __name__ == "__main__":
    test_key_and_models()
