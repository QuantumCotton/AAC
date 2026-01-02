import argparse
import json
import os
import re
from collections import Counter


HABITAT_ORDER = [
    'Farm',
    'Domestic',
    'Forest',
    'Jungle',
    'Nocturnal',
    'Arctic',
    'Shallow Water',
    'Coral Reef',
    'Deep Sea',
    'Ultra Deep Sea',
]


REMOVE_NAMES = [
    'Abyssal Spiderfish', 'Barreleye', 'Black Swallower', 'Blobfish', 'Coffinfish', 'Cookiecutter Shark',
    'Dragonfish', 'Faceless Cusk', 'Fangtooth', 'Frilled Shark', 'Ghost Shark', 'Goblin Shark',
    'Gulper Eel', 'Hatchetfish', 'Lizardfish', 'Mariana Snailfish', 'Stoplight Loosejaw',
    'Vampire Squid', 'Viperfish', 'Zombie Worm',
    'Big Red Jelly',
    'Acorn Worm', 'Basket Star', 'Brisingid Starfish', 'Giant Tube Worm', 'Glass Sponge', 'Monophore',
    'Ping Pong Tree Sponge', 'Sea Pen', 'Sea Pig', 'Siphonophore',
    'Cacomistle', 'Civet', 'Cusk Eel', 'Deep Sea Amphipod', 'Genet', 'Grenadier Fish',
    'Krill (Antarctic)', 'Napoleon Wrasse', 'Oarfish', 'Spookfish', 'Tripod Fish'
]


ADD_NAMES = [
    'Lion',
    'African Elephant',
    'Giraffe',
    'Zebra',
    'Hippopotamus',
    'Rhinoceros',
    'Cheetah',
    'Leopard',
    'Kangaroo',
    'Wallaby',
    'Giant Panda',
    'Red Panda',
    'Gorilla',
    'Baboon',
    'Basset Hound', 'Beagle', 'Boxer', 'Bulldog', 'Chihuahua', 'Corgi', 'Dachshund', 'Dalmatian',
    'Doberman', 'German Shepherd', 'Great Dane', 'Greyhound', 'Husky', 'Jack Russell', 'Labrador',
    'Pitbull', 'Pomeranian', 'Poodle', 'Pug', 'Rottweiler', 'Saint Bernard', 'Shiba Inu',
    'Bald Eagle', 'Budgie', 'Canary', 'Cockatoo', 'Crow', 'Dove', 'Emu', 'Flamingo', 'Heron',
    'Kingfisher', 'Magpie', 'Mockingbird', 'Nightingale', 'Ostrich', 'Peacock', 'Pelican', 'Raven',
    'Robin', 'Sparrow', 'Stork', 'Swan', 'Vulture',
    'Meerkat',
    'Capybara',
    'Quokka',
    'Sloth',
    'Komodo Dragon',
    'Cobra',
    'King Cobra',
    'Alligator',
    'Crocodile',
]


DEFAULT_DEEP_SEA_FILLERS = [
    'Giant Isopod',
    'Coelacanth',
]

EXTRA_REAL_FILLERS = [
    'Manatee',
    'Sea Otter',
    'Sea Turtle',
    'Blue Whale',
    'Orca',
    'Humpback Whale',
    'Giant Clam',
    'Manta Ray',
    'Stingray',
    'Hammerhead Shark',
    'Great White Shark',
    'Dolphin',
]


DEEP_SEA_FUN_SPOOKY = [
    'Anglerfish',
    'Giant Squid',
    'Colossal Squid',
    'Vampire Squid',
    'Goblin Shark',
    'Frilled Shark',
    'Six-Gill Shark',
    'Cookiecutter Shark',
    'Chimaera',
    'Gulper Eel',
    'Viperfish',
    'Dragonfish',
    'Lanternfish',
    'Hatchetfish',
    'Fangtooth',
    'Barreleye',
    'Oarfish',
    'Japanese Spider Crab',
    'Nautilus',
    'Wolffish',
    'Sperm Whale',
    'Beaked Whale',
    'Elephant Seal',
    'Coelacanth',
]

ULTRA_DEEP_SEA_FUN_SPOOKY = [
    'Mariana Snailfish',
    'Dumbo Octopus',
    'Tripod Fish',
    'Grenadier Fish',
    'Cusk Eel',
    'Snipe Eel',
    'Spookfish',
    'Deep Sea Jellyfish',
    'Giant Isopod',
    'Glass Sponge',
    'Siphonophore',
    'Comb Jelly',
]


