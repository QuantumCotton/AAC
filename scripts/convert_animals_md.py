#!/usr/bin/env python3
"""Convert animals.md JSON to animals_fixed.json format."""
import json
import re
from pathlib import Path

# Map from animals.md categories to our app categories
CATEGORY_MAP = {
    "shoreline_intertidal_zone": "Shallow Water",
    "shallow_water_neritic_coral_reefs": "Coral Reef",
    "deep_water_bathypelagic_abyssal": "Deep Sea",
    "jungle_rainforest": "Jungle",
    "temperate_forest": "Forest",
    "desert_arid": "Nocturnal",  # Many desert animals are nocturnal
    "arctic_tundra": "Arctic",
    "wetlands_marshes_swamps": "Shallow Water",  # Close enough
    "rivers_lakes_lotic_lentic": "Shallow Water",
    "caves_subterranean": "Nocturnal",
    "urban_anthropogenic": "Domestic",
}

# Animals to skip (too obscure for kids or not kid-friendly)
SKIP_ANIMALS = {
    "bed bug", "cockroach", "silverfish", "house centipede", "mosquito",
    "lugworm", "sandhopper", "amphipod", "planarian", "isopod",
    "springtail", "pseudoscorpion", "cave beetle", "cave snail",
    "velvet worm", "harvestman", "bristlemouth", "deep sea prawn",
    "water scorpion", "mayfly", "water strider",
}

# Simple facts for common animals (kid-friendly)
SIMPLE_FACTS = {
    "clownfish": "Clownfish live in sea anemones that protect them from predators!",
    "blue tang": "Blue tangs can change color based on their mood!",
    "green sea turtle": "Sea turtles can hold their breath for over 5 hours!",
    "manta ray": "Manta rays have the largest brain of any fish!",
    "bottlenose dolphin": "Dolphins talk to their friends using clicks and whistles!",
    "polar bear": "Polar bears have black skin under their white fur!",
    "emperor penguin": "Emperor penguin dads keep eggs warm on their feet!",
    "lion": "Lions are the only cats that live in groups called prides!",
    "elephant": "Elephants can recognize themselves in a mirror!",
    "giraffe": "Giraffes have the same number of neck bones as humans - seven!",
    "gorilla": "Gorillas can learn sign language!",
    "chimpanzee": "Chimps use tools like sticks to catch termites!",
    "orangutan": "Orangutans build a new nest to sleep in every night!",
    "jaguar": "Jaguars have the strongest bite of all big cats!",
    "toucan": "A toucan's bill is light and hollow like a honeycomb!",
    "sloth": "Sloths are so slow that algae grows on their fur!",
    "poison dart frog": "One tiny poison dart frog has enough venom to harm 10 people!",
    "anaconda": "Anacondas can swallow animals bigger than their head!",
    "crocodile": "Crocodiles can't stick out their tongue!",
    "alligator": "Alligators have been around since dinosaur times!",
    "hippopotamus": "Hippos make their own pink sunscreen from their sweat!",
    "flamingo": "Flamingos are pink because of the shrimp they eat!",
    "beaver": "Beavers have orange teeth that never stop growing!",
    "platypus": "Platypuses are one of few mammals that lay eggs!",
    "koala": "Koalas sleep up to 22 hours a day!",
    "kangaroo": "Baby kangaroos are called joeys and live in mom's pouch!",
    "owl": "Owls can turn their heads almost all the way around!",
    "bat": "Bats are the only mammals that can truly fly!",
    "wolf": "Wolves howl to talk to their pack from far away!",
    "fox": "Foxes can hear a mouse under the snow from far away!",
    "bear": "Bears can smell food from 20 miles away!",
    "deer": "Deer grow new antlers every single year!",
    "rabbit": "Rabbits can't vomit - they have to eat carefully!",
    "squirrel": "Squirrels can find buried nuts even under snow!",
    "hedgehog": "Hedgehogs have about 5,000 spines on their back!",
    "octopus": "Octopuses have three hearts and blue blood!",
    "jellyfish": "Jellyfish have been around for over 500 million years!",
    "starfish": "Starfish can regrow their arms if they lose one!",
    "seahorse": "Seahorse dads carry the babies, not the moms!",
    "shark": "Sharks have been around longer than trees!",
    "whale": "Blue whales are the biggest animals that ever lived!",
    "dolphin": "Dolphins sleep with one eye open!",
    "seal": "Seals can hold their breath for up to 2 hours!",
    "walrus": "Walruses use their tusks to pull themselves onto ice!",
    "penguin": "Penguins propose to their mates with a pebble!",
    "parrot": "Parrots can live to be 80 years old!",
    "eagle": "Eagles can spot a rabbit from 2 miles away!",
    "hummingbird": "Hummingbirds can fly backwards!",
    "peacock": "Only male peacocks have those beautiful tail feathers!",
    "cow": "Cows have best friends and get sad when apart!",
    "pig": "Pigs are smarter than dogs!",
    "horse": "Horses can sleep standing up!",
    "chicken": "Chickens can remember over 100 faces!",
    "dog": "Dogs can smell 10,000 times better than humans!",
    "cat": "Cats spend 70% of their lives sleeping!",
    "hamster": "Hamsters can run 5 miles on their wheel each night!",
    "goldfish": "Goldfish can recognize their owners!",
}

