#!/usr/bin/env python3
"""
Generate natural audio scripts using GPT-5-mini with intonation markers
"""

import os
import json
import time
import random
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables (ensure we load from project root even when run from scripts/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)

# Configure APIs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_monolingual_v1")
ELEVENLABS_NAME_MODEL = os.getenv("ELEVENLABS_NAME_MODEL", "eleven_multilingual_v2")

ELEVENLABS_STABILITY = float(os.getenv("ELEVENLABS_STABILITY", "0.55"))
ELEVENLABS_SIMILARITY_BOOST = float(os.getenv("ELEVENLABS_SIMILARITY_BOOST", "0.80"))
ELEVENLABS_STYLE = float(os.getenv("ELEVENLABS_STYLE", "0.0"))
ELEVENLABS_USE_SPEAKER_BOOST = os.getenv("ELEVENLABS_USE_SPEAKER_BOOST", "true").strip().lower() in {"1", "true", "yes"}
ELEVENLABS_OUTPUT_FORMAT = os.getenv("ELEVENLABS_OUTPUT_FORMAT", "mp3_44100_128")

def normalize_eleven_v3_stability(value: float) -> float:
    # Eleven v3 requires stability to be exactly one of: 0.0, 0.5, 1.0
    allowed = (0.0, 0.5, 1.0)
    if value in allowed:
        return value
    # Snap to nearest
    return min(allowed, key=lambda v: abs(v - value))

def sanitize_tts_text(text: str) -> str:
    s = (text or "").replace("\r", " ").replace("\n", " ").replace("\t", " ")
    s = " ".join(s.split())
    return s.strip()

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY, timeout=60.0)

_BANNED_PHRASES = [
    "did you know",
    "guess what",
    "wow",
    "amazing",
    "incredible",
    "happy",
    "listen to this",
    "here's something interesting",
    "something interesting about",
    "fun fact",
    "something special about",
    "meet the",
    "special",
    "what's really interesting",
    "pretty neat",
    "right?",
    "can you say",
]

# Hardcoded script overrides for animals that tend to get bad GPT outputs
_SCRIPT_OVERRIDES = {
    "bottlenose dolphin": {
        "simple": "[curious] I'm a Bottlenose Dolphin. I talk to my friends using clicks and whistles underwater.",
        "detailed": "I'm a Bottlenose Dolphin. I can grow up to 12 feet long and weigh around 600 pounds. Each dolphin has a unique whistle, like a name, so we can find our friends. I live in warm oceans all around the world.",
    },
    "dolphin": {
        "simple": "[curious] I'm a Dolphin. I use clicks and whistles to chat with my pod.",
        "detailed": "I'm a Dolphin. I can hold my breath for up to 10 minutes and swim as fast as 20 miles per hour. I'm one of the smartest animals in the ocean and I love to play.",
    },
}

_STYLE_MODES = [
    "DIRECT_FACT",          # plain, calm, confident
    "KID_REPORTER",         # 'I'm reporting from...'
    "TINY_STORY",           # 1-2 sentence mini scene
    "QUIZ",                 # quick question + answer
    "COMPARE",              # simple comparison kids know
    "SOUND_EFFECT",         # one tasteful sound word (roar/splash) max once
    "COUNTING",             # uses one number concept
    "MYSTERY_REVEAL",        # short setup then reveal
    "IMAGINE",              # gentle imagination prompt
    "SUPERPOWER_BUT_REAL",  # 'My real superpower is...' but factual
    "BACKYARD_CONNECTION",  # connect to where kids might see it
    "SCIENCE_LAB",          # 'Scientists noticed...'
]

def slugify(name: str) -> str:
    """Convert animal name to URL-friendly slug."""
    return name.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')

