import requests
import os
import json
import time

# User provided key
API_KEY = "AQ.Ab8RN6JlwHr_BIEOrmYf5V7wBWPkd4d8SEC4DC7E9w1UCUiblQ"

# Fal.ai endpoint based on search results
FAL_URL = "https://queue.fal.run/fal-ai/nano-banana"

def test_fal_generation(prompt, filename):
    headers = {
        "Authorization": f"Key {API_KEY}",
        "Content-Type": "application/json"
    }
    
    body = {
        "prompt": prompt,
        "image_size": "square_hd"
    }
    
    print(f"Testing Fal.ai endpoint for: {prompt[:30]}...")
    try:
        response = requests.post(FAL_URL, headers=headers, json=body)
        
        if response.status_code == 200:
            print("✅ Request successful!")
            result = response.json()
            print(f"Result keys: {result.keys()}")
            
            # Check for image URL
            image_url = None
            if "images" in result and len(result["images"]) > 0:
                image_url = result["images"][0]["url"]
            elif "image" in result:
                image_url = result["image"]["url"]
            
            if image_url:
                print(f"Downloading image from {image_url}...")
                img_resp = requests.get(image_url)
                if img_resp.status_code == 200:
                    with open(filename, "wb") as f:
                        f.write(img_resp.content)
                    print(f"Saved to {filename}")
                    return True
            return False
            
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            # Try 'Bearer' instead of 'Key' just in case
            if response.status_code == 401:
                print("Retrying with Bearer prefix...")
                headers["Authorization"] = f"Bearer {API_KEY}"
                response = requests.post(FAL_URL, headers=headers, json=body)
                if response.status_code == 200:
                    print("✅ Success with Bearer!")
                    # ... handle success ...
                    return True
                else:
                    print(f"❌ Failed with Bearer: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    if not os.path.exists("public/assets/images/asl_test"):
        os.makedirs("public/assets/images/asl_test")
        
    test_fal_generation(
        "child's hands making ASL sign for MORE, fingers touching together, soft pink background, educational illustration style",
        "public/assets/images/asl_test/test_more_fal.png"
    )