def slugify(name):
    """Convert name to slug."""
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

def get_fact(name):
    """Get a simple fact for an animal."""
    name_lower = name.lower()
    # Check for exact match
    if name_lower in SIMPLE_FACTS:
        return SIMPLE_FACTS[name_lower]
    # Check for partial match
    for key, fact in SIMPLE_FACTS.items():
        if key in name_lower or name_lower in key:
            return fact.replace(key.title(), name)
    # Default fact
    return f"{name} is an amazing animal that lives in the wild!"

def main():
    # Read animals.md
    md_path = Path(__file__).parent.parent / "animals.md"
    with open(md_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    animals = []
    seen_names = set()
    
    # Process all habitat categories
    for habitat_type, habitats in data.items():
        for habitat_key, habitat_data in habitats.items():
            if isinstance(habitat_data, str):  # Skip notes
                continue
            
            category = CATEGORY_MAP.get(habitat_key, "Forest")
            
            # Process general inhabitants
            for animal in habitat_data.get("general_inhabitants", []):
                name = animal["common_name"]
                if name.lower() in SKIP_ANIMALS or name.lower() in seen_names:
                    continue
                seen_names.add(name.lower())
                
                animals.append({
                    "id": slugify(name),
                    "name": name,
                    "category": category,
                    "fact": get_fact(name),
                })
            
            # Process nocturnal inhabitants -> Nocturnal category
            for animal in habitat_data.get("nocturnal_inhabitants", []):
                name = animal["common_name"]
                if name.lower() in SKIP_ANIMALS or name.lower() in seen_names:
                    continue
                seen_names.add(name.lower())
                
                animals.append({
                    "id": slugify(name),
                    "name": name,
                    "category": "Nocturnal",
                    "fact": get_fact(name),
                })
    
    # Read existing animals_fixed.json to keep good ones
    existing_path = Path(__file__).parent.parent / "animals_fixed.json"
    with open(existing_path, "r", encoding="utf-8") as f:
        existing = json.load(f)
    
    # Keep existing animals that aren't in new list (Ultra Deep Sea, etc.)
    for animal in existing:
        name_lower = animal["name"].lower()
        if name_lower not in seen_names:
            # Keep Deep Sea and Ultra Deep Sea animals
            if animal["category"] in ["Deep Sea", "Ultra Deep Sea"]:
                animals.append(animal)
                seen_names.add(name_lower)
            # Keep Farm animals
            elif animal["category"] == "Farm":
                animals.append(animal)
                seen_names.add(name_lower)
            # Keep Domestic animals
            elif animal["category"] == "Domestic":
                animals.append(animal)
                seen_names.add(name_lower)
    
    # Sort by category then name
    category_order = ["Farm", "Domestic", "Forest", "Jungle", "Nocturnal", "Arctic", 
                      "Shallow Water", "Coral Reef", "Deep Sea", "Ultra Deep Sea"]
    animals.sort(key=lambda x: (category_order.index(x["category"]) if x["category"] in category_order else 99, x["name"]))
    
    # Write output
    output_path = Path(__file__).parent.parent / "animals_fixed_new.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(animals, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {len(animals)} animals")
    
    # Count by category
    from collections import Counter
    cats = Counter(a["category"] for a in animals)
    for cat, count in sorted(cats.items(), key=lambda x: category_order.index(x[0]) if x[0] in category_order else 99):
        print(f"  {cat}: {count}")

if __name__ == "__main__":
    main()