def normalize_animal_name(name: str) -> str:
    s = (name or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    # Remove punctuation that commonly differs between datasets.
    s = re.sub(r"[^a-z0-9 ]+", "", s)
    return s.strip()

def _article_for(name: str) -> str:
    return "an" if (name or "").strip()[:1].lower() in {"a", "e", "i", "o", "u"} else "a"

def build_simple_script_from_fact(animal_name: str, facts: dict) -> str:
    """Build a clean, kid-friendly 'simple' script without OpenAI.

    Goal: avoid template-y intros ("meet the", "special"), and always start with:
    "I'm a/an <animal>." then one short real fact (when available).
    """

    # Prefer curated kid fact, but fall back to the single-string "fact" field if that's all we have.
    raw_fact = ""
    if isinstance(facts, dict):
        raw_fact = facts.get("fact_level_1") or facts.get("fact") or ""
    raw_fact = sanitize_tts_text(raw_fact)

    # Remove banned/cheesy openers from the curated fact if they exist.
    lowered = raw_fact.lower()
    for phrase in _BANNED_PHRASES:
        if phrase and phrase in lowered:
            raw_fact = sanitize_tts_text(raw_fact.lower().replace(phrase, ""))
            lowered = raw_fact.lower()

    # Strip any leading "I'm a/an <animal>" from the curated fact to avoid duplication.
    # (We will always prepend our own clean opener.)
    name_lower = (animal_name or "").strip().lower()
    if raw_fact:
        no_tags = raw_fact
        if no_tags.startswith("[") and "]" in no_tags:
            # If facts ever include tags, remove a leading one.
            close = no_tags.find("]")
            no_tags = no_tags[close + 1 :].strip()
        no_tags_lower = no_tags.lower()
        if no_tags_lower.startswith("i'm a ") or no_tags_lower.startswith("i'm an "):
            # If the animal name appears very early, treat it as an intro and remove it.
            cut_region = no_tags_lower[: max(40, len(name_lower) + 10)]
            if name_lower and name_lower in cut_region:
                # Drop the first sentence.
                for sep in (".", "!", "?"):
                    if sep in no_tags:
                        no_tags = no_tags.split(sep, 1)[1].strip()
                        break
                raw_fact = sanitize_tts_text(no_tags)

    # Keep only the first sentence-like chunk (prevents rambling).
    fact_chunk = raw_fact
    for sep in (".", "!", "?"):
        if sep in fact_chunk:
            fact_chunk = fact_chunk.split(sep, 1)[0].strip()
            break
    fact_chunk = sanitize_tts_text(fact_chunk)

    opener = f"I'm {_article_for(animal_name)} {animal_name}."
    if not fact_chunk:
        return opener

    # Ensure fact ends with a period.
    if not fact_chunk.endswith("."):
        fact_chunk = fact_chunk + "."
    return sanitize_tts_text(f"{opener} {fact_chunk}")

def _pick_simple_fact_fallback(facts: dict) -> str:
    if not isinstance(facts, dict):
        return ""
    # Prefer curated simple fact.
    raw = sanitize_tts_text(facts.get("fact_level_1") or "")
    if raw:
        return raw
    # Fall back to single-string fact field (present in animals.json).
    raw2 = sanitize_tts_text(facts.get("fact") or "")
    if raw2:
        return raw2
    # Fall back to one detailed component (still factual).
    lvl2 = facts.get("fact_level_2") if isinstance(facts.get("fact_level_2"), dict) else {}
    for key in ("unique_fact", "habitat", "size_details"):
        v = sanitize_tts_text((lvl2 or {}).get(key) or "")
        if v:
            return v
    return ""

def _deterministic_simple_tag(animal_id: str) -> str:
    # One tag max for "cute animated" delivery without being obnoxious.
    # IMPORTANT: avoid pause tags at the start. These lines are played immediately on button press.
    tags = ["[curious]", "[excited]", "[thoughtful]"]
    if not animal_id:
        return tags[0]
    idx = sum(ord(c) for c in animal_id) % len(tags)
    return tags[idx]

def _avoid_repeating_animal_name_in_second_sentence(text: str, animal_name: str) -> str:
    s = sanitize_tts_text(text)
    if not s or not animal_name:
        return s

    tag = ""
    rest = s
    if rest.startswith("[") and "]" in rest:
        close = rest.find("]")
        tag = rest[: close + 1]
        rest = rest[close + 1 :].strip()

    if "." not in rest:
        return s

    first, second = rest.split(".", 1)
    first = first.strip()
    second = second.strip()
    if not second:
        return s

    # If the second sentence starts by repeating the animal name, replace with "I".
    # Example: "I'm a trumpet fish. Trumpet fish often swim vertically..." -> "... I often swim vertically..."
    an = re.escape((animal_name or "").strip())
    second2 = re.sub(rf"^(?:the\s+)?{an}\b", "I", second, flags=re.IGNORECASE)
    second2 = sanitize_tts_text(second2)
    if not second2:
        return s

    rebuilt = f"{first}. {second2}"
    if tag:
        rebuilt = f"{tag} {rebuilt}"
    return sanitize_tts_text(rebuilt)

def generate_simple_script_with_openai(animal_name: str, animal_id: str, facts: dict, *, allow_invented: bool, animal_category: str = "") -> str:
    """Use OpenAI to write a short kid-friendly simple script with one real fact.

    Must start with: "I'm a/an <animal>" and must include at least one factual detail.
    """
    if not OPENAI_API_KEY:
        return ""

    tag = _deterministic_simple_tag(animal_id)
    fallback_fact = _pick_simple_fact_fallback(facts)

    simple_fact = sanitize_tts_text((facts or {}).get("fact_level_1") if isinstance(facts, dict) else "")
    lvl2 = facts.get("fact_level_2") if isinstance(facts, dict) and isinstance(facts.get("fact_level_2"), dict) else {}
    size = sanitize_tts_text((lvl2 or {}).get("size_details") or "")
    unique = sanitize_tts_text((lvl2 or {}).get("unique_fact") or "")
    habitat = sanitize_tts_text((lvl2 or {}).get("habitat") or "")

    has_any_fact = bool(simple_fact or size or unique or habitat or fallback_fact)
    if not has_any_fact and not allow_invented:
        return ""

    banned_text = ", ".join([f'"{p}"' for p in _BANNED_PHRASES])
    model_name = os.getenv("OPENAI_MODEL", "gpt-5-mini")

    allowed_tags = "[curious], [excited], [thoughtful]"
    system_prompt = (
        "You write SHORT, cute-but-calm, kid-friendly animal fact lines for ages 3–8. "
        "The audio plays immediately when a child presses a button; avoid leading silence. "
        "The text will be read by ElevenLabs; use punctuation for natural pauses. "
        "You MUST use the provided facts only (no guessing). "
        "Avoid cheesy templates. Output plain text only."
    )

    if has_any_fact:
        user_prompt = f"""
ANIMAL: {animal_name}

FACTS YOU MAY USE (pick ONE small detail kids benefit from):
- fact_level_1: {simple_fact}
- size_details: {size}
- unique_fact: {unique}
- habitat: {habitat}
- fallback_fact: {fallback_fact}

HARD RULES:
1) Optional: start with exactly one tag from this list: {allowed_tags}
2) Then start EXACTLY with: I'm a/an {animal_name}.
3) Then add ONE short factual sentence (8–18 words after the intro is fine).
4) Do NOT repeat the animal name after the first sentence; use "I" or "they".
5) Use punctuation for pauses (commas/periods). Do NOT use pause tags. No special markup besides the optional one tag.
3) Do NOT use any of these phrases: {banned_text}
4) No questions. No "Did you know". No "Meet the". No "special".
5) If a field is empty, ignore it. Do not invent.

Return ONE line that is spoken-friendly.
"""
    else:
        # Opt-in: create a safe, broadly-true, kid-friendly line from general knowledge.
        # Keep it generic to reduce the chance of being wrong.
        user_prompt = f"""
ANIMAL: {animal_name}
CATEGORY (may help, optional): {animal_category}

TASK:
Write ONE kid-friendly fact line for ages 3–8 using general knowledge.

HARD RULES:
1) Optional: start with exactly one tag from this list: {allowed_tags}
2) Then start EXACTLY with: I'm a/an {animal_name}.
3) Then add ONE short, broadly-true sentence (no numbers, no measurements, no scientific jargon).
4) Do NOT repeat the animal name after the first sentence; use "I" or "they".
5) Use punctuation for pauses (commas/periods). Do NOT use pause tags. No special markup besides the optional one tag.
3) Do NOT use any of these phrases: {banned_text}
4) No questions. No hype. No "Did you know".
5) Avoid very specific claims. Prefer general traits (where it lives, what it eats, what it looks like).
6) Keep it respectful and non-scary.

Return ONE line that is spoken-friendly.
"""

    # Validate: must start with I'm a/an <animal> (allow optional leading tag)
    def _strip_tag(t: str) -> str:
        t2 = (t or "").strip()
        if t2.startswith("[") and "]" in t2:
            t2 = t2.split("]", 1)[1].strip()
        return t2

    def _is_valid(line: str) -> bool:
        base = _strip_tag(line).lower()
        if not (base.startswith("i'm a ") or base.startswith("i'm an ")):
            return False
        if normalize_animal_name(animal_name) not in normalize_animal_name(base[: max(60, len(animal_name) + 20)]):
            return False
        # Ensure there is content beyond the opener.
        # Require at least ~3 words after the first period.
        after = base
        if "." in after:
            after = after.split(".", 1)[1].strip()
        if len(after.split()) < 3:
            return False
        return True

    def _call_openai(extra_instruction: str = "") -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        if extra_instruction:
            messages.append({"role": "user", "content": extra_instruction})
        resp = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.6,
            max_tokens=120,
        )
        return sanitize_tts_text(resp.choices[0].message.content)

    try:
        line = _call_openai()
        if not _is_valid(line):
            repair = (
                "Rewrite the ONE line. You forgot the fact. "
                "Keep the exact intro 'I'm a/an <animal>'. Then add ONE factual sentence using the provided facts. "
                "Do not add any new facts."
            )
            line = _call_openai(repair)
        if not _is_valid(line):
            return ""
    except Exception:
        return ""

    # Fix awkward repetition like "trumpet fish trumpet fish".
    line = _avoid_repeating_animal_name_in_second_sentence(line, animal_name)

    # Add one deterministic v3 tag for animation.
    if not line.startswith("["):
        line = f"{tag} {line}"
    return sanitize_tts_text(line)

