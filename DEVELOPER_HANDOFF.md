# Liora Animal Learning App - Developer Handoff Documentation

## 🎯 Project Overview

**Liora Animal Learning App** is an interactive, educational web application designed for children ages 3-8. It's a LeapFrog-style learning platform that teaches kids about animals, American Sign Language (ASL), and world places through engaging visuals, audio, and interactive card-based UI.

### Core Features
- **500+ Animals** across 15+ habitat categories (Marine, Terrestrial, Freshwater, Specialized)
- **62 ASL Signs** organized by theme (Basics, Family, Food, Animals, etc.)
- **35 World Places** organized by continent (Africa, Asia, Europe, Americas, etc.)
- **Audio Learning**: Pre-generated MP3 files with natural voice narration
- **Text-to-Speech Fallback**: Browser-based TTS when audio files are missing
- **Interactive Cards**: Click to flip, press-and-hold to hear facts
- **Page Flip Animation**: LeapFrog-style page turning with smooth transitions
- **Offline-Ready**: PWA-capable for iPad installation

---

## 🏗️ Technology Stack

### Frontend
- **Framework**: React 18 (Vite build system)
- **Styling**: Tailwind CSS 3.x
- **Language**: JavaScript (ES6+)
- **State Management**: React Hooks (useState, useRef, useMemo, useCallback)
- **Audio**: HTML5 Audio API + Web Speech API (TTS fallback)
- **Routing**: React state-based navigation (no router library)

### Backend/Build Tools
- **Build Tool**: Vite (fast HMR, optimized production builds)
- **Package Manager**: npm
- **Environment Variables**: dotenv for API keys

### Content Generation (Python Scripts)
- **Language**: Python 3.8+
- **Audio Generation**: ElevenLabs API (natural voice synthesis)
- **Script Generation**: OpenAI GPT-4o-mini (fact generation)
- **Image Generation**: 
  - DALL-E 3 (OpenAI) - for high-quality educational illustrations
  - Stability AI (fallback) - Stable Diffusion XL
  - Google Imagen (planned) - "Nano Banana" model
- **Data Processing**: JSON-based data structures

### APIs Used
1. **ElevenLabs** - Voice synthesis for audio generation
2. **OpenAI** - GPT for fact generation, DALL-E 3 for images
3. **Google Gemini** - Fact enhancement (optional)
4. **Stability AI** - Image generation (fallback)
5. **Google Imagen** - Image generation (planned integration)

---

## 📁 Project Structure

```
animal-learning/
├── public/
│   ├── assets/
│   │   ├── audio/
│   │   │   ├── animals/          # Animal audio files (simple & detailed)
│   │   │   ├── asl/              # ASL word pronunciations
│   │   │   └── places/           # Place name pronunciations
│   │   └── images/
│   │       ├── animals/          # Animal images (by category)
│   │       ├── asl/              # ASL hand sign images (by category)
│   │       └── places/           # Place images (by continent)
│   └── manifest.json             # PWA manifest
│
├── src/
│   ├── components/
│   │   ├── MainMenu.jsx          # Landing page with book selection
│   │   ├── HabitatBook.jsx       # Animals book (main feature)
│   │   ├── AnimalCard.jsx        # Individual animal card component
│   │   ├── ASLBook.jsx           # ASL signs book
│   │   └── PlacesBook.jsx        # World places book
│   │
│   ├── data/
│   │   ├── animals_fixed.json    # 500+ animals with facts
│   │   ├── simple_scripts.json   # Short audio scripts for animals
│   │   ├── asl_words.json        # 62 ASL signs with categories
│   │   └── places.json           # 35 places with facts
│   │
│   ├── App.jsx                   # Main app component with routing
│   ├── main.jsx                  # React entry point
│   └── index.css                 # Global styles + Tailwind imports
│
├── scripts/
│   ├── generate_natural_audio_simple.py     # Generate animal audio
│   ├── generate_natural_audio_clean.py      # Clean audio generation
│   ├── generate_images.py                   # Generate animal images
│   ├── generate_asl_gemini.py               # Generate ASL images (Gemini)
│   ├── generate_dalle_images.py             # Generate images (DALL-E)
│   ├── generate_placeholders.py             # Generate placeholder images
│   ├── test_dalle_asl.py                    # Test DALL-E ASL generation
│   ├── test_imagen_asl.py                   # Test Google Imagen
│   ├── convert_animals_md.py                # Convert markdown to JSON
│   └── update_facts_hardcoded.py            # Hardcode facts into JSON
│
├── .env                          # Environment variables (API keys)
├── package.json                  # npm dependencies
├── vite.config.js                # Vite configuration
├── tailwind.config.js            # Tailwind CSS configuration
└── README.md                     # Project documentation
```

