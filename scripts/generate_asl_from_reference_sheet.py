import os
import base64
import json
import argparse
from pathlib import Path

import requests


def read_env_value(key: str) -> str | None:
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return None
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip()
    return None


def slugify(text: str) -> str:
    return (
        text.strip()
        .lower()
        .replace("'", "")
        .replace("-", "_")
        .replace(" ", "_")
    )


def encode_image_b64(image_path: Path) -> tuple[str, str]:
    suffix = image_path.suffix.lower()
    if suffix in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif suffix == ".webp":
        mime = "image/webp"
    else:
        mime = "image/png"

    data = image_path.read_bytes()
    return mime, base64.b64encode(data).decode("utf-8")


def build_prompt(word: str) -> str:
    return (
        "Create ONE single AAC communication icon for the ASL sign, using the provided reference sheet ONLY as a STYLE guide. "
        "Match the exact visual style of the reference sheet: flat 2D educational clipart, thick black outlines, "
        "simple shapes, no realism. The output should look like it belongs in the same set. "
        "\n\n"
        f"TARGET WORD: {word}\n"
        "\n"
        "REQUIREMENTS:\n"
        "- Output must be ONE single icon card only (not a collage)\n"
        "- DO NOT recreate the full reference sheet\n"
        "- DO NOT include the title 'Basic Sign Language'\n"
        "- DO NOT include a grid of multiple cards\n"
        "- Use the SAME hand/arm style as the reference sheet\n"
        "- Use a clean white background with a thin black border around the icon (like a flashcard square)\n"
        "- Use the correct number of hands for that sign (one hand vs two hands)\n"
        "- No extra hands, no extra arms\n"
        "- No gradients, no shadows\n"
        "- Do NOT include any text in the image\n"
        "- Center the gesture, large and easy to recognize\n"
        "\n"
        "If the sign is ambiguous, choose the most common basic sign used for AAC/early learners."
    )


def generate_one(
    *,
    api_key: str,
    model: str,
    reference_image_path: Path,
    word: str,
    out_path: Path,
    timeout_s: int,
) -> None:
    mime, b64 = encode_image_b64(reference_image_path)
    prompt = build_prompt(word)

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": mime,
                            "data": b64,
                        }
                    },
                    {"text": prompt},
                ],
            }
        ],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": "1:1",
                "imageSize": "1K",
            },
        },
    }

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }

    resp = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers=headers,
        json=payload,
        timeout=timeout_s,
    )

    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:500]}")

    data = resp.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
        image_part = next(p for p in parts if "inlineData" in p)
        image_b64 = image_part["inlineData"]["data"]
    except Exception:
        raise RuntimeError(f"No image in response: {json.dumps(data)[:500]}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(base64.b64decode(image_b64))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", required=True, help="Path to the reference icon sheet image (png/jpg/webp)")
    parser.add_argument("--out", default="public/assets/images/asl/reference_set", help="Output directory")
    parser.add_argument("--model", default="gemini-3-pro-image-preview")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("words", nargs="*", help="Words to generate")
    args = parser.parse_args()

    api_key = os.getenv("GOOGLE_GEMINI_API_KEY") or read_env_value("GOOGLE_GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("Missing GOOGLE_GEMINI_API_KEY")

    ref_path = Path(args.ref)
    if not ref_path.exists():
        raise SystemExit(f"Reference image not found: {ref_path}")

    out_dir = Path(args.out)

    if args.words:
        words = args.words
    else:
        words = [
            "yes",
            "no",
            "please",
            "thank you",
            "sorry",
            "help",
            "more",
            "all done",
            "find",
            "want",
            "open",
            "sit",
            "sleep",
            "play",
            "eat",
            "drink",
            "hurt",
            "restroom",
            "stop",
            "go",
        ]

    for i, word in enumerate(words, 1):
        fname = slugify(word) + ".png"
        out_path = out_dir / fname
        print(f"[{i}/{len(words)}] Generating {word} -> {out_path}")
        generate_one(
            api_key=api_key,
            model=args.model,
            reference_image_path=ref_path,
            word=word,
            out_path=out_path,
            timeout_s=args.timeout,
        )

    print(f"Done. Output: {out_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