def _load_simple_scripts_file(path: Path) -> dict:
    try:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def _write_simple_scripts_file(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_simple_scripts_json(
    animals: list,
    merged_facts_for,
    *,
    batch_size: int,
    allow_invented: bool,
    require_tag: bool,
    scripts_path: Path,
    start_index: int,
    end_index: int,
    reverse: bool,
) -> None:
    bs = max(1, int(batch_size))
    start_index = max(1, int(start_index))
    end_index = max(start_index, int(end_index))

    indices = list(range(start_index, end_index + 1))
    if reverse:
        indices = list(range(end_index, start_index - 1, -1))

    out = _load_simple_scripts_file(scripts_path)
    total_batches = (len(indices) + bs - 1) // bs

    for batch_num in range(total_batches):
        batch_indices = indices[batch_num * bs : (batch_num + 1) * bs]
        payload = []
        batch_meta = []
        for global_index in batch_indices:
            animal = animals[global_index - 1]
            animal_id = slugify(animal.get("name") or "")
            batch_meta.append((global_index, animal, animal_id))
            payload.append(
                {
                    "name": animal.get("name") or "",
                    "category": animal.get("category") or "",
                    "facts": merged_facts_for(animal.get("name") or ""),
                }
            )

        print(f"\n📦 Script-only batch {batch_num + 1}/{total_batches}")
        simple_batch_map = {}
        if payload:
            print("    🤖 Creating SIMPLE batch with OpenAI (no ElevenLabs)...")
            simple_batch_map = generate_simple_batch_with_openai(
                payload,
                allow_invented=allow_invented,
                require_tag=require_tag,
            )

        for global_index, animal, animal_id in batch_meta:
            name = animal.get("name") or ""
            facts = merged_facts_for(name)

            simple_text = simple_batch_map.get(normalize_animal_name(name), "")
            if not simple_text:
                simple_text = generate_simple_script_with_openai(
                    name,
                    animal_id,
                    facts,
                    allow_invented=allow_invented,
                    animal_category=(animal.get("category") or ""),
                )
            if not simple_text:
                simple_text = build_simple_script_from_fact(name, facts)

            simple_text = _avoid_repeating_animal_name_in_second_sentence(simple_text, name)

            if require_tag and not (simple_text or "").lstrip().startswith("["):
                simple_text = sanitize_tts_text(f"{_deterministic_simple_tag(animal_id)} {simple_text}")

            base = (simple_text or "").lower().strip()
            if base.startswith("i'm ") and ("." not in base or len(base.split(".", 1)[-1].split()) < 3):
                print(f"    ⚠️ Script skipped (no usable fact found): {name}")
                continue

            out[animal_id] = {
                "name": name,
                "simple": sanitize_tts_text(simple_text),
                "updated_at": datetime.utcnow().isoformat() + "Z",
            }
            print(f"  📝 [{global_index}/{len(animals)}] {name}: {sanitize_tts_text(simple_text)}")

        _write_simple_scripts_file(scripts_path, out)
        if (batch_num + 1) < total_batches:
            time.sleep(0.5)

def generate_simple_batch_with_openai(batch: list, *, allow_invented: bool, require_tag: bool) -> dict:
    if not OPENAI_API_KEY:
        return {}

    banned_text = ", ".join([f'"{p}"' for p in _BANNED_PHRASES])
    model_name = os.getenv("OPENAI_MODEL", "gpt-5-mini")

    # ElevenLabs v3 voice tags for expressive speech
    allowed_tags = "[curious], [excited], [playful], [whispers], [giggles], [surprised]"
    tag_rule = "Each line MUST start with exactly one mood tag from the allowed list." if require_tag else "A tag is optional. If used, use exactly one tag from the allowed list."

    system_prompt = (
        "You write SHORT, fun, animated kid-friendly animal fact lines for ages 3–8. "
        "Make each line sound like a friendly nature show host talking to a toddler. "
        "Vary the energy and tone across the batch - some excited, some whispery/mysterious, some playful. "
        "Return strict JSON only."
    )

    batch_payload = []
    for item in batch:
        name = item.get("name") or ""
        category = item.get("category") or ""
        facts = item.get("facts") if isinstance(item.get("facts"), dict) else {}
        lvl2 = facts.get("fact_level_2") if isinstance(facts.get("fact_level_2"), dict) else {}
        batch_payload.append(
            {
                "name": name,
                "category": category,
                "fact_level_1": sanitize_tts_text(facts.get("fact_level_1") or ""),
                "fact": sanitize_tts_text(facts.get("fact") or ""),
                "size_details": sanitize_tts_text((lvl2 or {}).get("size_details") or ""),
                "unique_fact": sanitize_tts_text((lvl2 or {}).get("unique_fact") or ""),
                "habitat": sanitize_tts_text((lvl2 or {}).get("habitat") or ""),
            }
        )

    invent_rule = (
        "If a given animal has NO facts in the fields, you MAY invent ONE safe, broadly-true kid fact from general knowledge. "
        "Keep it generic: no numbers, no measurements, no rare claims."
        if allow_invented
        else "If a given animal has NO facts in the fields, return an empty string for its simple line."
    )

    user_prompt = (
        "Write one SIMPLE audio line per animal. Make each one sound fun and engaging when read aloud!\n\n"
        "RULES:\n"
        f"- BANNED phrases (never use): {banned_text}\n"
        f"- MOOD TAGS: {allowed_tags}. {tag_rule}\n"
        "- FORMAT: [tag] I'm a/an <animal>. <one fun fact sentence>\n"
        "- Keep it SHORT: 2-3 sentences max, under 25 words total.\n"
        "- Make it MEMORABLE: cool body parts, funny behaviors, surprising abilities.\n"
        "- VARY the mood tags across the batch - mix excited, curious, whispers, playful.\n"
        "- NO questions, NO 'special', NO 'amazing', NO hype words.\n"
        "- Use 'I' or 'we' after the intro, not the animal name again.\n"
        f"- {invent_rule}\n\n"
        "Output strict JSON ONLY:\n"
        "{{\"items\": [{{\"name\": \"...\", \"simple\": \"...\"}}]}}\n\n"
        f"ANIMALS:\n{json.dumps(batch_payload, ensure_ascii=False)}\n"
    )

    def _clean_json(txt: str) -> str:
        t = (txt or "").strip()
        if t.startswith("```json"):
            t = t[7:]
        if t.startswith("```"):
            t = t[3:]
        if t.endswith("```"):
            t = t[:-3]
        return t.strip()

    def _validate(result: dict) -> bool:
        if not isinstance(result, dict) or "items" not in result or not isinstance(result["items"], list):
            return False
        expected = {normalize_animal_name(x.get("name") or "") for x in batch_payload if x.get("name")}
        got = {normalize_animal_name(x.get("name") or "") for x in result["items"] if isinstance(x, dict)}
        if expected != got:
            return False
        for row in result["items"]:
            if not isinstance(row, dict) or not isinstance(row.get("simple"), str):
                return False
            line = sanitize_tts_text(row.get("simple") or "")
            if not line:
                continue
            low = line.lower()
            for phrase in _BANNED_PHRASES:
                if phrase and phrase in low:
                    return False
            if require_tag and not line.lstrip().startswith("["):
                return False
            base = line
            if base.startswith("[") and "]" in base:
                base = base.split("]", 1)[1].strip()
            base_low = base.lower()
            if not (base_low.startswith("i'm a ") or base_low.startswith("i'm an ")):
                return False
            if "." not in base_low:
                return False
            after = base_low.split(".", 1)[1].strip()
            if len(after.split()) < 3:
                return False
        return True

    def _call(extra_instruction: str = "") -> dict:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        if extra_instruction:
            messages.append({"role": "user", "content": extra_instruction})
        resp = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=900,
        )
        raw = sanitize_tts_text(resp.choices[0].message.content)
        return json.loads(_clean_json(raw))

    try:
        out = _call()
        if not _validate(out):
            repair = (
                "Your JSON was invalid or repetitive. Return JSON only. "
                "Make every line structurally different across the batch. "
                "Ensure each line includes a real fact sentence after the intro."
            )
            out = _call(repair)
        if not _validate(out):
            return {}
        mapping = {}
        for row in out.get("items", []):
            nm = (row.get("name") or "").strip()
            val = sanitize_tts_text(row.get("simple") or "")
            val = _avoid_repeating_animal_name_in_second_sentence(val, nm)
            mapping[normalize_animal_name(nm)] = sanitize_tts_text(val)
        return mapping
    except Exception:
        return {}

