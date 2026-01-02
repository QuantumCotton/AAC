#!/usr/bin/env python3
"""
Generate natural, conversational audio scripts for animal facts using Gemini
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)

def slugify(name: str) -> str:
    """Convert animal name to URL-friendly slug."""
    return name.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')

def generate_natural_script(animal_name: str, facts: dict, model) -> dict:
    """Generate natural, conversational scripts using Gemini."""
    
    # Create the prompt for Gemini
    prompt = f"""
You are creating educational audio content for children aged 3-8 about animals. 
Generate THREE different audio scripts for {animal_name} using these facts:

Simple Fact: {facts.get('fact_level_1', 'No simple fact available')}
Size Details: {facts.get('fact_level_2', {}).get('size_details', 'No size info')}
Unique Fact: {facts.get('fact_level_2', {}).get('unique_fact', 'No unique fact')}
Habitat: {facts.get('fact_level_2', {}).get('habitat', 'No habitat info')}

Requirements:
1. Make it sound like a friendly, excited nature guide talking to kids
2. Vary the order of facts in each script
3. Use simple words kids can understand
4. Add enthusiasm with words like "Wow!", "Guess what?", "Amazing!"
5. Keep each script under 30 words for simple, under 50 for detailed
6. Make each script unique in structure and phrasing

Format your response as JSON:
{{
  "name_script": "Short script introducing the animal",
  "simple_script": "Simple fact script with enthusiasm",
  "detailed_script": "Detailed facts in conversational style"
}}

Example for Lion:
{{
  "name_script": "Lion! Starts with L, the king of the jungle!",
  "simple_script": "Wow! I'm the king of the jungle with my big furry mane. I love to roar really loud to say hello to all my friends!",
  "detailed_script": "Guess what? I can weigh up to 400 pounds - that's as heavy as 50 kids! And my roar can travel 5 miles away. We live in sunny African savannas where we can nap all day!"
}}
"""

    try:
        response = model.generate_content(prompt)
        # Parse the JSON response
        script_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if script_text.startswith("```json"):
            script_text = script_text[7:]
        if script_text.endswith("```"):
            script_text = script_text[:-3]
        
        scripts = json.loads(script_text)
        return scripts
    except Exception as e:
        print(f"❌ Error generating script for {animal_name}: {e}")
        # Fallback to basic scripts
        return {
            "name_script": f"{animal_name}! Starts with {animal_name[0]}!",
            "simple_script": facts.get('fact_level_1', f"I'm a {animal_name}!"),
            "detailed_script": f"I'm a {animal_name}! {facts.get('fact_level_2', {}).get('unique_fact', '')}"
        }

def main():
    """Generate natural audio scripts for all animals."""
    print("🎤 Generating Natural Audio Scripts with Gemini...")
    
    # Initialize Gemini model
    model = genai.GenerativeModel('gemini-pro')
    
    # Load animals and facts
    animals_file = Path(__file__).parent.parent / "src/data" / "animals_clean.json"
    facts_file = Path(__file__).parent.parent / "src/data" / "facts_clean.json"
    
    with open(animals_file, 'r', encoding='utf-8') as f:
        animals = json.load(f)
    
    with open(facts_file, 'r', encoding='utf-8') as f:
        facts = json.load(f)
    
    # Create facts lookup
    facts_lookup = {fact['name']: fact for fact in facts}
    
    # Generate scripts for all animals
    all_scripts = {}
    success_count = 0
    
    for i, animal in enumerate(animals):
        animal_id = slugify(animal["name"])
        animal_facts = facts_lookup.get(animal["name"], {})
        
        print(f"\n🦁 [{i+1}/{len(animals)}] Generating script for: {animal['name']}")
        
        # Generate natural scripts
        scripts = generate_natural_script(animal["name"], animal_facts, model)
        all_scripts[animal_id] = scripts
        
        if scripts:
            success_count += 1
        
        # Rate limiting for Gemini
        time.sleep(1)
        
        # Save progress every 20 animals
        if (i + 1) % 20 == 0:
            output_file = Path(__file__).parent.parent / "src/data" / "audio_scripts.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_scripts, f, indent=2)
            print(f"💾 Saved progress: {i+1} animals")
    
    # Save final scripts
    output_file = Path(__file__).parent.parent / "src/data" / "audio_scripts.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_scripts, f, indent=2)
    
    print("\n✅ Script generation complete!")
    print(f"📊 Generated scripts for {success_count} animals")
    print(f"📁 Saved to: {output_file}")

if __name__ == "__main__":
    main()
