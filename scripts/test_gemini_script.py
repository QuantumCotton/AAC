#!/usr/bin/env python3
"""Test Gemini script generation for one animal"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)

# Test with one animal
animal_name = "Lion"
facts = {
    "fact_level_1": "Lions are big cats that live in groups called prides.",
    "fact_level_2": {
        "size_details": "Lions can weigh up to 400 pounds",
        "unique_fact": "A lion's roar can be heard from 5 miles away",
        "habitat": "African savannas"
    }
}

prompt = f"""
Create THREE exciting audio scripts for kids about {animal_name}!

Facts to include:
- Simple: {facts.get('fact_level_1', 'No simple fact')}
- Size: {facts.get('fact_level_2', {}).get('size_details', 'No size info')}
- Special: {facts.get('fact_level_2', {}).get('unique_fact', 'No unique fact')}
- Home: {facts.get('fact_level_2', {}).get('habitat', 'No habitat info')}

Make each script different! Use fun words like "Wow!", "Guess what?", "Amazing!".
Keep it simple for 3-8 year olds.

Return JSON:
{{
  "name": "Short intro",
  "simple": "Simple fact with excitement",
  "detailed": "All facts in fun way"
}}

Example:
{{
  "name": "Lion! Starts with L, king of the jungle!",
  "simple": "Wow! I have a big furry mane and I roar super loud to say hi!",
  "detailed": "Guess what? I weigh as much as 50 kids! My roar travels 5 miles! We live in sunny Africa where we nap all day!"
}}
"""

model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content(prompt)

print("Response from Gemini:")
print(response.text)