def generate_natural_script(animal_name: str, facts: dict) -> dict:
    """Generate natural scripts using GPT-5-mini with intonation markers."""
    
    # Check for hardcoded overrides first
    name_key = (animal_name or "").strip().lower()
    if name_key in _SCRIPT_OVERRIDES:
        override = _SCRIPT_OVERRIDES[name_key]
        return {
            "name": f"{animal_name}!",
            "simple": override.get("simple", ""),
            "detailed": override.get("detailed", ""),
        }
    
    # Get facts
    # If we don't have a curated simple fact, default to a clean, non-template opener.
    # The actual simple audio should effectively be: "I'm a/an <animal>. <one real fact>."
    simple_fact = facts.get('fact_level_1', f"I'm {_article_for(animal_name)} {animal_name}.")
    size = facts.get('fact_level_2', {}).get('size_details', '')
    unique = facts.get('fact_level_2', {}).get('unique_fact', '')
    habitat = facts.get('fact_level_2', {}).get('habitat', '')
    
    # User preference: keep it direct (no 'meet the special ...' templates)
    style_mode = "DIRECT_FACT"

    system_prompt = (
        "You write short, natural, non-repetitive audio scripts for a kids animal soundboard (ages 3-8). "
        "The audio will be heard many times per day, so you MUST vary structure and avoid catchphrases. "
        "Never invent facts. If a fact is missing, omit it instead of making something up. "
        "Output JSON only."
    )

    banned_text = ", ".join([f'"{p}"' for p in _BANNED_PHRASES])

    allowed_tags = (
        "[curious], [excited], [thoughtful], [surprised], [whispers], [chuckles], [laughs], "
        "[sighs], [short pause], [long pause]"
    )

    user_prompt = f"""
ANIMAL: {animal_name}

FACTS (use these, do not add new facts):
- simple_fact: {simple_fact}
- size: {size}
- unique: {unique}
- habitat: {habitat}

STYLE MODE FOR THIS ANIMAL: {style_mode}

HARD CONSTRAINTS:
1. Do NOT use any of these words/phrases anywhere (case-insensitive): {banned_text}
2. Do NOT start sentences with repeated openers like: "Did you know", "Guess what", "Wow", "Amazing", "Listen to this".
3. No ALL CAPS sentences. If you emphasize, capitalize at most ONE single word.
4. Keep it kid-friendly, warm, and clear.
5. Make each field feel different from the others.
5b. PUNCTUATION: Use at most 1 exclamation mark total across simple+detailed (0 is fine). Avoid multiple exclamation marks.
5c. Eleven v3 audio tags (optional): you may add 0–2 TOTAL tags across simple+detailed. Tags must be exactly one of: {allowed_tags}. Do not invent new tags.
5d. Do NOT use SSML or XML of any kind (no <break>, no <phoneme>, no angle brackets).
5e. Spoken-friendly formatting: avoid colons like "length:". Prefer sentences. Expand abbreviations (ft -> feet, lb -> pounds). Write digits as words.
6. Length targets:
   - name: 3–8 words.
   - simple: 10–22 words.
   - detailed: 35–60 words (aim for 250+ characters for v3 stability).
7. Detailed MUST include at least 2 of: size / unique / habitat (when provided).
8. Avoid the phrase "something interesting".
9. Simple MUST start with: "I'm a" or "I'm an" followed by the animal name.

OUTPUT JSON ONLY in this schema:
{{
  "name": "...",
  "simple": "...",
  "detailed": "..."
}}
"""

    def _is_bad(text: str) -> bool:
        t = (text or "").strip().lower()
        if not t:
            return True
        for phrase in _BANNED_PHRASES:
            if phrase in t:
                return True
        return False

    def _strip_leading_tags(text: str) -> str:
        t = (text or "").strip()
        # Remove up to 2 leading [tag] markers
        for _ in range(2):
            if t.startswith("[") and "]" in t:
                close = t.find("]")
                t = t[close + 1 :].strip()
            else:
                break
        return t

    def _validate_scripts(s: dict) -> bool:
        if not isinstance(s, dict):
            return False
        for key in ("name", "simple", "detailed"):
            if key not in s or not isinstance(s[key], str) or not s[key].strip():
                return False
            if _is_bad(s[key]):
                return False
            if "<" in s[key] or ">" in s[key]:
                return False
        # Basic length guardrails
        if len(s["name"].split()) < 1 or len(s["name"].split()) > 10:
            return False
        if len(s["simple"].split()) < 6 or len(s["simple"].split()) > 28:
            return False
        if len(s["detailed"].split()) < 20 or len(s["detailed"].split()) > 80:
            return False

        # Enforce the simple intro pattern the user wants.
        simple_clean = _strip_leading_tags(s["simple"]).lower()
        if not (simple_clean.startswith("i'm a ") or simple_clean.startswith("i'm an ")):
            return False
        if animal_name.lower() not in simple_clean[: max(40, len(animal_name) + 10)]:
            return False
        return True

    try:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is missing. Check your .env.")

        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.9,
            max_tokens=260,
        )
        
        script_text = response.choices[0].message.content.strip()
        
        # Clean up response
        if script_text.startswith("```json"):
            script_text = script_text[7:]
        if script_text.endswith("```"):
            script_text = script_text[:-3]
        
        scripts = json.loads(script_text)
        if _validate_scripts(scripts):
            scripts["name"] = sanitize_tts_text(scripts["name"])
            scripts["simple"] = sanitize_tts_text(scripts["simple"])
            scripts["detailed"] = sanitize_tts_text(scripts["detailed"])
            return scripts

        # Retry once with an explicit repair instruction (quality > token savings)
        repair_prompt = (
            "Your JSON violated constraints (repetition or banned phrases or length). "
            "Rewrite JSON ONLY, keeping facts accurate, and avoid ALL banned phrases. "
            "Make it sound natural and different in structure from typical templates."
        )
        response2 = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "user", "content": repair_prompt},
            ],
            temperature=0.95,
            max_tokens=260,
        )

        script_text2 = response2.choices[0].message.content.strip()
        if script_text2.startswith("```json"):
            script_text2 = script_text2[7:]
        if script_text2.endswith("```"):
            script_text2 = script_text2[:-3]
        scripts2 = json.loads(script_text2)
        if _validate_scripts(scripts2):
            scripts2["name"] = sanitize_tts_text(scripts2["name"])
            scripts2["simple"] = sanitize_tts_text(scripts2["simple"])
            scripts2["detailed"] = sanitize_tts_text(scripts2["detailed"])
            return scripts2

        raise RuntimeError("OpenAI returned scripts that failed validation twice")
    except Exception as e:
        msg = str(e)
        # If OpenAI auth is broken, STOP. Don't spend ElevenLabs credits generating junk.
        if "401" in msg or "403" in msg or "Incorrect" in msg or "invalid_api_key" in msg:
            raise

        # For transient errors, return a minimal non-repetitive fallback using provided facts.
        safe_name = f"{animal_name}."
        safe_simple = f"{simple_fact}"
        parts = []
        if size:
            parts.append(f"Size: {size}.")
        if unique:
            parts.append(f"{unique}.")
        if habitat:
            parts.append(f"Habitat: {habitat}.")
        safe_detailed = " ".join(parts) if parts else safe_simple
        return {
            "name": sanitize_tts_text(safe_name),
            "simple": sanitize_tts_text(safe_simple),
            "detailed": sanitize_tts_text(safe_detailed),
        }

