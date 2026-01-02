// Category-specific styling for animal images
export const categoryStyles = {
  'Farm': {
    // Warm, friendly farm colors
    background: {
      primary: '#87CEEB', // Sky blue
      secondary: '#98D982', // Meadow green
      gradient: 'linear-gradient(135deg, #87CEEB 0%, #98D982 100%)'
    },
    pattern: 'subtle-clouds',
    promptSuffix: 'in a sunny farm setting with soft blue sky and green pasture background, gentle morning light',
    toyMode: 'cute cartoon style with rounded features, big friendly eyes',
    realMode: 'photorealistic but soft and warm lighting'
  },
  
  'Domestic': {
    // Cozy home colors
    background: {
      primary: '#FFE5CC', // Warm peach
      secondary: '#E6D3B3', // Soft beige
      gradient: 'linear-gradient(135deg, #FFE5CC 0%, #E6D3B3 100%)'
    },
    pattern: 'subtle-paw-prints',
    promptSuffix: 'in a cozy home environment with warm soft lighting, comfortable background',
    toyMode: 'adorable pet portrait style, extra fluffy and cute',
    realMode: 'high quality pet photography, warm indoor lighting'
  },
  
  'Forest': {
    // Deep forest greens
    background: {
      primary: '#228B22', // Forest green
      secondary: '#90EE90', // Light green
      gradient: 'linear-gradient(135deg, #228B22 0%, #90EE90 100%)'
    },
    pattern: 'subtle-leaves',
    promptSuffix: 'in a lush forest with dappled sunlight filtering through trees, natural woodland setting',
    toyMode: 'friendly forest creature style, surrounded by simplified trees',
    realMode: 'wildlife photography style, natural forest habitat'
  },
  
  'Jungle': {
    // Vibrant tropical colors
    background: {
      primary: '#006400', // Dark green
      secondary: '#FF8C00', // Dark orange
      gradient: 'linear-gradient(135deg, #006400 0%, #228B22 50%, #FF8C00 100%)'
    },
    pattern: 'subtle-tropical-leaves',
    promptSuffix: 'in a vibrant tropical rainforest with exotic plants and colorful flowers, humid atmosphere',
    toyMode: 'playful jungle adventure style, bright and colorful',
    realMode: 'National Geographic style, rich tropical colors'
  },
  
  'Nocturnal': {
    // Night sky colors
    background: {
      primary: '#191970', // Midnight blue
      secondary: '#4B0082', // Indigo
      gradient: 'linear-gradient(135deg, #191970 0%, #4B0082 100%)'
    },
    pattern: 'subtle-stars',
    promptSuffix: 'under a starry night sky with moonlight, magical nighttime atmosphere',
    toyMode: 'cute night creature style with glowing elements',
    realMode: 'night wildlife photography with natural moonlight'
  },
  
  'Arctic': {
    // Cool ice colors
    background: {
      primary: '#E0FFFF', // Light cyan
      secondary: '#B0E0E6', // Powder blue
      gradient: 'linear-gradient(135deg, #E0FFFF 0%, #B0E0E6 50%, #F0F8FF 100%)'
    },
    pattern: 'subtle-snowflakes',
    promptSuffix: 'in arctic snow and ice landscapes with soft blue-white lighting, crisp cold air',
    toyMode: 'cute arctic friend style with soft rounded ice shapes',
    realMode: 'arctic wildlife photography with pristine snow'
  },
  
  'Shallow Water': {
    // Beach/ocean colors
    background: {
      primary: '#00CED1', // Dark turquoise
      secondary: '#87CEEB', // Sky blue
      gradient: 'linear-gradient(135deg, #00CED1 0%, #87CEEB 100%)'
    },
    pattern: 'subtle-waves',
    promptSuffix: 'in clear shallow tropical water with sandy bottom, sunlight filtering through water',
    toyMode: 'playful sea creature style with bubbly effects',
    realMode: 'underwater photography style, clear tropical water'
  },
  
  'Coral Reef': {
    // Vibrant reef colors
    background: {
      primary: '#FF6B6B', // Coral red
      secondary: '#4ECDC4', // Turquoise
      secondary2: '#FFE66D', // Yellow
      gradient: 'linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 50%, #FFE66D 100%)'
    },
    pattern: 'subtle-coral',
    promptSuffix: 'among colorful coral reefs with tropical fish, crystal clear water',
    toyMode: 'vibrant cartoon reef style with exaggerated colors',
    realMode: 'underwater reef photography with natural coral colors'
  },
  
  'Deep Sea': {
    // Mysterious deep ocean colors
    background: {
      primary: '#000080', // Navy
      secondary: '#191970', // Midnight blue
      gradient: 'linear-gradient(135deg, #000080 0%, #191970 50%, #000033 100%)'
    },
    pattern: 'subtle-bioluminescent',
    promptSuffix: 'in deep dark ocean with bioluminescent light effects, mysterious deep sea atmosphere',
    toyMode: 'glowing deep sea creature style with light effects',
    realMode: 'deep sea documentary style with natural bioluminescence'
  },
  
  'Ultra Deep Sea': {
    // Abyssal zone colors
    background: {
      primary: '#000033', // Very dark blue
      secondary: '#000000', // Black
      gradient: 'linear-gradient(135deg, #000033 0%, #000000 100%)'
    },
    pattern: 'subtle-abyssal',
    promptSuffix: 'in the abyssal depths with minimal light, pressure-adapted environment',
    toyMode: 'mysterious abyss creature with subtle glowing features',
    realMode: 'deep sea ROV camera style, true deep sea conditions'
  }
};