DOG_BREEDS = {
    'Basset Hound','Beagle','Boxer','Bulldog','Chihuahua','Corgi','Dachshund','Dalmatian','Doberman',
    'German Shepherd','Great Dane','Greyhound','Husky','Jack Russell','Labrador','Pitbull','Pomeranian',
    'Poodle','Pug','Rottweiler','Saint Bernard','Shiba Inu'
}

PET_BIRDS = {'Budgie', 'Canary', 'Cockatoo'}
WATER_BIRDS = {'Flamingo', 'Heron', 'Kingfisher', 'Pelican', 'Stork', 'Swan'}
LAND_BIRDS = {'Bald Eagle', 'Crow', 'Dove', 'Magpie', 'Mockingbird', 'Nightingale', 'Raven', 'Robin', 'Sparrow', 'Vulture', 'Peacock'}
BIG_BIRDS = {'Ostrich', 'Emu'}


def slugify(name: str) -> str:
    s = (name or '').lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'\s+', '_', s)
    s = re.sub(r'-+', '_', s)
    s = re.sub(r'^_+|_+$', '', s)
    return s


def category_for_name(name: str) -> str:
    if name in set(DEEP_SEA_FUN_SPOOKY):
        return 'Deep Sea'
    if name in set(ULTRA_DEEP_SEA_FUN_SPOOKY):
        return 'Ultra Deep Sea'

    if name in DOG_BREEDS:
        return 'Domestic'
    if name in PET_BIRDS:
        return 'Domestic'
    if name in WATER_BIRDS:
        return 'Shallow Water'
    if name in BIG_BIRDS:
        return 'Jungle'
    if name in LAND_BIRDS:
        return 'Forest'

    if name in {'Alligator', 'Crocodile', 'Komodo Dragon', 'Cobra', 'King Cobra'}:
        return 'Jungle'

    if name in {'Meerkat', 'Capybara', 'Quokka', 'Sloth'}:
        return 'Jungle'

    if name in {
        'Lion','African Elephant','Giraffe','Zebra','Hippopotamus','Rhinoceros','Cheetah','Leopard',
        'Kangaroo','Wallaby','Giant Panda','Red Panda','Gorilla','Baboon'
    }:
        return 'Jungle'

    if name in DEFAULT_DEEP_SEA_FILLERS:
        return 'Deep Sea'

    if name in {'Manatee', 'Sea Otter', 'Sea Turtle', 'Dolphin'}:
        return 'Shallow Water'

    if name in {'Blue Whale', 'Orca', 'Humpback Whale'}:
        return 'Deep Sea'

    if name in {'Giant Clam', 'Manta Ray', 'Stingray'}:
        return 'Coral Reef'

    if name in {'Hammerhead Shark', 'Great White Shark'}:
        return 'Deep Sea'

    return 'Forest'


def sort_key(item: dict):
    cat = (item.get('category') or '').strip()
    name = (item.get('name') or '').strip()
    try:
        cat_idx = HABITAT_ORDER.index(cat)
    except ValueError:
        cat_idx = 999
    return (cat_idx, cat, name.lower())


def _unique_by_name(rows):
    seen = set()
    out = []
    for r in rows:
        n = r.get('name')
        if n and n not in seen:
            out.append(r)
            seen.add(n)
    return out


