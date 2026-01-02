#!/usr/bin/env python3
"""Generate real facts for animals with placeholder facts using GPT."""
import json
import os
import time
from pathlib import Path
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def needs_real_fact(fact: str) -> bool:
    """Check if this is a placeholder fact that needs replacement."""
    if not fact:
        return True
    low = fact.lower()
    return (
        "amazing animal" in low or
        "lives in the wild" in low or
        "is an amazing" in low or
        len(fact) < 30
    )

def generate_facts_batch(animals: list) -> dict:
    """Generate facts for a batch of animals using GPT."""
    if not client:
        print("No OpenAI API key!")
        return {}
    
    system_prompt = (
        "You generate SHORT, fun, kid-friendly animal facts for ages 3-8. "
        "Each fact should be ONE memorable thing about the animal. "
        "Keep it under 20 words. No 'amazing', 'special', or hype words. "
        "Return JSON only."
    )
    
    names = [a["name"] for a in animals]
    user_prompt = (
        f"Generate ONE fun fact for each animal. Facts should be concrete and memorable.\n"
        f"Examples of GOOD facts:\n"
        f"- 'Crows can recognize human faces and hold grudges for years!'\n"
        f"- 'Ants can carry 50 times their own body weight!'\n"
        f"- 'Axolotls can regrow their legs, tail, and even parts of their brain!'\n\n"
        f"Animals: {json.dumps(names)}\n\n"
        f"Return JSON: {{\"facts\": {{\"Animal Name\": \"fact text\", ...}}}}"
    )
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
        return result.get("facts", {})
    except Exception as e:
        print(f"Error: {e}")
        return {}

def main():
    animals_path = Path(__file__).parent.parent / "animals_fixed.json"
    
    with open(animals_path, "r", encoding="utf-8") as f:
        animals = json.load(f)
    
    # Find animals that need real facts
    need_facts = [a for a in animals if needs_real_fact(a.get("fact", ""))]
    print(f"Total animals: {len(animals)}")
    print(f"Need real facts: {len(need_facts)}")
    
    if not need_facts:
        print("All animals have real facts!")
        return
    
    # Process in batches
    batch_size = 20
    facts_map = {}
    
    for i in range(0, len(need_facts), batch_size):
        batch = need_facts[i:i+batch_size]
        print(f"\nBatch {i//batch_size + 1}/{(len(need_facts) + batch_size - 1)//batch_size}: {len(batch)} animals")
        
        batch_facts = generate_facts_batch(batch)
        facts_map.update(batch_facts)
        
        # Show progress
        for a in batch:
            fact = batch_facts.get(a["name"], "")
            if fact:
                print(f"  ✓ {a['name']}: {fact[:50]}...")
            else:
                print(f"  ✗ {a['name']}: No fact generated")
        
        if i + batch_size < len(need_facts):
            time.sleep(1)  # Rate limit
    
    # Update animals with new facts
    updated = 0
    for a in animals:
        if a["name"] in facts_map and facts_map[a["name"]]:
            a["fact"] = facts_map[a["name"]]
            updated += 1
    
    # Save updated file
    with open(animals_path, "w", encoding="utf-8") as f:
        json.dump(animals, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Updated {updated} animals with real facts")

if __name__ == "__main__":
    main()