def find_first_incomplete_index(animals: list, names_dir: Path, facts_dir: Path) -> int:
    for idx, animal in enumerate(animals, start=1):
        animal_id = slugify(animal["name"])
        name_path = names_dir / f"{animal_id}_name.mp3"
        simple_path = facts_dir / f"{animal_id}_fact_simple.mp3"
        detailed_path = facts_dir / f"{animal_id}_fact_detailed.mp3"
        if not (name_path.exists() and simple_path.exists() and detailed_path.exists()):
            return idx
    return len(animals) + 1

def find_last_incomplete_index(animals: list, names_dir: Path, facts_dir: Path) -> int:
    for idx in range(len(animals), 0, -1):
        animal = animals[idx - 1]
        animal_id = slugify(animal["name"])
        name_path = names_dir / f"{animal_id}_name.mp3"
        simple_path = facts_dir / f"{animal_id}_fact_simple.mp3"
        detailed_path = facts_dir / f"{animal_id}_fact_detailed.mp3"
        if not (name_path.exists() and simple_path.exists() and detailed_path.exists()):
            return idx
    return 0

def acquire_animal_lock(locks_dir: Path, animal_id: str, stale_seconds: int = 6 * 60 * 60) -> Path | None:
    locks_dir.mkdir(parents=True, exist_ok=True)
    lock_path = locks_dir / f"{animal_id}.lock"
    try:
        with open(lock_path, "x", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow().isoformat()}Z\n")
        return lock_path
    except FileExistsError:
        try:
            age = time.time() - lock_path.stat().st_mtime
            if age > stale_seconds:
                try:
                    lock_path.unlink()
                except Exception:
                    return None
                with open(lock_path, "x", encoding="utf-8") as f:
                    f.write(f"{datetime.utcnow().isoformat()}Z\n")
                return lock_path
        except Exception:
            return None
        return None