def enforce_category_roster(rows, category: str, desired_names):
    desired = [n for n in desired_names if isinstance(n, str) and n.strip()]
    desired_set = set(desired)
    kept_other = [r for r in rows if (r.get('category') or '').strip() != category]
    existing_in_cat = [r for r in rows if (r.get('category') or '').strip() == category]
    existing_by_name = {r.get('name'): r for r in existing_in_cat if r.get('name')}

    rebuilt = []
    for name in desired:
        r = existing_by_name.get(name)
        if not r:
            r = {'id': slugify(name), 'name': name, 'category': category, 'fact': ''}
        else:
            r = dict(r)
            r['id'] = r.get('id') or slugify(name)
            r['category'] = category
        rebuilt.append(r)

    return _unique_by_name(kept_other + rebuilt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--target-multiple-of-12', type=int, default=0, help='If >0, pad with real filler animals to reach this total and keep divisible by 12')
    ap.add_argument('--pad-to-next-multiple-of-12', action='store_true', help='Pad with real filler animals until total is divisible by 12')
    ap.add_argument('--animals-json', default=os.path.join('src','data','animals.json'))
    ap.add_argument('--animals-clean', default=os.path.join('src','data','animals_clean.json'))
    ap.add_argument('--add-all', action='store_true', help='Add all ADD_NAMES (default)')
    ap.add_argument('--no-fillers', action='store_true', help='Do not add default deep sea fillers')
    args = ap.parse_args()

    with open(args.animals_json, 'r', encoding='utf-8') as f:
        animals = json.load(f)

    before_count = len(animals)
    before_names = {a.get('name') for a in animals}

    remove_set = set(REMOVE_NAMES)
    kept = [a for a in animals if a.get('name') not in remove_set]

    removed_present = [n for n in REMOVE_NAMES if n in before_names]

    add_list = list(ADD_NAMES)
    if not args.no_fillers:
        for n in DEFAULT_DEEP_SEA_FILLERS:
            if n not in add_list:
                add_list.append(n)

    kept_names = {a.get('name') for a in kept}

    to_add = [n for n in add_list if n not in kept_names]

    for name in to_add:
        entry = {
            'id': slugify(name),
            'name': name,
            'category': category_for_name(name),
            'fact': ''
        }
        kept.append(entry)

    kept = enforce_category_roster(kept, 'Deep Sea', DEEP_SEA_FUN_SPOOKY)
    kept = enforce_category_roster(kept, 'Ultra Deep Sea', ULTRA_DEEP_SEA_FUN_SPOOKY)

    after_count = len(kept)

    filler_pool = list(EXTRA_REAL_FILLERS)

    if args.target_multiple_of_12 and args.target_multiple_of_12 > 0:
        target = int(args.target_multiple_of_12)
        if target % 12 != 0:
            raise SystemExit('--target-multiple-of-12 must be divisible by 12')
        if after_count > target:
            raise SystemExit(f'Current total {after_count} exceeds target {target}. Remove fewer or raise target.')
        pad_needed = target - after_count
        if pad_needed > len(filler_pool):
            raise SystemExit(f'Need {pad_needed} filler animals but only have {len(filler_pool)}. Add more to EXTRA_REAL_FILLERS.')
        used = {a.get('name') for a in kept}
        added_now = 0
        for name in filler_pool:
            if added_now >= pad_needed:
                break
            if name in used:
                continue
            kept.append({'id': slugify(name), 'name': name, 'category': category_for_name(name), 'fact': ''})
            used.add(name)
            added_now += 1
        if added_now != pad_needed:
            raise SystemExit(f'Could not add enough unique filler animals. Needed {pad_needed}, added {added_now}.')
        after_count = len(kept)

    if args.pad_to_next_multiple_of_12:
        rem = after_count % 12
        pad_needed = (12 - rem) % 12
        if pad_needed:
            used = {a.get('name') for a in kept}
            added_now = 0
            for name in filler_pool:
                if added_now >= pad_needed:
                    break
                if name in used:
                    continue
                kept.append({'id': slugify(name), 'name': name, 'category': category_for_name(name), 'fact': ''})
                used.add(name)
                added_now += 1
            if added_now != pad_needed:
                raise SystemExit(f'Could not add enough unique filler animals. Needed {pad_needed}, added {added_now}.')
            after_count = len(kept)

    kept.sort(key=sort_key)

    cat_before = Counter(a.get('category') for a in animals)
    cat_after = Counter(a.get('category') for a in kept)

    print('=== UPDATE PREVIEW ===')
    print('Before:', before_count)
    print('Removed (present):', len(removed_present))
    print('Added:', len(to_add))
    print('After:', after_count)
    print('Divisible by 12:', (after_count % 12 == 0))
    print('Category before:', dict(cat_before))
    print('Category after:', dict(cat_after))

    if not args.apply:
        print('\nDry-run only. Re-run with --apply to write files.')
        return

    with open(args.animals_json, 'w', encoding='utf-8') as f:
        json.dump(kept, f, indent=2, ensure_ascii=False)

    clean = [{'name': a.get('name'), 'category': a.get('category')} for a in kept]
    with open(args.animals_clean, 'w', encoding='utf-8') as f:
        json.dump(clean, f, indent=2, ensure_ascii=False)

    print('\nWrote:')
    print(' -', args.animals_json)
    print(' -', args.animals_clean)


if __name__ == '__main__':
    main()
