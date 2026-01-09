# Household Items Section

## Overview
A new section for learning common household items, vehicles, food, and everyday objects.

## Features
- **Ring binder style** - Same visual design as Animals section
- **Category filtering** - Filter by Kitchen, Bedroom, Bathroom, etc.
- **Touch audio** - Says item name when tapped
- **Responsive grid** - 3-6 columns depending on screen size
- **Visual feedback** - Hover and tap animations

## Current Test Items (3)
1. **Spoon** 🥄 - Kitchen
2. **Truck** 🚚 - Vehicles  
3. **Apple** 🍎 - Food

## Planned Categories
- Kitchen
- Bedroom
- Bathroom
- Living Room
- Vehicles
- Food
- Clothing
- Tools
- Nature
- Sports
- Music
- School

## Components Created
- `src/data/household_items.json` - Item data with 3 samples
- `src/components/HouseholdItemsBook.jsx` - Main component
- `scripts/generate_household_icons.py` - Generate AI icons with DALL-E
- `scripts/generate_household_audio.py` - Generate audio with Eleven Labs or OpenAI

## Next Steps - Choose One

### Option A: Test with Emojis (Quick)
- Works now with emoji placeholders
- No API calls needed
- Test the UI and functionality

### Option B: Generate AI Icons & Audio
- Run icon generation script
- Run audio generation script
- Requires API keys in .env file

## Commands

### Generate Icons
```bash
# Test run (no API calls)
python scripts/generate_household_icons.py --dry-run

# Generate specific items
python scripts/generate_household_icons.py --items spoon,truck,apple

# Generate all items
python scripts/generate_household_icons.py
```

### Generate Audio
```bash
# Test run (no API calls)
python scripts/generate_household_audio.py --dry-run

# Generate specific items with Eleven Labs
python scripts/generate_household_audio.py --items spoon,truck,apple

# Generate with OpenAI instead
python scripts/generate_household_audio.py --use-openai

# Generate all items
python scripts/generate_household_audio.py
```

## How to Add More Items
Add to `src/data/household_items.json`:
```json
{
  "id": "item_id",
  "name": "Item Name",
  "category": "Category",
  "emoji": "📦"
}
```

## Future Enhancement
Once test is approved, expand to 200+ items across all categories.
