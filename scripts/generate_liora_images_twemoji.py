#!/usr/bin/env python3
"""Generate consistent AAC symbol images from Twemoji.

Why:
- Deterministic, readable icons (no AI drift / random logos).
- Consistent style across all symbols.

What it does:
- Reads src/data/liora_symbols_full.json (uses each symbol's `icon` emoji)
- Downloads the corresponding Twemoji PNG (72x72) from the official CDN
- Composites it onto a solid background color
- Writes PNGs to public/assets/images/liora/{categoryId}/{symbolId}.png

Env vars:
- BG_COLOR_HEX: background color (default #F3F4F6)
- SIZE: output size in px (default 256)
- PADDING: padding in px (default 32)
- ONLY_CATEGORIES: comma-separated category ids to generate (optional)
- LIMIT_PER_CATEGORY: int (optional)
"""

import io
import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_DIR = Path(__file__).parent.parent
SYMBOLS_FILE = BASE_DIR / "src" / "data" / "liora_symbols_full.json"
OUT_DIR = BASE_DIR / "public" / "assets" / "images" / "liora"
CACHE_DIR = BASE_DIR / ".cache" / "twemoji"

TWEMOJI_BASE = "https://twemoji.maxcdn.com/v/latest/72x72"


def _hex_to_rgba(hex_color: str):
    h = hex_color.strip()
    if not h:
        h = "#F3F4F6"
    if not h.startswith("#"):
        h = "#" + h
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", h):
        raise ValueError(f"Invalid BG_COLOR_HEX: {hex_color}")
    r = int(h[1:3], 16)
    g = int(h[3:5], 16)
    b = int(h[5:7], 16)
    return (r, g, b, 255)


def _emoji_to_twemoji_filename(emoji: str) -> str:
    cps = [f"{ord(ch):x}" for ch in emoji]
    return "-".join(cps) + ".png"


def _download_twemoji_png(emoji: str) -> bytes:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    filename = _emoji_to_twemoji_filename(emoji)
    cached = CACHE_DIR / filename
    if cached.exists():
        return cached.read_bytes()

    url = f"{TWEMOJI_BASE}/{filename}"
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to download Twemoji {emoji} from {url}: {r.status_code}")

    cached.write_bytes(r.content)
    return r.content


def _ensure_pillow():
    try:
        from PIL import Image  # noqa: F401
    except Exception:
        raise RuntimeError(
            "Pillow is required. Install it with: pip install pillow\n"
            "Then rerun: python scripts/generate_liora_images_twemoji.py"
        )


def _compose_icon(icon_png_bytes: bytes, out_size: int, padding: int, bg_rgba):
    from PIL import Image

    bg = Image.new("RGBA", (out_size, out_size), bg_rgba)
    icon = Image.open(io.BytesIO(icon_png_bytes)).convert("RGBA")

    max_w = out_size - 2 * padding
    max_h = out_size - 2 * padding

    # Scale preserving aspect ratio
    icon.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

    x = (out_size - icon.size[0]) // 2
    y = (out_size - icon.size[1]) // 2

    bg.alpha_composite(icon, (x, y))
    return bg


def main():
    _ensure_pillow()

    bg_hex = os.getenv("BG_COLOR_HEX", "#F3F4F6")
    out_size = int(os.getenv("SIZE", "256"))
    padding = int(os.getenv("PADDING", "32"))

    only_categories = os.getenv("ONLY_CATEGORIES", "").strip()
    limit_per_category = os.getenv("LIMIT_PER_CATEGORY", "").strip()
    only_set = set([c.strip() for c in only_categories.split(",") if c.strip()]) if only_categories else None
    limit_n = int(limit_per_category) if limit_per_category else None

    bg_rgba = _hex_to_rgba(bg_hex)

    data = json.loads(SYMBOLS_FILE.read_text(encoding="utf-8"))
    categories = data.get("categories", [])

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    generated = 0
    skipped = 0
    failed = 0

    print("🧩 Liora Twemoji Image Generator")
    print("=" * 50)
    print(f"BG_COLOR_HEX={bg_hex} SIZE={out_size} PADDING={padding}")

    for cat in categories:
        if only_set is not None and cat.get("id") not in only_set:
            continue

        cat_id = cat.get("id")
        (OUT_DIR / cat_id).mkdir(parents=True, exist_ok=True)

        symbols = cat.get("symbols", [])
        if limit_n is not None:
            symbols = symbols[:limit_n]

        print(f"\n🏷️  {cat.get('name')} ({cat_id})")
        for sym in symbols:
            sym_id = sym.get("id")
            emoji = sym.get("icon")
            if not emoji:
                failed += 1
                print(f"  ❌ Missing icon emoji for {sym_id}")
                continue

            out_path = OUT_DIR / cat_id / f"{sym_id}.png"
            if out_path.exists():
                skipped += 1
                continue

            try:
                icon_bytes = _download_twemoji_png(emoji)
                img = _compose_icon(icon_bytes, out_size, padding, bg_rgba)
                img.save(out_path, format="PNG")
                generated += 1
                print(f"  ✅ {sym_id}.png")
            except Exception as e:
                failed += 1
                print(f"  ❌ {sym_id}: {e}")

    print("\n" + "=" * 50)
    print(f"✅ Generated: {generated}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Output: {OUT_DIR}")


if __name__ == "__main__":
    main()