---

## 🎨 UI/UX Design

### Design Philosophy
- **LeapFrog-Inspired**: Colorful, chunky buttons, large touch targets
- **Kid-Friendly**: High contrast, simple navigation, emoji icons
- **Educational**: Clear labels, audio feedback, visual learning
- **Accessible**: Large text, TTS support, forgiving interactions

### Color Scheme (by Category)
- **Marine**: Blue gradients (#3B82F6 → #1E40AF)
- **Terrestrial**: Green gradients (#10B981 → #047857)
- **Freshwater**: Cyan gradients (#06B6D4 → #0E7490)
- **Specialized**: Purple gradients (#8B5CF6 → #6D28D9)
- **ASL Categories**: Pastel colors (purple, pink, orange, green, yellow, blue)
- **Places (Continents)**: Earth tones and vibrant colors

### Layout Structure
1. **Main Menu** - Three large book buttons (Animals, ASL, Places)
2. **Book View** - Left sidebar (categories), main content area (cards), page tabs
3. **Card Grid** - 12 cards per page, 3 columns × 4 rows
4. **Page Navigation** - Numbered tabs at bottom, click to flip pages
5. **Back Button** - Top-left corner, returns to main menu

### Animations
- **Page Flip**: 3D transform with perspective, 600ms duration
- **Card Flip**: 180° rotation on Y-axis, 400ms duration
- **Hover Effects**: Scale 1.05, shadow increase, smooth transitions
- **Active States**: Pulsing animation, color shifts

---

## 🔧 How It Works

### Application Flow

1. **App Initialization** (`App.jsx`)
   - Load animals, ASL, and places data from JSON files
   - Set up state management for current view (menu, animals, asl, places)
   - Render MainMenu component by default

2. **Main Menu** (`MainMenu.jsx`)
   - Display three book selection buttons
   - Each button triggers navigation to respective book
   - Smooth fade-in animation on load

3. **Book Views** (HabitatBook, ASLBook, PlacesBook)
   - **Data Loading**: Import JSON data, organize by category/continent
   - **Pagination**: Chunk items into pages of 12
   - **Category Selection**: Left sidebar with clickable category buttons
   - **Page Navigation**: Bottom tabs for page flipping
   - **Card Rendering**: Grid of 12 cards per page

4. **Card Interaction** (AnimalCard, WordCard, PlaceCard)
   - **Click**: Flip card to show back (fact/definition)
   - **Press & Hold**: Play audio (fact narration)
   - **TTS Fallback**: If audio file missing, use Web Speech API
   - **Visual Feedback**: Active state during audio playback

### Data Flow

```
JSON Files (src/data/)
    ↓
Component Import
    ↓
useMemo Processing (categorization, pagination)
    ↓
State Management (useState)
    ↓
Render Cards (map over data)
    ↓
User Interaction (click, hold)
    ↓
Audio Playback / TTS
```

### Audio System

**Primary**: Pre-generated MP3 files
- Located in `public/assets/audio/`
- Generated via ElevenLabs API (Python scripts)
- Natural voice, kid-friendly tone
- Two versions: simple (short) and detailed (long)

**Fallback**: Web Speech API (Browser TTS)
- Activated when audio file is missing
- Uses `window.speechSynthesis.speak()`
- Reads fact text directly from JSON data
- No network required, works offline

### Image System

**Current**: Placeholder images (color-coded)
- Generated via `generate_placeholders.py`
- Solid color backgrounds matching category themes
- Text labels for identification

**Planned**: AI-generated educational illustrations
- DALL-E 3 for high-quality, realistic images
- Google Imagen for alternative style
- Stability AI as fallback
- 1024×1024 resolution, PNG format

---

## 🔑 Environment Variables

Required API keys in `.env`:

```bash
# ElevenLabs API for audio generation
ELEVENLABS_API_KEY=sk_xxxxx
ELEVENLABS_VOICE_ID=fjnwTZkKtQOJaYzGLa6n
ELEVENLABS_MODEL=eleven_v3

# OpenAI API for Script Generation & Image Generation
OPENAI_API_KEY=sk-proj-xxxxx

# Google Gemini API for fact generation/enhancement
GOOGLE_GEMINI_API_KEY=AIzaSyxxxxx

# Google Imagen API for image generation (Nano Banana)
GOOGLE_IMAGEN_API_KEY=AQ.Ab8RN6Jxxxxx

# Stability AI for image generation
STABILITY_API_KEY=sk-xxxxx
STABILITY_MODEL=stable-diffusion-xl-1024-v1-0
```

---

## 🚀 Setup & Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+ (for content generation scripts)
- Valid API keys (ElevenLabs, OpenAI, etc.)

### Installation Steps

1. **Install Node dependencies**
   ```bash
   npm install
   ```

2. **Install Python dependencies**
   ```bash
   pip install openai elevenlabs requests python-dotenv pillow
   ```

3. **Configure environment variables**
   - Edit `.env` and add your API keys

4. **Run development server**
   ```bash
   npm run dev
   ```

5. **Build for production**
   ```bash
   npm run build
   npm run preview
   ```

---

## 📊 Data Structure

### Animals (`animals_fixed.json`)
```json
[
  {
    "id": "clownfish",
    "name": "Clownfish",
    "category": "marine",
    "habitat": "coral_reefs",
    "fact": "Clownfish live in sea anemones and are immune to their stings!"
  }
]
```

### ASL Words (`asl_words.json`)
```json
{
  "categories": [
    {
      "id": "basics",
      "name": "Basics & Manners",
      "emoji": "👋",
      "color": "#9333EA",
      "words": ["hello", "please", "thank you"]
    }
  ]
}
```

### Places (`places.json`)
```json
{
  "continents": [
    {
      "id": "africa",
      "name": "Africa",
      "emoji": "🦁",
      "color": "#D97706",
      "places": [
        {
          "name": "Sahara Desert",
          "type": "habitat",
          "fact": "The Sahara is the largest hot desert in the world!"
        }
      ]
    }
  ]
}
```

---

## 🎯 Key Components

### 1. App.jsx
**Purpose**: Main application container with routing logic

**State Management**:
- `currentView`: Controls which book is displayed (menu, animals, asl, places)
- Navigation functions: `showAnimals()`, `showASL()`, `showPlaces()`, `showMenu()`

### 2. MainMenu.jsx
**Purpose**: Landing page with three book selection buttons

**Features**:
- Large, colorful buttons with emojis
- Hover animations (scale, shadow)
- Gradient backgrounds matching book themes

### 3. HabitatBook.jsx (Animals)
**Purpose**: Main book for browsing 500+ animals by habitat

**Features**:
- 15+ habitat categories
- 12 animals per page
- Page flip animation
- Category filtering
- Audio playback on press-and-hold

**Key Logic**:
```javascript
// Organize animals by category
const animalsByCategory = useMemo(() => {
  return animals.reduce((acc, animal) => {
    if (!acc[animal.category]) acc[animal.category] = [];
    acc[animal.category].push(animal);
    return acc;
  }, {});
}, [animals]);

// Chunk into pages of 12
const pages = useMemo(() => {
  const items = animalsByCategory[selectedCategory] || [];
  const chunks = [];
  for (let i = 0; i < items.length; i += 12) {
    chunks.push(items.slice(i, i + 12));
  }
  return chunks;
}, [animalsByCategory, selectedCategory]);
```

### 4. AnimalCard.jsx
**Purpose**: Individual animal card with flip and audio

**Interactions**:
- **Click**: Flip to show fact
- **Press & Hold (500ms)**: Play audio
- **Movement Tolerance**: 30px (forgiving for kids)

**Audio Logic**:
```javascript
const handlePointerDown = (e) => {
  startPos.current = { x: e.clientX, y: e.clientY };
  startTime.current = Date.now();
  
  longPressTimer.current = setTimeout(() => {
    const audioPath = `/assets/audio/animals/${animal.id}_simple.mp3`;
    const audio = new Audio(audioPath);
    
    audio.play().catch(() => {
      // Fallback to TTS
      const utterance = new SpeechSynthesisUtterance(animal.fact);
      window.speechSynthesis.speak(utterance);
    });
  }, 500);
};
```

### 5. ASLBook.jsx
**Purpose**: Browse 62 ASL signs by category

**Features**:
- 7 themed categories (Basics, Family, Food, etc.)
- Pastel color-coded backgrounds
- TTS on click (speaks the word)
- 12 words per page

**TTS Implementation**:
```javascript
const speakWord = (word) => {
  const utterance = new SpeechSynthesisUtterance(word);
  utterance.rate = 0.8; // Slower for clarity
  window.speechSynthesis.speak(utterance);
};
```

### 6. PlacesBook.jsx
**Purpose**: Explore 35 world places by continent

**Features**:
- 6 continents (Africa, Asia, Europe, Americas, Oceania, Antarctica)
- Flip cards to reveal facts
- TTS on flip (speaks the fact)
- 12 places per page

---

## 🐍 Python Scripts

### generate_natural_audio_simple.py
**Purpose**: Generate MP3 audio files for all animals

**Process**:
1. Load `animals_fixed.json` and `simple_scripts.json`
2. For each animal, generate two scripts:
   - **Simple**: "I'm a [animal]. [One fun fact]"
   - **Detailed**: Longer educational narration
3. Send scripts to ElevenLabs API
4. Save MP3 files to `public/assets/audio/animals/`

**Usage**:
```bash
python scripts/generate_natural_audio_simple.py
```

### generate_images.py
**Purpose**: Generate animal images using AI

**Supported APIs**:
- DALL-E 3 (OpenAI)
- Stable Diffusion XL (Stability AI)

**Process**:
1. Load animals from JSON
2. Generate educational illustration prompts
3. Call image generation API
4. Save images to `public/assets/images/animals/[category]/`

**Usage**:
```bash
python scripts/generate_images.py
```

### generate_placeholders.py
**Purpose**: Create color-coded placeholder images

**Process**:
1. Load ASL and Places data
2. Generate solid color images with text labels
3. Use category/continent theme colors
4. Save to respective image directories

**Usage**:
```bash
python scripts/generate_placeholders.py
```

### test_dalle_asl.py
**Purpose**: Test DALL-E 3 for generating ASL hand sign images

**Process**:
1. Select 5 common ASL signs (hello, thank you, love, please, yes)
2. Generate detailed prompts for hand photography
3. Call DALL-E 3 API
4. Save test images to `public/assets/images/asl/test_samples/`

**Usage**:
```bash
python scripts/test_dalle_asl.py
```

---

## 🔍 Current Status

### ✅ Completed
- React app structure with 3 books (Animals, ASL, Places)
- Main menu navigation
- Page flip animations
- Card flip interactions
- Press-and-hold audio playback
- TTS fallback system
- Placeholder images for all content
- Data structures (JSON files)
- Python scripts for content generation

### ⚠️ In Progress
- **Image Generation**: Need valid OpenAI API key for DALL-E 3
- **Audio Generation**: ElevenLabs key working, generating audio files
- **Google Imagen Integration**: Testing alternative image API

### 📋 TODO
1. **Fix OpenAI API Key**: Current key is invalid/expired
   - Get new key from https://platform.openai.com/api-keys
   - Update `.env` file
   - Run `python scripts/test_dalle_asl.py` to test

2. **Generate ASL Images**: Once API key is valid
   - Run test generation (5 samples)
   - If successful, generate all 62 ASL signs
   - Replace placeholder images

3. **Generate Places Images**: Similar process
   - Generate all 35 place images
   - Use educational, kid-friendly style

4. **Audio Completion**: Continue generating animal audio
   - Simple scripts for all 500+ animals
   - Detailed scripts for featured animals

5. **PWA Setup**: Make app installable on iPad
   - Configure `manifest.json`
   - Add service worker for offline support
   - Test installation flow

6. **Performance Optimization**:
   - Lazy load images
   - Preload audio for current page
   - Optimize bundle size

---

## 🎓 Educational Design Principles

### Age-Appropriate Content (3-8 years)
- **Simple Language**: Short sentences, common words
- **Concrete Facts**: Avoid abstract concepts
- **Memorable Details**: Focus on surprising, fun facts
- **Visual Learning**: Images + audio + text
- **Repetition**: Consistent UI patterns

### Interaction Design
- **Large Touch Targets**: Minimum 80px buttons
- **Forgiving Gestures**: 30px movement tolerance
- **Immediate Feedback**: Visual + audio confirmation
- **Error Prevention**: No destructive actions
- **Progress Indicators**: Page numbers, category highlights

### Accessibility
- **High Contrast**: WCAG AA compliant colors
- **TTS Support**: All text can be spoken
- **Keyboard Navigation**: Tab through cards
- **Screen Reader**: Semantic HTML, ARIA labels
- **No Time Limits**: Kids can explore at their own pace

---

## 🚨 Known Issues

### 1. OpenAI API Key Invalid
**Issue**: Current key in `.env` is rejected by OpenAI (401 error)

**Solution**: Generate new key at https://platform.openai.com/api-keys

### 2. Google Imagen API Endpoint Unknown
**Issue**: Provided key format doesn't match standard Google APIs

**Solution**: User needs to verify correct endpoint and authentication method

### 3. Placeholder Images
**Issue**: Current images are solid colors with text labels

**Solution**: Generate real images once API keys are valid

---

## 📞 Support & Resources

### Documentation
- React: https://react.dev
- Vite: https://vitejs.dev
- Tailwind CSS: https://tailwindcss.com
- ElevenLabs API: https://elevenlabs.io/docs
- OpenAI API: https://platform.openai.com/docs

### API Key Management
- OpenAI: https://platform.openai.com/api-keys
- ElevenLabs: https://elevenlabs.io/app/settings/api-keys
- Stability AI: https://platform.stability.ai/account/keys

### Deployment Options
- Vercel (recommended for Vite apps)
- Netlify
- GitHub Pages
- AWS S3 + CloudFront

---

## 🎉 Summary

This is a **React + Vite + Tailwind CSS** educational app with:
- **3 interactive books** (Animals, ASL, Places)
- **600+ content items** (500 animals, 62 ASL signs, 35 places)
- **AI-generated content** (audio via ElevenLabs, images via DALL-E/Imagen)
- **LeapFrog-style UI** (colorful, animated, kid-friendly)
- **Offline-capable** (TTS fallback, PWA-ready)

**Next Steps**: Fix OpenAI API key → Generate images → Complete audio → Deploy

**Estimated Time to Production**: 2-3 days (assuming valid API keys)
