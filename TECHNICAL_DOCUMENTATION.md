# Animal Learning Application - Technical Documentation

## Table of Contents
- [1. Overall Architecture](#1-overall-architecture)
- [2. Animal Section Structure](#2-animal-section-structure)
- [3. Press-and-Hold Implementation](#3-press-and-hold-implementation)
- [4. Audio System](#4-audio-system)
- [5. Eleven Labs Integration](#5-eleven-labs-integration)
- [6. Data Structure](#6-data-structure)
- [7. Theme System](#7-theme-system)

---

## 1. Overall Architecture

The app is a React + Vite application with a LeapFrog-style book interface for animal education.

**Main Entry:** `src/App.jsx`
- Manages different "books" via `currentBook` state
- Books: Animals, ASL (Liora), Places
- Uses Context Providers: Theme, Audio, Asset, FactLevel, Accessibility

**Key Dependencies:**
- React 18
- Howler.js (audio playback)
- Tailwind CSS (styling)
- Vite (build tool)

---

## 2. Animal Section Structure

### LeapFrogBook Component (`src/components/LeapFrogBook.jsx`)

**Layout:**
- Book-style interface with spiral binding in center
- Left and right pages display animals
- Rainbow spiral colors (LeapFrog aesthetic)

**Pagination:**
- Animals organized by habitats
- 9 animals per page (3x3 grid)
- Pages grouped into "spreads" (2 pages per view)
- Total spreads calculated based on habitat sizes

**Habitats:**
1. Farm
2. Domestic
3. Forest
4. Jungle
5. Nocturnal
6. Arctic
7. Shallow Water
8. Coral Reef
9. Deep Sea
10. Ultra Deep Sea

**Navigation:**
- Tap left/right edges of book to turn pages
- Swipe gestures for mobile (touch events)
- Habitat tabs on left edge (completed habitats)
- Habitat tabs on right edge (current + upcoming habitats)
- Page flip animation with 650ms total duration

**Features:**
- Theme toggle: Toy (🧸) / Real (📷) modes
- Fact level toggle: Kids (👶) / Education (🎓) modes
- Download progress indicator (SyncScreen)

### AnimalCard Component (`src/components/AnimalCard.jsx`)

**Display:**
- Animal image with aspect-square container
- Animal name displayed below image
- Download indicator if assets not downloaded
- Active indicator (green dot) when playing audio

**Card Flip Animation:**
- 3D CSS flip with `rotateY(180deg)`
- Front: Animal image
- Back: Fact text with gradient background
- Perspective: 1000px

**Image Paths:**
- Toy mode: `/assets/images/toy_mode/{animal_id}.webp`
- Real mode: `/assets/images/real_mode/{animal_id}.webp`

---

## 3. Press-and-Hold Implementation

**AnimalCard.jsx** handles touch interactions with accessibility features for autistic users.

### Constants
```javascript
const HOLD_MS = 300;              // Hold time for intentional touch
const MOVE_PX = 25;               // Movement tolerance
const MIN_TOUCH_DURATION = 150;      // Minimum touch duration
const MAX_RAPID_TOUCHES = 3;        // Block after too many rapid touches
const RAPID_TOUCH_WINDOW = 1000;    // Time window for rapid touch detection
```

### Interaction States
```javascript
// Animation states
'idle' | 'popping' | 'flipped' | 'unflipping' | 'shrinking'

// Touch tracking
pressStartRef - Timestamp when press began
pressPointerIdRef - Pointer ID of current touch
didLongPressRef - Whether long press triggered
startPosRef - Starting coordinates {x, y}
holdTimerRef - setTimeout reference
```

### Behaviors

**Short Tap** (< 300ms):
- Plays animal name audio
- Uses `useAudio().playSound(paths.nameAudio, animal.id)`

**Long Press** (≥ 300ms):
1. Card pops out (scales to 1.15x)
2. Wait 300ms
3. Card flips (shows fact text)
4. Wait 400ms
5. Plays fact audio and waits for completion
6. Waits 300ms
7. Card flips back
8. Waits 400ms
9. Card shrinks to normal (1.0x)
10. Returns to 'idle'

### Accessibility Features

**Intentional Touch Detection:**
- Checks touch duration and movement
- Blocks if movement > 25px (tolerant for wobbly hands)
- Requires minimum 150ms touch duration

**Multi-Touch Protection:**
- Blocks if `isMultiTouchBlocked` is true
- Cancels if `e.touches.length > 1`
- Prevents accidental multi-touch triggers

**Rapid Touch Prevention:**
- Counts touches within 1-second window
- Blocks after 3 rapid touches
- Resets after 2-second block period

**iOS Protection:**
- `touchAction: 'none'` prevents long-press menu
- `WebkitTouchCallout: 'none'` prevents save dialog
- `onContextMenu` and `onDragStart` prevention

---

## 4. Audio System

### AudioContext (`src/contexts/AudioContext.jsx`)

**Library:** Howler.js
- Cross-browser audio support
- Better than HTML5 Audio for mobile

**State:**
```javascript
currentSound - Currently playing Howl instance
isPlaying - Boolean playback status
activeAnimalId - ID of currently playing animal
```

**Features:**

**Caching System:**
- LRU cache with max 40 sounds
- `soundCacheRef` - Map of cached Howl instances
- `cacheOrderRef` - Array of keys for eviction order
- Evicts oldest sounds when cache is full

**Audio Unlock:**
- Howler AudioContext starts 'suspended'
- Unlocked on first user interaction (pointerdown, touchstart, mousedown)
- Prevents audio auto-play blocking

**Click Sound:**
- Generated with Web Audio API (no external file)
- Square wave oscillator at 820Hz
- Duration: 50ms with exponential decay envelope

**Playback:**
```javascript
playSound(src, animalId, opts)
- Stops current sound if different
- Creates or retrieves cached Howl
- Sets activeAnimalId
- Calls opts.onEnd when complete
- Tracks interaction stats in localStorage
```

### Audio File Structure

```
public/assets/audio/
├── names/
│   ├── mariana_snailfish_name.mp3
│   ├── polar_bear_name.mp3
│   └── ...
├── facts/
│   ├── mariana_snailfish_fact_simple.mp3
│   ├── mariana_snailfish_fact_detailed.mp3
│   ├── polar_bear_fact_simple.mp3
│   └── ...
└── phonics/
    ├── letter_A.mp3
    ├── letter_B.mp3
    └── letter_Z.mp3
```

---

## 5. Eleven Labs Integration

### Script: `scripts/generate_natural_audio_simple.py`

**Purpose:** Generate natural, kid-friendly audio scripts and convert to speech using Eleven Labs TTS.

### API Configuration

```python
# Environment Variables
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_monolingual_v1")
ELEVENLABS_NAME_MODEL = os.getenv("ELEVENLABS_NAME_MODEL", "eleven_multilingual_v2")

# Voice Settings
ELEVENLABS_STABILITY = 0.55
ELEVENLABS_SIMILARITY_BOOST = 0.80
ELEVENLABS_STYLE = 0.0
ELEVENLABS_USE_SPEAKER_BOOST = True
ELEVENLABS_OUTPUT_FORMAT = "mp3_44100_128"
```

### Audio Generation Process

#### Step 1: Script Generation (OpenAI GPT-5-mini)

**System Prompt:**
```
You write SHORT, cute-but-calm, kid-friendly animal fact lines for ages 3–8.
The audio plays immediately when a child presses a button; avoid leading silence.
The text will be read by ElevenLabs; use punctuation for natural pauses.
You MUST use the provided facts only (no guessing).
Avoid cheesy templates. Output plain text only.
```

**Voice Tags (Eleven Labs v3):**
- `[curious]` - Inquisitive tone
- `[excited]` - High energy
- `[thoughtful]` - Calm, reflective
- `[surprised]` - Mild shock
- `[whispers]` - Soft, quiet
- `[giggles]` - Playful laughter
- `[chuckles]` - Light laugh
- `[sighs]` - Relief
- `[short pause]` - Brief break
- `[long pause]` - Extended break

**Banned Phrases:**
- "Did you know"
- "Guess what"
- "Wow", "Amazing", "Incredible"
- "Happy"
- "Listen to this"
- "Here's something interesting"
- "Fun fact"
- "Something special"
- "Meet the"
- "Special"

**Script Structure:**

Simple Mode:
```
[tag] I'm a/an {animal}. {one factual sentence}.
Example: [curious] I'm a Mariana Snailfish. I'm the deepest swimming fish in the whole ocean!
```

Detailed Mode:
```
{multiple sentences combining size, unique facts, and habitat}
Example: I'm a Mariana Snailfish. I can grow up to 11 inches long and weigh around 0.5 pounds. Each fish has a unique whistle like a name. I live in warm oceans all around the world.
```

#### Step 2: API Call to Eleven Labs

```python
url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
headers = {
    "xi-api-key": ELEVENLABS_API_KEY,
    "Content-Type": "application/json",
    "Accept": "audio/mpeg",
}
data = {
    "text": cleaned_text,
    "model_id": ELEVENLABS_MODEL,
    "voice_settings": {
        "stability": 0.55,  # v3 requires 0.0, 0.5, or 1.0
        "similarity_boost": 0.80,
        "use_speaker_boost": True,
        "style": 0.0,
    },
    "output_format": "mp3_44100_128",
}
```

#### Step 3: Retry Logic

**Rate Limiting (HTTP 429):**
- Wait: 3s, 6s, 9s (exponential backoff)
- Max 3 retries

**Quota Errors:**
- `insufficient_credits`
- `quota_exceeded`
- `rate_limit_exceeded`
- `voice_limit_reached`
- `subscription_required`
- Raises RuntimeError and stops execution

**Other Errors:**
- Logs error message
- Returns False
- Continues to next animal

#### Step 4: Batch Processing

**Batches:** 3 animals per batch

**Workflow:**
1. Generate simple scripts with OpenAI for all 3 animals
2. Save to `simple_scripts.json` for review
3. Generate name audio (uses `ELEVENLABS_NAME_MODEL`)
4. Generate simple fact audio
5. Generate detailed fact audio
6. Wait 1 second between batches

#### Step 5: Special Features

**Hardcoded Overrides:**
Some animals have problematic AI outputs, so they're hardcoded:
- Bottlenose Dolphin
- Dolphin

**Lock Files:**
- Located at `public/assets/audio/.locks/{animal_id}.lock`
- Prevents duplicate processing
- Auto-releases after 6 hours (stale)

**Resume Mode:**
- `--resume`: Auto-detects first incomplete animal
- `--reverse`: Processes from end to start
- `--start N`: Start at specific animal
- `--limit N`: Process N animals total

**Fallback to TTS:**
If audio file fails to load, falls back to Web Speech API:
```javascript
const utterance = new SpeechSynthesisUtterance(text);
utterance.rate = 0.85;
window.speechSynthesis.speak(utterance);
```

### CLI Usage

```bash
# Generate all audio
python scripts/generate_natural_audio_simple.py

# Resume from incomplete
python scripts/generate_natural_audio_simple.py --resume

# Specific category only
python scripts/generate_natural_audio_simple.py --category "Farm"

# Only names (no facts)
python scripts/generate_natural_audio_simple.py --only-name

# Only simple facts with OpenAI
python scripts/generate_natural_audio_simple.py --only-simple --simple-openai

# Generate scripts only (no audio)
python scripts/generate_natural_audio_simple.py --write-simple-scripts

# Use existing scripts
python scripts/generate_natural_audio_simple.py --use-simple-scripts src/data/simple_scripts.json

# Batch size
python scripts/generate_natural_audio_simple.py --batch-size 5
```

---

## 6. Data Structure

### Animal Object (`src/data/animals.json`)

```json
{
  "id": "mariana_snailfish",
  "name": "Mariana Snailfish",
  "category": "Ultra Deep Sea",
  "fact": "The Mariana snailfish lives at depths of up to 8,000 meters and is one of the deepest-living fish ever found!",
  "fact_level_1": "I am the deepest swimming fish in the whole ocean! I look like a pink tadpole.",
  "fact_level_2": {
    "size_details": "Length: up to 11 inches. Weight: ~0.5 lbs (No significant gender difference).",
    "unique_fact": "It has transparent skin that lets you see its liver!",
    "habitat": "The Mariana Trench (26,000+ feet deep)"
  }
}
```

**Fields:**
- `id`: Unique slug identifier
- `name`: Display name
- `category`: Habitat category
- `fact`: Legacy fact string
- `fact_level_1`: Simple kid-friendly fact
- `fact_level_2`: Detailed facts object with multiple fields

### Asset Paths (`src/utils/slugify.js`)

**Slugify Function:**
```javascript
function slugify(name) {
  return name
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '_')
    .replace(/-+/g, '_')
    .replace(/^_+|_+$/g, '');
}
```

**Examples:**
- "Red-Eyed Tree Frog" → "red_eyed_tree_frog"
- "Bottlenose Dolphin" → "bottlenose_dolphin"
- "Mariana Snailfish" → "mariana_snailfish"

**getAssetPaths Function:**
```javascript
function getAssetPaths(animalId) {
  return {
    toyImage: `/assets/images/toy_mode/${animalId}.webp`,
    realImage: `/assets/images/real_mode/${animalId}.webp`,
    nameAudio: `/assets/audio/names/${animalId}_name.mp3`,
    factAudioSimple: `/assets/audio/facts/${animalId}_fact_simple.mp3`,
    factAudioDetailed: `/assets/audio/facts/${animalId}_fact_detailed.mp3`,
    factAudioLegacy: `/assets/audio/facts/${animalId}_fact.mp3`,
    phonicsAudio: `/assets/audio/phonics/letter_${animalId.charAt(0).toUpperCase()}.mp3`
  };
}
```

---

## 7. Theme System

### ThemeContext (`src/contexts/ThemeContext.jsx`)

**Modes:**
1. **Toy Mode** (`theme === 'toy'`)
   - Cute cartoon-style illustrations
   - Path: `/assets/images/toy_mode/`
   - Icon: 🧸

2. **Real Mode** (`theme === 'real'`)
   - Realistic photographs
   - Path: `/assets/images/real_mode/`
   - Icon: 📷

### FactLevelContext (`src/contexts/FactLevelContext.jsx`)

**Modes:**
1. **Kids Mode** (`isSimpleLevel === true`)
   - Simple facts (1-2 sentences)
   - Icon: 👶
   - Color: Pink-400

2. **Education Mode** (`isSimpleLevel === false`)
   - Detailed facts (3-4 sentences)
   - Icon: 🎓
   - Color: Blue-500

---

## Key Technical Decisions

1. **Howler.js**: Chosen for audio playback due to better cross-browser and mobile support compared to HTML5 Audio

2. **Pointer Events**: Used for unified touch/mouse handling, works seamlessly across desktop and mobile platforms

3. **CSS 3D Transforms**: Card flip animation using `rotateY(180deg)` with `preserve-3d` transform style

4. **LRU Cache**: Audio caching with max 40 sounds prevents redundant network requests and improves performance

5. **Intentional Touch**: Accessibility feature designed for autistic users to filter out accidental touches

6. **Eleven Labs v3**: Supports expressive voice tags (`[curious]`, `[excited]`, etc.) for more animated speech

7. **OpenAI GPT-5-mini**: Used for script generation to ensure varied, non-repetitive, kid-friendly content

8. **Batch Processing**: Generates scripts for multiple animals in one API call to save time and costs

9. **Lock Files**: Prevents duplicate audio generation when running multiple processes

10. **Web Speech API Fallback**: Ensures audio playback continues even if Eleven Labs audio files fail to load

---

## File Structure

```
e:\Projects\animal learning\
├── src/
│   ├── App.jsx                          # Main app component
│   ├── components/
│   │   ├── LeapFrogBook.jsx            # Animal book interface
│   │   ├── AnimalCard.jsx               # Individual animal card
│   │   ├── MainMenu.jsx                 # Book selection menu
│   │   └── ...
│   ├── contexts/
│   │   ├── AudioContext.jsx             # Audio playback system
│   │   ├── ThemeContext.jsx            # Theme management
│   │   ├── FactLevelContext.jsx         # Fact level management
│   │   ├── AccessibilityContext.jsx      # Accessibility features
│   │   └── AssetContext.jsx            # Asset download tracking
│   ├── data/
│   │   ├── animals.json                # Animal data with facts
│   │   └── habitats.js               # Habitat definitions
│   └── utils/
│       └── slugify.js                 # Path generation
├── public/
│   └── assets/
│       ├── images/
│       │   ├── toy_mode/              # Cartoon images
│       │   └── real_mode/             # Real photos
│       └── audio/
│           ├── names/                   # Animal name audio
│           ├── facts/                   # Fact audio
│           └── phonics/               # Letter sounds
└── scripts/
    └── generate_natural_audio_simple.py  # Audio generation script
```

---

## Environment Variables (.env)

```bash
# Eleven Labs
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL=eleven_monolingual_v1
ELEVENLABS_NAME_MODEL=eleven_multilingual_v2
ELEVENLABS_STABILITY=0.55
ELEVENLABS_SIMILARITY_BOOST=0.80
ELEVENLABS_STYLE=0.0
ELEVENLABS_USE_SPEAKER_BOOST=true
ELEVENLABS_OUTPUT_FORMAT=mp3_44100_128

# OpenAI
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-5-mini
```

---

## Development Workflow

### Adding New Animals

1. Add entry to `src/data/animals.json`
2. Generate images (toy and real) - place in `public/assets/images/`
3. Run audio generation:
   ```bash
   python scripts/generate_natural_audio_simple.py --resume
   ```

### Modifying Audio Scripts

1. Edit `scripts/generate_natural_audio_simple.py`
2. Adjust system prompts or banned phrases
3. Regenerate scripts only:
   ```bash
   python scripts/generate_natural_audio_simple.py --write-simple-scripts
   ```
4. Review `src/data/simple_scripts.json`
5. Regenerate audio with approved scripts:
   ```bash
   python scripts/generate_natural_audio_simple.py --use-simple-scripts src/data/simple_scripts.json
   ```

---

## Performance Optimizations

1. **Audio Caching**: LRU cache prevents redundant downloads
2. **Lazy Loading**: Images use `loading="lazy"`
3. **Debounced Touches**: Rapid touch detection prevents excessive animations
4. **Batch Generation**: Processes multiple animals per API call
5. **Selective Loading**: Only loads habitat assets when needed

---

## Accessibility Features

1. **Intentional Touch**: Filters accidental touches for autistic users
2. **Large Touch Targets**: Easy-to-tap cards
3. **Visual Feedback**: Active state indicators
4. **Keyboard Support**: (Can be added with Tab navigation)
5. **Voice Options**: Simple vs Education modes for different cognitive levels

---

## Future Enhancements

- [ ] Add keyboard navigation support
- [ ] Implement ARIA labels for screen readers
- [ ] Add progress persistence across sessions
- [ ] Support offline mode with Service Worker
- [ ] Add animation preferences (reduce motion option)
- [ ] Implement multi-language support
