# Alphabet Section - Documentation

## Overview

The Alphabet section is a new learning module in Liora's Learning Library that teaches the alphabet through interactive play. It includes three main pages with different learning modes and activities.

---

## Pages

### 1. Alphabet Grid (Main Page)
**Features:**
- All 26 letters displayed in alphabetical order (5x6 grid)
- Bright, colorful letters with toy-style design
- Two modes: **ABC** (letter names) and **Sound** (phonetic sounds)
- Tap any letter to hear its name or sound
- Smooth animations and visual feedback

**Toggle Button:**
- Located at top right corner
- Switch between "ABC" (purple) and "Sound" (green)
- Changes audio playback for all letters

### 2. Keyboard Layouts
**Features:**
- Three layout options:
  - **QWERTY** - Standard keyboard layout
  - **Dvorak** - Alternative keyboard layout (for learning efficiency)
  - **Vowels** - Just the 5 vowels (A, E, I, O, U)
- Tap any letter to hear its name
- Helps children learn keyboard layouts early

### 3. Letter Game
**Features:**
- Interactive letter recognition game
- Letters pop up randomly across screen with different sizes and rotations
- Sequence-based gameplay: A → B → C → D... (first 10 letters)
- Sound effects:
  - ✅ Correct: Fun popping sound
  - ❌ Wrong: Muffled error sound
  - 🔔 Interest: Loud ding (every 4 correct letters, or after 5 seconds of inactivity)
  - 📉 Boring: Soft buzz (error mode)

**Error Mode:**
- Activates when user taps 10+ times without correct letter within 3 seconds
- Screen dims to 50% brightness
- Red/dark background
- Blocks all taps for 3 seconds
- Prevents accidental noise from tapping for fun

**Progress:**
- Shows current target letter (e.g., "Find: A")
- Progress counter (e.g., "1 / 10")
- Wrong tap counter
- Completion celebration screen

---

## Audio Generation

### Voice Configuration

**Voice:** Mark (UgBBYS2sOqTuMpoF3BR0)
- Neutral American English
- Clear pronunciation
- No heavy accent

**Model:** Eleven Labs Turbo v2
- Supports phoneme tags for precise control
- Fast generation

### Pronunciation Dictionary

Uses phoneme tags to control exact pronunciation:

| Letter | Phoneme Tag | Sound |
|--------|--------------|-------|
| A | `<phoneme="ey">A</phoneme>` | "ay" |
| B | `<phoneme="bi">B</phoneme>` | "bee" |
| C | `<phoneme="si">C</phoneme>` | "see" |
| D | `<phoneme="di">D</phoneme>` | "dee" |
| E | `<phoneme="i">E</phoneme>` | "ee" |
| F | `<phoneme="ɛf">F</phoneme>` | "ef" |
| G | `<phoneme="dʒi">G</phoneme>` | "jee" |
| H | `<phoneme="eɪtʃ">H</phoneme>` | "aych" |
| I | `<phoneme="aɪ">I</phoneme>` | "eye" |
| J | `<phoneme="dʒeɪ">J</phoneme>` | "jay" |
| K | `<phoneme="keɪ">K</phoneme>` | "kay" |
| L | `<phoneme="ɛl">L</phoneme>` | "ell" |
| M | `<phoneme="ɛm">M</phoneme>` | "em" |
| N | `<phoneme="ɛn">N</phoneme>` | "en" |
| O | `<phoneme="oʊ">O</phoneme>` | "oh" |
| P | `<phoneme="pi">P</phoneme>` | "pee" |
| Q | `<phoneme="kyu">Q</phoneme>` | "kyoo" |
| R | `<phoneme="ɑr">R</phoneme>` | "ar" |
| S | `<phoneme="ɛs">S</phoneme>` | "ess" |
| T | `<phoneme="ti">T</phoneme>` | "tee" |
| U | `<phoneme="ju">U</phoneme>` | "you" |
| V | `<phoneme="vi">V</phoneme>` | "vee" |
| W | `<phoneme="dʌblju">W</phoneme>` | "double-you" |
| X | `<phoneme="ɛks">X</phoneme>` | "ex" |
| Y | `<phoneme="waɪ">Y</phoneme>` | "why" |
| Z | `<phoneme="zi">Z</phoneme>` | "zee" |

### Generating Audio

Run the script to generate all alphabet audio:

```bash
# Generate all audio (names and sounds)
python scripts/generate_alphabet_audio.py

# Generate letter names only
python scripts/generate_alphabet_audio.py --name-only

# Generate phonetic sounds only
python scripts/generate_alphabet_audio.py --sound-only

# Generate specific letters (e.g., just A-J)
python scripts/generate_alphabet_audio.py --letters "ABCDEFGHIJ"

# Resume from specific letter (skip existing)
python scripts/generate_alphabet_audio.py --skip-existing

# Test without API calls (dry run)
python scripts/generate_alphabet_audio.py --dry-run
```

