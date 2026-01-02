import os
import time
import argparse
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load environment variables (ensure we load from project root even when run from scripts/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_v3")

ELEVENLABS_SIMILARITY_BOOST = float(os.getenv("ELEVENLABS_SIMILARITY_BOOST", "0.80"))
ELEVENLABS_USE_SPEAKER_BOOST = os.getenv("ELEVENLABS_USE_SPEAKER_BOOST", "true").strip().lower() in {"1", "true", "yes"}
ELEVENLABS_OUTPUT_FORMAT = os.getenv("ELEVENLABS_OUTPUT_FORMAT", "mp3_44100_128")

# Eleven v3 stability must be one of 0.0, 0.5, 1.0
ELEVENLABS_TTD_STABILITY = float(os.getenv("ELEVENLABS_TTD_STABILITY", "0.5"))


def sanitize_tts_text(text: str) -> str:
    s = (text or "").replace("\r", " ").replace("\n", " ").replace("\t", " ")
    s = " ".join(s.split())
    return s.strip()


def normalize_v3_stability(value: float) -> float:
    allowed = (0.0, 0.5, 1.0)
    if value in allowed:
        return value
    return min(allowed, key=lambda v: abs(v - value))


PHONICS = {
    "A": "A. Ah. Aye.",
    "B": "B. Bee. Buh.",
    "C": "C. Cat: kuh. City: sss.",
    "D": "D. Dee. Duh.",
    "E": "E. Eh. Eee.",
    "F": "F. Eff. Fff.",
    "G": "G. Go: guh. Giant: juh.",
    "H": "H. Aitch. Hhh.",
    "I": "I. Ih. Eye.",
    "J": "J. Jay. Juh.",
    "K": "K. Kay. Kuh.",
    "L": "L. El. Lll.",
    "M": "M. Em. Mmm.",
    "N": "N. En. Nnn.",
    "O": "O. Oh. Ooo.",
    "P": "P. Pee. Puh.",
    "Q": "Q. Cue. Kwuh.",
    "R": "R. Ar. Rrr.",
    "S": "S. Ess. Sss.",
    "T": "T. Tee. Tuh.",
    "U": "U. Uh. You.",
    "V": "V. Vee. Vvv.",
    "W": "W. Double-u. Wuh.",
    "X": "X. Ex. Kss.",
    "Y": "Y. Why. Yuh.",
    "Z": "Z. Zee. Zzz.",
}


def eleven_tts(text: str, out_path: Path, max_retries: int = 3) -> None:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY missing")
    if not ELEVENLABS_VOICE_ID:
        raise RuntimeError("ELEVENLABS_VOICE_ID missing")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    stability_value = ELEVENLABS_TTD_STABILITY
    if (ELEVENLABS_MODEL or "").strip().lower() == "eleven_v3":
        stability_value = normalize_v3_stability(stability_value)

    payload = {
        "text": sanitize_tts_text(text),
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": {
            "stability": stability_value,
            "similarity_boost": ELEVENLABS_SIMILARITY_BOOST,
            "use_speaker_boost": ELEVENLABS_USE_SPEAKER_BOOST,
        },
        "output_format": ELEVENLABS_OUTPUT_FORMAT,
    }

    last_err = None
    for attempt in range(max_retries):
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=(10, 120))
            if r.status_code == 200:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(r.content)
                return

            # 429 retry
            if r.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue

            body = (r.text or "").strip()
            if len(body) > 600:
                body = body[:600] + "..."
            raise RuntimeError(f"ElevenLabs TTS failed {r.status_code}: {body}")
        except Exception as e:
            last_err = e
            if attempt < max_retries - 1:
                time.sleep(1.5)
                continue
            raise

    if last_err:
        raise last_err


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--letters", type=str, default="A-Z", help="Subset, e.g. A-Z or A,C,D or A-F")
    parser.add_argument("--redo", action="store_true", help="Regenerate even if file exists")
    args = parser.parse_args()

    out_dir = PROJECT_ROOT / "public" / "assets" / "audio" / "phonics"

    letters = []
    spec = args.letters.strip().upper()
    if spec == "A-Z":
        letters = [chr(c) for c in range(ord('A'), ord('Z') + 1)]
    elif "-" in spec and len(spec) == 3:
        start, end = spec.split("-")
        letters = [chr(c) for c in range(ord(start), ord(end) + 1)]
    else:
        parts = [p.strip() for p in spec.split(",") if p.strip()]
        letters = parts

    for letter in letters:
        if letter not in PHONICS:
            print(f"Skipping unknown letter spec: {letter}")
            continue
        out_path = out_dir / f"letter_{letter}.mp3"
        if out_path.exists() and not args.redo:
            print(f"⏭️ {letter} exists")
            continue

        # v3 prompting: keep it clean and consistent
        text = f"[cheerful] {PHONICS[letter]}"
        print(f"🎧 Generating {out_path.name}: {PHONICS[letter]}")
        eleven_tts(text, out_path)
        time.sleep(0.25)

    print("✅ Done")


if __name__ == "__main__":
    main()