def release_animal_lock(lock_path: Path | None) -> None:
    if not lock_path:
        return
    try:
        lock_path.unlink()
    except Exception:
        pass

def generate_audio_with_retry(text: str, output_path: Path, max_retries=3, model_id: str | None = None) -> bool:
    """Generate audio using ElevenLabs with retry."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    cleaned_text = sanitize_tts_text(text)

    stability_value = ELEVENLABS_STABILITY
    if (ELEVENLABS_MODEL or "").strip().lower() == "eleven_v3":
        stability_value = normalize_eleven_v3_stability(stability_value)

    voice_settings = {
        "stability": stability_value,
        "similarity_boost": ELEVENLABS_SIMILARITY_BOOST,
        "use_speaker_boost": ELEVENLABS_USE_SPEAKER_BOOST,
    }

    # "style" is not supported by all models/voices; include only when explicitly non-zero.
    if ELEVENLABS_STYLE != 0.0:
        voice_settings["style"] = ELEVENLABS_STYLE

    data = {
        "text": cleaned_text,
        "model_id": (model_id or ELEVENLABS_MODEL),
        "voice_settings": voice_settings,
        "output_format": ELEVENLABS_OUTPUT_FORMAT,
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, headers=headers, timeout=(10, 120))
            
            if response.status_code == 200:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            elif response.status_code == 429:
                wait_time = 3 * (attempt + 1)  # Faster retry: 3s, 6s, 9s
                print(f"⏱️ Rate limit. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            elif response.status_code in (400, 401, 402, 403):
                body_text = (response.text or "").strip()
                try:
                    body_json = response.json()
                except Exception:
                    body_json = None

                detail_status = None
                if isinstance(body_json, dict):
                    detail = body_json.get("detail")
                    if isinstance(detail, dict):
                        detail_status = detail.get("status")

                if detail_status in {
                    "insufficient_credits",
                    "quota_exceeded",
                    "rate_limit_exceeded",
                    "voice_limit_reached",
                    "subscription_required",
                }:
                    raise RuntimeError(f"ELEVENLABS_LIMIT::{detail_status}")

                if len(body_text) > 400:
                    body_text = body_text[:400] + "..."
                print(f"❌ Failed: {response.status_code} {body_text}")
                return False
            else:
                body = (response.text or "").strip()
                if body:
                    if len(body) > 200:
                        body = body[:200] + "..."
                    print(f"❌ Failed: {response.status_code} {body}")
                else:
                    print(f"❌ Failed: {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                continue
        except Exception as e:
            print(f"❌ Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            continue
    
    return False

def main():
    """Generate natural audio for all animals."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--redo-all", action="store_true", help="Regenerate audio even if files already exist")
    parser.add_argument("--wipe", action="store_true", help="Delete all existing mp3s before generating")
    parser.add_argument("--dry-run", action="store_true", help="Generate and print scripts only (no ElevenLabs audio)")
    parser.add_argument("--category", type=str, default="", help="Only process animals in this category/habitat (e.g. Farm). Case-insensitive.")
    parser.add_argument("--only-name", action="store_true", help="Only generate name audio (single word). Skips OpenAI and fact audio.")
    parser.add_argument("--only-simple", action="store_true", help="Only generate simple fact audio (skip OpenAI; keep name/detailed untouched unless missing)")
    parser.add_argument("--simple-openai", action="store_true", help="When used with --only-simple, use OpenAI to write the simple line (cute/animated) using provided facts only")
    parser.add_argument("--allow-invented-simple", action="store_true", help="Allow GPT to create a simple fact from general knowledge when no fact data exists (opt-in)")
    parser.add_argument("--start", type=int, default=1, help="1-based animal index to start from")
    parser.add_argument("--limit", type=int, default=0, help="Max number of animals to process (0 = no limit)")
    parser.add_argument("--batch-size", type=int, default=3, help="Animals per batch")
    parser.add_argument("--resume", action="store_true", help="Auto-detect the first animal missing audio and continue from there")
    parser.add_argument("--reverse", action="store_true", help="Process animals from end to start")
    parser.add_argument("--write-simple-scripts", action="store_true", help="GPT-only: generate simple scripts JSON (no ElevenLabs)")
    parser.add_argument("--simple-scripts-path", type=str, default=str(PROJECT_ROOT / "src" / "data" / "simple_scripts.json"), help="Path to read/write simple scripts JSON")
    parser.add_argument("--use-simple-scripts", type=str, default="", help="Use an existing simple scripts JSON file (keyed by animal_id) instead of calling OpenAI")
    args = parser.parse_args()

    print("🎤 Generating Natural Audio with OpenAI + ElevenLabs...")
    
    # Load data - use animals_fixed.json as the master list
    animals_file = Path(__file__).parent.parent / "animals_fixed.json"
    facts_file = Path(__file__).parent.parent / "src/data" / "facts_clean.json"
    animals_rich_file = Path(__file__).parent.parent / "src/data" / "animals.json"
    
    with open(animals_file, 'r', encoding='utf-8') as f:
        animals = json.load(f)

    if args.category:
        want = args.category.strip().lower()
        filtered = [a for a in animals if (a.get("category") or "").strip().lower() == want]
        if not filtered:
            categories = sorted({(a.get("category") or "").strip() for a in animals if (a.get("category") or "").strip()})
            print(f"❌ No animals found for category: {args.category}")
            if categories:
                print("Available categories:")
                for c in categories:
                    print(f"  - {c}")
            return
        animals = filtered
    
    with open(facts_file, 'r', encoding='utf-8') as f:
        facts = json.load(f)

    # animals.json contains the full fact payloads (fact_level_1 / fact_level_2) for all animals.
    animals_rich = []
    try:
        with open(animals_rich_file, 'r', encoding='utf-8') as f:
            animals_rich = json.load(f)
    except Exception:
        animals_rich = []

    print(f"📚 Loaded animals_fixed.json: {len(animals)} animals")
    print(f"📚 Loaded facts_clean.json: {len(facts)} entries")
    print(f"📚 Loaded animals.json: {len(animals_rich)} entries")

    # Robust lookup: facts datasets sometimes differ by casing/punctuation.
    facts_lookup = {}
    for fact in facts:
        key = normalize_animal_name(fact.get("name", ""))
        if key and key not in facts_lookup:
            facts_lookup[key] = fact

    animals_rich_lookup = {}
    for a in animals_rich:
        key = normalize_animal_name(a.get("name", ""))
        if key and key not in animals_rich_lookup:
            animals_rich_lookup[key] = a

    # Create lookup for the current loaded animals (which might be animals_fixed.json)
    animals_current_lookup = {}
    for a in animals:
        key = normalize_animal_name(a.get("name", ""))
        if key:
            animals_current_lookup[key] = a

    def merged_facts_for(name: str) -> dict:
        k = normalize_animal_name(name)
        base = facts_lookup.get(k) or {}
        fallback = animals_rich_lookup.get(k) or {}
        current = animals_current_lookup.get(k) or {}
        
        if not isinstance(base, dict): base = {}
        if not isinstance(fallback, dict): fallback = {}
        if not isinstance(current, dict): current = {}
        
        merged = dict(fallback)
        merged.update(base)
        
        # Inject 'fact' from current list as fact_level_1 if missing
        if current.get("fact") and not merged.get("fact_level_1"):
            merged["fact_level_1"] = current["fact"]
            
        # Deep-merge level_2 dict
        lvl2 = {}
        if isinstance(fallback.get("fact_level_2"), dict):
            lvl2.update(fallback.get("fact_level_2") or {})
        if isinstance(base.get("fact_level_2"), dict):
            lvl2.update(base.get("fact_level_2") or {})
        if lvl2:
            merged["fact_level_2"] = lvl2
        return merged

    # Phase 1: generate scripts only (cheap), save to JSON for review.
    if args.write_simple_scripts:
        scripts_path = Path(args.simple_scripts_path)
        batch_size = max(1, int(args.batch_size))
        start_index = max(1, args.start)
        end_index = len(animals) if args.limit <= 0 else min(len(animals), start_index + args.limit - 1)
        require_tag = (ELEVENLABS_MODEL or "").strip().lower() == "eleven_v3"
        generate_simple_scripts_json(
            animals,
            merged_facts_for,
            batch_size=batch_size,
            allow_invented=bool(args.allow_invented_simple),
            require_tag=require_tag,
            scripts_path=scripts_path,
            start_index=start_index,
            end_index=end_index,
            reverse=bool(args.reverse),
        )
        print(f"\n✅ Wrote simple scripts JSON: {scripts_path}")
        return
    
    assets_dir = PROJECT_ROOT / "public" / "assets" / "audio"
    names_dir = assets_dir / "names"
    facts_dir = assets_dir / "facts"
    locks_dir = assets_dir / ".locks"

    if args.wipe:
        for d in (names_dir, facts_dir):
            if d.exists():
                for f in d.glob("*.mp3"):
                    f.unlink()

    batch_size = max(1, int(args.batch_size))
    success_count = 0

    simple_scripts_by_id = {}
    if args.use_simple_scripts:
        simple_scripts_by_id = _load_simple_scripts_file(Path(args.use_simple_scripts))
    
    start_index = max(1, args.start)
    if args.resume and (not args.redo_all):
        names_dir.mkdir(parents=True, exist_ok=True)
        facts_dir.mkdir(parents=True, exist_ok=True)
        if args.reverse:
            auto_start = find_last_incomplete_index(animals, names_dir, facts_dir)
            if auto_start >= 1:
                start_index = min(start_index, auto_start) if args.start != 1 else auto_start
                print(f"🔁 Resume mode (reverse): starting at animal #{start_index}/{len(animals)}")
            else:
                print("✅ Resume mode: everything already exists. Nothing to do.")
                return
        else:
            auto_start = find_first_incomplete_index(animals, names_dir, facts_dir)
            if auto_start <= len(animals):
                start_index = max(start_index, auto_start)
                print(f"🔁 Resume mode: starting at animal #{start_index}/{len(animals)}")
            else:
                print("✅ Resume mode: everything already exists. Nothing to do.")
                return
    end_index = len(animals) if args.limit <= 0 else min(len(animals), start_index + args.limit - 1)

    indices = list(range(start_index, end_index + 1))
    if args.reverse:
        indices = list(range(start_index, 0, -1)) if args.limit <= 0 else list(range(start_index, start_index - len(indices), -1))
        indices = [i for i in indices if 1 <= i <= len(animals)]

    total_batches = (len(indices) + batch_size - 1) // batch_size
    for batch_num in range(total_batches):
        batch_indices = indices[batch_num * batch_size : (batch_num + 1) * batch_size]
        print(f"\n📦 Processing batch {batch_num + 1}/{total_batches}")

        batch_work = []
        try:
            for global_index in batch_indices:
                animal = animals[global_index - 1]

                animal_id = slugify(animal["name"])

                lock_path = acquire_animal_lock(locks_dir, animal_id)
                if not lock_path:
                    print(f"  ⏭️ Skipping {animal['name']} - locked by another process")
                    continue
                
                name_path = names_dir / f"{animal_id}_name.mp3"
                simple_path = facts_dir / f"{animal_id}_fact_simple.mp3"
                detailed_path = facts_dir / f"{animal_id}_fact_detailed.mp3"

                if not args.redo_all:
                    if args.only_name:
                        if name_path.exists():
                            print(f"  ⏭️ Skipping {animal['name']} - name already exists")
                            release_animal_lock(lock_path)
                            continue
                    elif args.only_simple:
                        if simple_path.exists():
                            print(f"  ⏭️ Skipping {animal['name']} - simple already exists")
                            release_animal_lock(lock_path)
                            continue
                    else:
                        if name_path.exists() and simple_path.exists() and detailed_path.exists():
                            print(f"  ⏭️ Skipping {animal['name']} - already exists")
                            release_animal_lock(lock_path)
                            continue
                
                batch_work.append(
                    {
                        "global_index": global_index,
                        "animal": animal,
                        "animal_id": animal_id,
                        "lock_path": lock_path,
                        "name_path": name_path,
                        "simple_path": simple_path,
                        "detailed_path": detailed_path,
                    }
                )

            simple_batch_map = {}
            if (not args.only_name) and args.only_simple and args.simple_openai and batch_work:
                require_tag = (ELEVENLABS_MODEL or "").strip().lower() == "eleven_v3"
                payload = []
                for w in batch_work:
                    a = w["animal"]
                    payload.append(
                        {
                            "name": a.get("name") or "",
                            "category": a.get("category") or "",
                            "facts": merged_facts_for(a.get("name") or ""),
                        }
                    )
                print("    🤖 Creating SIMPLE batch with OpenAI...")
                simple_batch_map = generate_simple_batch_with_openai(
                    payload,
                    allow_invented=bool(args.allow_invented_simple),
                    require_tag=require_tag,
                )

            for w in batch_work:
                global_index = w["global_index"]
                animal = w["animal"]
                animal_id = w["animal_id"]
                lock_path = w["lock_path"]
                name_path = w["name_path"]
                simple_path = w["simple_path"]
                detailed_path = w["detailed_path"]

                print(f"  🦁 [{global_index}/{len(animals)}] Processing: {animal['name']}")

                animal_facts = merged_facts_for(animal["name"])

                name_text = sanitize_tts_text(f"{animal['name']}")

                if args.only_name:
                    scripts = {
                        "name": name_text,
                        "simple": "",
                        "detailed": "",
                    }
                elif args.only_simple:
                    if args.simple_openai:
                        # Prefer pre-generated scripts if provided.
                        from_file = None
                        if simple_scripts_by_id:
                            row = simple_scripts_by_id.get(animal_id)
                            if isinstance(row, dict):
                                from_file = row.get("simple")
                            elif isinstance(row, str):
                                from_file = row
                        simple_text = sanitize_tts_text(from_file or "")

                        if not simple_text:
                            simple_text = simple_batch_map.get(normalize_animal_name(animal["name"]), "")
                        if not simple_text:
                            simple_text = generate_simple_script_with_openai(
                                animal["name"],
                                animal_id,
                                animal_facts,
                                allow_invented=bool(args.allow_invented_simple),
                                animal_category=(animal.get("category") or ""),
                            )
                        if not simple_text:
                            simple_text = build_simple_script_from_fact(animal["name"], animal_facts)
                    else:
                        simple_text = build_simple_script_from_fact(animal["name"], animal_facts)

                    simple_text = _avoid_repeating_animal_name_in_second_sentence(simple_text, animal["name"])

                    # Ensure an Eleven v3 tag exists for a slightly more animated delivery.
                    if (ELEVENLABS_MODEL or "").strip().lower() == "eleven_v3":
                        if not (simple_text or "").lstrip().startswith("["):
                            simple_text = sanitize_tts_text(f"{_deterministic_simple_tag(animal_id)} {simple_text}")

                    # If we still couldn't form a factual line beyond the opener, SKIP to avoid burning credits.
                    base = simple_text.lower().strip()
                    if base.startswith("i'm ") and ("." not in base or len(base.split(".", 1)[-1].split()) < 3):
                        print(f"    ⚠️ Skipping simple audio (no usable fact found): {animal['name']}")
                        release_animal_lock(lock_path)
                        continue

                    scripts = {
                        "name": name_text,
                        "simple": simple_text,
                        "detailed": "",
                    }
                else:
                    # Generate natural scripts with OpenAI
                    print("    🤖 Creating script with OpenAI...")
                    scripts = generate_natural_script(animal["name"], animal_facts)
                    scripts["name"] = name_text

                print(f"    📝 {sanitize_tts_text(scripts['name'])}")
                if not args.only_name:
                    print(f"    📝 {sanitize_tts_text(scripts['simple'])}")
                    if not args.only_simple:
                        print(f"    📝 {sanitize_tts_text(scripts['detailed'])}")

                if args.dry_run:
                    release_animal_lock(lock_path)
                    continue

                try:
                    if args.only_name:
                        if args.redo_all or (not name_path.exists()):
                            if generate_audio_with_retry(scripts["name"], name_path, model_id=ELEVENLABS_NAME_MODEL):
                                print(f"    ✅ Name audio: {animal['name']}")
                                success_count += 1
                        continue
                    elif not args.only_simple:
                        if args.redo_all or (not name_path.exists()):
                            if generate_audio_with_retry(scripts["name"], name_path, model_id=ELEVENLABS_NAME_MODEL):
                                print(f"    ✅ Name audio: {animal['name']}")
                                success_count += 1

                    if args.redo_all or (not simple_path.exists()):
                        if generate_audio_with_retry(scripts["simple"], simple_path):
                            print(f"    ✅ Simple fact: {animal['name']}")
                            success_count += 1

                    if not args.only_simple:
                        if args.redo_all or (not detailed_path.exists()):
                            if generate_audio_with_retry(scripts["detailed"], detailed_path):
                                print(f"    ✅ Detailed fact: {animal['name']}")
                                success_count += 1
                except KeyboardInterrupt:
                    print("\n🛑 Interrupted by user. Releasing lock and stopping.")
                    release_animal_lock(lock_path)
                    print(f"Resume with: python generate_natural_audio_simple.py --start {global_index} --batch-size {batch_size}")
                    return
                except RuntimeError as e:
                    if str(e).startswith("ELEVENLABS_LIMIT::"):
                        limit_reason = str(e).split("::", 1)[1]
                        print(f"\n🛑 Stopping due to ElevenLabs limit: {limit_reason}")
                        print(f"Resume with: python generate_natural_audio_simple.py --start {global_index} --batch-size {batch_size}")
                        print(f"\n✅ Partial complete! Generated {success_count} audio files")
                        release_animal_lock(lock_path)
                        return
                    raise
                finally:
                    release_animal_lock(lock_path)
        finally:
            for w in batch_work:
                try:
                    release_animal_lock(w.get("lock_path"))
                except Exception:
                    pass
        
        # Brief pause between batches
        if (batch_num + 1) < total_batches:
            print("  ⏸️ Brief pause between batches...")
            time.sleep(1)
    
    print(f"\n✅ Complete! Generated {success_count} audio files")

if __name__ == "__main__":
    main()