// Generate AI prompt for animal image
export function generateImagePrompt(animal, isToyMode = true) {
  const category = animal.category;
  const style = categoryStyles[category] || categoryStyles['Forest'];
  
  const basePrompt = `Realistic ${animal.name}, friendly expression, educational illustration style`;
  const modeStyle = isToyMode ? style.toyMode : style.realMode;
  const background = style.promptSuffix;
  
  return `${basePrompt}, ${modeStyle}, ${background}, centered composition, high detail, vibrant colors, children's book illustration quality, Pixar-inspired rendering, no text, white background isolated`;
}

// Get background style for CSS
export function getBackgroundStyle(category, isToyMode = true) {
  const style = categoryStyles[category] || categoryStyles['Forest'];
  
  return {
    background: style.background.gradient,
    position: 'relative',
    overflow: 'hidden'
  };
}

// Pattern definitions (can be used as CSS or SVG overlays)
export const patterns = {
  'subtle-clouds': {
    type: 'clouds',
    opacity: 0.1,
    color: '#FFFFFF'
  },
  'subtle-paw-prints': {
    type: 'paws',
    opacity: 0.1,
    color: '#8B7355'
  },
  'subtle-leaves': {
    type: 'leaves',
    opacity: 0.1,
    color: '#90EE90'
  },
  'subtle-tropical-leaves': {
    type: 'tropical',
    opacity: 0.1,
    color: '#228B22'
  },
  'subtle-stars': {
    type: 'stars',
    opacity: 0.3,
    color: '#FFFF00'
  },
  'subtle-snowflakes': {
    type: 'snowflakes',
    opacity: 0.2,
    color: '#FFFFFF'
  },
  'subtle-waves': {
    type: 'waves',
    opacity: 0.1,
    color: '#FFFFFF'
  },
  'subtle-coral': {
    type: 'coral',
    opacity: 0.1,
    color: '#FF6B6B'
  },
  'subtle-bioluminescent': {
    type: 'glow',
    opacity: 0.2,
    color: '#00FFFF'
  },
  'subtle-abyssal': {
    type: 'depth',
    opacity: 0.1,
    color: '#000080'
  }
};

export default {
  categoryStyles,
  generateImagePrompt,
  getBackgroundStyle,
  patterns
};
