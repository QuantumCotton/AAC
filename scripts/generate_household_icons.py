#!/usr/bin/env python3
"""
Generate household item icons using Stability AI
"""

import os
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)

# Stability AI API key
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

# Data file
DATA_FILE = PROJECT_ROOT / "src" / "data" / "household_items.json"

# Output directory
OUTPUT_DIR = PROJECT_ROOT / "public" / "assets" / "images" / "household"


def load_items():
    """Load household items from JSON file"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['items']


def generate_stability_image(item_name: str, output_path: Path) -> bool:
    """Generate image using Stability AI"""
    try:
        url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        
        # Create a child-friendly prompt
        prompt = f"A simple, colorful cartoon icon of a {item_name} on a white background. Minimal design, flat illustration style, suitable for educational app for children. Clean lines, bright colors."
        
        headers = {
            "authorization": f"Bearer {STABILITY_API_KEY}",
            "accept": "image/*",
        }
        
        data = {
            "prompt": prompt,
            "output_format": "png",
            "aspect_ratio": "1:1",
            "size": "256x256",
        }
        
        print(f"  🎨 Generating Stability AI image for: {item_name}")
        response = requests.post(
            url, 
            headers=headers, 
            data=data, 
            files={"none": None},
            timeout=(10, 120)
        )
        
        if response.status_code == 200:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"    ✅ Saved: {output_path.name}")
            return True
        
        print(f"    ❌ Failed: {response.status_code}")
        try:
            error_data = response.json()
            print(f"    Error: {error_data}")
        except:
            pass
        return False
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False


def generate_all_icons(items: list, dry_run: bool = False) -> dict:
    """Generate icons for all items"""
    results = {"success": 0, "failed": 0, "total": len(items)}
    
    print(f"\n🎨 Generating Household Item Icons")
    print(f"📊 Total items: {len(items)}")
    print(f"📁 Output: {OUTPUT_DIR}")
    
    if not STABILITY_API_KEY:
        print("\n❌ No Stability AI API key found in .env")
        print("📝 Please add STABILITY_API_KEY to your .env file")
        return results
    
    for i, item in enumerate(items, 1):
        item_name = item['name'].lower()
        output_path = OUTPUT_DIR / f"{item['id']}.png"
        
        print(f"\n[{i}/{len(items)}] {item['name']} ({item['category']})")
        
        # Skip if exists
        if not dry_run and output_path.exists():
            print(f"  ⏭️ Skipping - already exists")
            results["success"] += 1
            continue
        
        if dry_run:
            print(f"  📝 Would generate: {item_name} -> {output_path.name}")
            results["success"] += 1
            continue
        
        # Generate image
        if generate_stability_image(item_name, output_path):
            results["success"] += 1
        else:
            results["failed"] += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Complete!")
    print(f"📊 Success: {results['success']}/{results['total']}")
    print(f"📊 Failed: {results['failed']}/{results['total']}")
    print(f"{'='*60}")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate household item icons using Stability AI"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate and print only (no API calls)"
    )
    parser.add_argument(
        "--items",
        type=str,
        default="all",
        help="Specific items to generate (comma-separated, or 'all')"
    )
    
    args = parser.parse_args()
    
    # Load items
    items = load_items()
    
    # Filter if specific items requested
    if args.items != "all":
        requested_ids = [id.strip() for id in args.items.split(",")]
        items = [item for item in items if item['id'] in requested_ids]
    
    # Generate icons
    generate_all_icons(items, args.dry_run)


if __name__ == "__main__":
    import sys
    sys.exit(main())
