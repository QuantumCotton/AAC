# Background Image Requirements for Liora

## Overview
Each habitat needs a seamless, tileable background image that creates a themed "wallpaper" feel behind the animal cards. The app layers a color tint + pattern over these images, so they should be **subtle** and not too busy.

## Technical Specs

| Property | Value |
|----------|-------|
| **Format** | WebP (preferred) or PNG |
| **Size** | 320×320 pixels (will be tiled/repeated) |
| **Style** | Soft, dreamy, slightly blurred, low-contrast |
| **Colors** | Muted pastels matching habitat theme |
| **Tile-friendly** | Edges should blend seamlessly when repeated |

## File Locations
Place images in: `public/assets/backgrounds/`

## Required Files (10 total)

### 1. `farm.webp`
- **Theme**: Sunny farmland
- **Elements**: Rolling green hills, wooden fences, hay bales (subtle)
- **Color palette**: Soft greens (#D9F99D), warm yellows, brown accents

### 2. `domestic.webp`
- **Theme**: Cozy home environment
- **Elements**: Soft cushions, window light, warm indoor feeling
- **Color palette**: Warm yellows (#FEF08A), cream, light orange

### 3. `forest.webp`
- **Theme**: Temperate woodland
- **Elements**: Tree trunks, dappled sunlight through leaves, ferns
- **Color palette**: Forest greens (#BBF7D0), brown bark, mossy tones

### 4. `jungle.webp`
- **Theme**: Tropical rainforest
- **Elements**: Large leaves, vines, exotic flowers (subtle), misty
- **Color palette**: Vibrant greens (#A7F3D0), tropical accents

### 5. `nocturnal.webp`
- **Theme**: Nighttime / twilight
- **Elements**: Moon glow, stars, soft shadows, purple sky
- **Color palette**: Deep purples (#E9D5FF), midnight blue, silver

### 6. `arctic.webp`
- **Theme**: Frozen tundra / ice
- **Elements**: Snow drifts, ice crystals, northern lights (subtle)
- **Color palette**: Icy blues (#BFDBFE), white, pale cyan

### 7. `shallow_water.webp`
- **Theme**: Beach / coastal waters
- **Elements**: Sandy bottom, gentle waves, sunlight through water
- **Color palette**: Turquoise (#A5F3FC), sandy beige, foam white

### 8. `coral_reef.webp`
- **Theme**: Vibrant reef
- **Elements**: Coral formations, bubbles, colorful but soft
- **Color palette**: Ocean blue (#BAE6FD), coral pinks, seafoam

### 9. `deep_sea.webp`
- **Theme**: Dark ocean depths
- **Elements**: Bioluminescent dots, dark water, mysterious glow
- **Color palette**: Deep slate (#CBD5E1), navy, subtle glowing accents

### 10. `ultra_deep_sea.webp`
- **Theme**: Abyssal zone / Mariana Trench
- **Elements**: Near-black water, sparse bioluminescence, pressure feeling
- **Color palette**: Near-black (#E2E8F0 tinted dark), faint blue glow

## Image Generation Prompts (for AI tools)

You can use these prompts with Midjourney, DALL-E, or Stable Diffusion:

```
Farm:
"Seamless tileable pattern, soft watercolor farmland, rolling green hills, wooden fence, hay bales, sunny day, muted pastel colors, dreamy blurred style, children's book illustration, 320x320"

Forest:
"Seamless tileable pattern, temperate forest floor, tree trunks, dappled sunlight, ferns and moss, soft green tones, dreamy watercolor style, gentle blur, children's book illustration, 320x320"

Arctic:
"Seamless tileable pattern, snowy arctic landscape, ice crystals, soft blue and white, northern lights glow, dreamy watercolor style, children's book illustration, 320x320"

Deep Sea:
"Seamless tileable pattern, deep ocean water, bioluminescent particles, dark blue and black, mysterious glow, soft dreamy style, children's book illustration, 320x320"
```

## Notes

1. **Kid Mode vs Education Mode**: The app automatically adjusts overlay opacity:
   - Kid Mode: Brighter, more colorful overlay
   - Education Mode: Slightly muted, professional feel

2. **Don't make images too detailed** - they sit behind cards and should create atmosphere, not distract

3. **Test tiling** - open image in an editor and tile it 3×3 to check for obvious seams

4. **Fallback**: If an image is missing, the app uses a solid color background based on the habitat's theme color
