#!/usr/bin/env python3
"""
Generate household item icons using Stability AI with detailed prompts
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

# Data files
DATA_FILE = PROJECT_ROOT / "src" / "data" / "household_items.json"
PROMPTS_FILE = PROJECT_ROOT / "stability_prompts_household.json"

# Output directory
OUTPUT_DIR = PROJECT_ROOT / "public" / "assets" / "images" / "household"


def load_items():
    """Load household items from JSON file"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['items']


def load_prompts():
    """Load detailed prompts from JSON file"""
    with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create a lookup dictionary: id -> prompt
    prompt_lookup = {}
    for category, items in data['prompts'].items():
        for item in items:
            prompt_lookup[item['id']] = item['prompt']
    
    return prompt_lookup


def generate_stability_image(item_name: str, item_category: str, prompt: str, output_path: Path) -> bool:
    """Generate image using Stability AI"""
    try:
        url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        
        headers = {
            "authorization": f"Bearer {STABILITY_API_KEY}",
            "accept": "image/*",
        }
        
        data = {
            "prompt": prompt,
            "output_format": "png",
            "aspect_ratio": "1:1",
            "size": "512x512",
        }
        
        print(f"  🎨 Generating: {item_name} ({item_category})")
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


def generate_all_icons(items: list, prompts: dict, dry_run: bool = False, force: bool = False) -> dict:
    """Generate icons for all items"""
    results = {"success": 0, "failed": 0, "skipped": 0, "total": len(items)}
    
    print(f"\n🎨 Generating Household Item Icons with Detailed Prompts")
    print(f"📊 Total items: {len(items)}")
    print(f"📁 Output: {OUTPUT_DIR}")
    if force:
        print(f"🔄 Force mode: Regenerating all icons")
    
    if not STABILITY_API_KEY:
        print("\n❌ No Stability AI API key found in .env")
        print("📝 Please add STABILITY_API_KEY to your .env file")
        return results
    
    for i, item in enumerate(items, 1):
        item_name = item['name']
        item_category = item['category']
        item_id = item['id']
        output_path = OUTPUT_DIR / f"{item_id}.png"
        
        # Get the detailed prompt
        prompt = prompts.get(item_id)
        
        if not prompt:
            print(f"\n[{i}/{len(items)}] {item_name} ({item_category})")
            print(f"  ⚠️  No prompt found, skipping")
            results["skipped"] += 1
            continue
        
        print(f"\n[{i}/{len(items)}] {item_name} ({item_category})")
        
        # Skip if exists and not forcing
        if not dry_run and not force and output_path.exists():
            print(f"  ⏭️  Skipping - already exists")
            results["skipped"] += 1
            continue
        
        if dry_run:
            print(f"  📝 Would generate: {item_name}")
            print(f"  📝 Prompt: {prompt[:80]}...")
            results["success"] += 1
            continue
        
        # Generate image
        if generate_stability_image(item_name, item_category, prompt, output_path):
            results["success"] += 1
        else:
            results["failed"] += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Complete!")
    print(f"📊 Success: {results['success']}/{results['total']}")
    print(f"📊 Failed: {results['failed']}/{results['total']}")
    print(f"📊 Skipped: {results['skipped']}/{results['total']}")
    print(f"{'='*60}")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate household item icons using Stability AI with detailed prompts"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate and print only (no API calls)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate all icons, even if they already exist"
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
    
    # Load prompts
    prompts = load_prompts()
    print(f"📝 Loaded {len(prompts)} detailed prompts")
    
    # Filter if specific items requested
    if args.items != "all":
        requested_ids = [id.strip() for id in args.items.split(",")]
        items = [item for item in items if item['id'] in requested_ids]
    
    # Generate icons
    generate_all_icons(items, prompts, args.dry_run, args.force)


if __name__ == "__main__":
    import sys
    sys.exit(main())