### Output Files

Audio files are saved to:
```
public/assets/audio/alphabet/
├── letter_a_name.mp3      # "A"
├── letter_a_sound.mp3      # "ay" (phonetic)
├── letter_b_name.mp3      # "B"
├── letter_b_sound.mp3      # "bee"
└── ... (through z)
```

---

## File Structure

```
src/components/
├── AlphabetBook.jsx          # Main container (3 pages)
├── AlphabetGrid.jsx          # Page 1: A-Z grid
├── KeyboardLayout.jsx        # Page 2: Keyboard layouts
└── LetterGame.jsx           # Page 3: Letter recognition game
```

---

## Technical Details

### Color Scheme

Each letter has a unique color (repeating pattern):
- Red, Orange, Yellow, Green, Cyan, Blue, Purple, Pink
- Consistent across all pages

### Game Configuration

```javascript
const GAME_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'];
const POP_INTERVAL = 2000;        // New letter every 2 seconds
const WRONG_THRESHOLD = 10;         // 10 wrong taps trigger error mode
const ERROR_WINDOW = 3000;         // 3-second window
```

### Sound Effects (Web Audio API)

All game sounds are synthesized using the Web Audio API (no external files):

- **Correct**: Sine wave, 600-800Hz, short duration
- **Wrong**: Triangle wave, 150-100Hz, muffled
- **Ding**: Sine wave, 1200Hz, loud
- **Buzz**: Sawtooth wave, 80Hz, soft

### Accessibility

- **Intentional Touch**: Uses `useAccessibility` context to filter accidental touches
- **Large Touch Targets**: All buttons are large and easy to tap
- **Visual Feedback**: Clear state changes and animations
- **Error Prevention**: Error mode prevents accidental noise from tapping

---

## Environment Variables (.env)

```bash
# Eleven Labs Configuration
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_VOICE_ID=UgBBYS2sOqTuMpoF3BR0
ELEVENLABS_MODEL=eleven_turbo_v2
ELEVENLABS_STABILITY=0.75
ELEVENLABS_SIMILARITY_BOOST=0.85
ELEVENLABS_STYLE=0.0
ELEVENLABS_USE_SPEAKER_BOOST=true
ELEVENLABS_OUTPUT_FORMAT=mp3_44100_128
```

---

## Integration with App

The Alphabet section is integrated into the main app through:

1. **App.jsx**: Added routing for `'alphabet'` book ID
2. **MainMenu.jsx**: Added Alphabet book button (🔤 emoji)
3. **AudioContext**: Uses existing audio system for playback
4. **AccessibilityContext**: Uses existing intentional touch filtering

---

## Usage Guide

### For Children

1. **Start Learning**: Tap "Alphabet" book from main menu
2. **Explore Letters**: On main page, tap letters to hear them
3. **Toggle Modes**: Switch between "ABC" and "Sound" at top right
4. **Learn Keyboards**: Go to "Keyboards" page to try different layouts
5. **Play Game**: Go to "Game" page for letter recognition challenge

### For Parents/Teachers

1. **Generate Audio**: Run the audio generation script before first use
2. **Monitor Progress**: Game shows progress and wrong tap counter
3. **Error Mode**: Automatically activates to prevent frustration
4. **Dvorak Layout**: Introduce alternative keyboard for efficiency

---

## Future Enhancements

Potential future features for the Alphabet section:

- [ ] Expand game to all 26 letters (currently A-J)
- [ ] Add uppercase/lowercase toggle
- [ ] Word association mode (e.g., A → Apple)
- [ ] Difficulty levels (slower/faster pop-ups)
- [ ] Sticker rewards for completing game
- [ ] Keyboard typing practice mode
- [ ] Letter tracing practice
- [ ] Multiplayer letter racing game

---

## Troubleshooting

### Audio Not Playing

1. Check that audio files exist in `public/assets/audio/alphabet/`
2. Verify Eleven Labs API key in `.env`
3. Try regenerating audio with `--skip-existing` flag

### Game Too Fast/Slow

Adjust `POP_INTERVAL` in `LetterGame.jsx`:
- Lower value = faster pop-ups
- Higher value = slower pop-ups

### Letters Not Visible on Mobile

Check responsive breakpoints:
- Letters use `clamp()` for responsive sizing
- Grid adjusts to screen size
- Ensure minimum viewport width (320px)

---

## Credits

- **Voice**: Mark (Eleven Labs)
- **Audio Generation**: Eleven Labs TTS with phoneme tags
- **Sound Effects**: Web Audio API (synthesized)
- **UI/UX**: Based on existing animal section design

---

## Related Documentation

- `TECHNICAL_DOCUMENTATION.md` - Overall app architecture
- `src/App.jsx` - Main app routing
- `src/contexts/AudioContext.jsx` - Audio system
- `src/contexts/AccessibilityContext.jsx` - Intentional touch filtering
