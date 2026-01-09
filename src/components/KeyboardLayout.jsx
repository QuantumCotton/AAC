import React, { useState, useEffect, useRef } from 'react';
import { useAudio } from '../contexts/AudioContext';
import { ALPHABET, VOWELS } from './AlphabetBook';

// Keyboard layouts
const LAYOUTS = {
  qwerty: [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
  ],
  dvorak: [
    ['"', ',', '.', 'P', 'Y', 'F', 'G', 'C', 'R', 'L', '/'],
    ['A', 'O', 'E', 'U', 'I', 'D', 'H', 'T', 'N', 'S'],
    [';', 'Q', 'J', 'K', 'X', 'B', 'M', 'W', 'V', 'Z']
  ],
  vowels: [['A', 'E', 'I', 'O', 'U']]
};

const LAYOUT_COLORS = {
  qwerty: '#3b82f6',
  dvorak: '#8b5cf6',
  vowels: '#f97316'
};

export default function KeyboardLayout({ mode }) {
  const { playSound } = useAudio();
  const secondAudioRef = useRef(null);
  const [selectedLayout, setSelectedLayout] = useState('qwerty'); // 'qwerty' | 'dvorak' | 'vowels'
  
  const getSoundPath = (letter) => {
    const letterLower = letter.toLowerCase();
    
    // In name mode, play letter name
    if (mode === 'name') {
      return `/assets/audio/alphabet/letter_${letterLower}_name.mp3`;
    }
    
    // For consonants, use regular sound
    if (!VOWELS.includes(letter)) {
      return `/assets/audio/alphabet/letter_${letterLower}_sound.mp3`;
    }
    
    // For vowels in sound mode, return short sound path (will play long after)
    return `/assets/audio/alphabet/letter_${letterLower}_sound_short.mp3`;
  };
  
  const handleLetterPress = (letter) => {
    const soundPath = getSoundPath(letter);
    
    // Stop any currently playing second audio
    if (secondAudioRef.current) {
      secondAudioRef.current.pause();
      secondAudioRef.current = null;
    }
    
    // Play first sound
    playSound(soundPath, letter);
    
    // For vowels in sound mode, play long sound after short sound
    if (mode === 'sound' && VOWELS.includes(letter)) {
      const letterLower = letter.toLowerCase();
      const longSoundPath = `/assets/audio/alphabet/letter_${letterLower}_sound_long.mp3`;
      
      // Create audio element for long sound
      const longAudio = new Audio(longSoundPath);
      secondAudioRef.current = longAudio;
      
      // Get duration of short sound and schedule long sound
      const shortAudio = new Audio(soundPath);
      shortAudio.addEventListener('loadedmetadata', () => {
        const shortDuration = shortAudio.duration * 1000; // Convert to ms
        
        setTimeout(() => {
          if (secondAudioRef.current === longAudio) {
            longAudio.play().catch(console.error);
          }
        }, shortDuration + 100); // Add small buffer
      });
      
      shortAudio.addEventListener('error', () => {
        // If short audio fails, just play long sound after short delay
        setTimeout(() => {
          if (secondAudioRef.current === longAudio) {
            longAudio.play().catch(console.error);
          }
        }, 500);
      });
    }
  };

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (secondAudioRef.current) {
        secondAudioRef.current.pause();
      }
    };
  }, []);
  
  const layoutButtons = [
    { id: 'qwerty', label: 'QWERTY' },
    { id: 'dvorak', label: 'Dvorak' },
    { id: 'vowels', label: 'Vowels' }
  ];
  
  const getLayoutTitle = () => {
    const titles = {
      qwerty: 'QWERTY Keyboard',
      dvorak: 'Dvorak Keyboard',
      vowels: 'Vowels Only'
    };
    return titles[selectedLayout];
  };

  return (
    <div className="flex flex-col h-full">
      {/* Layout selector */}
      <div className="flex justify-center gap-3 mb-6">
        {layoutButtons.map((btn) => (
          <button
            key={btn.id}
            onClick={() => setSelectedLayout(btn.id)}
            className={`px-4 py-2 rounded-full text-sm font-bold shadow transition-all ${
              selectedLayout === btn.id
                ? `scale-110 ${btn.id === 'qwerty' ? 'bg-blue-500' : btn.id === 'dvorak' ? 'bg-purple-500' : 'bg-green-500'} text-white`
                : 'bg-white/70 text-gray-700 hover:scale-105'
            }`}
          >
            {btn.label}
          </button>
        ))}
      </div>

      {/* Keyboard layout title */}
      <h2 className="text-center text-2xl font-bold text-white mb-4 drop-shadow-lg">
        {getLayoutTitle()}
      </h2>

      {/* Keyboard grid */}
      <div className="flex-1 flex items-center justify-center">
        <div className="w-full max-w-5xl">
          {LAYOUTS[selectedLayout].map((row, rowIndex) => (
            <div 
              key={rowIndex} 
              className="flex justify-center gap-2 mb-2"
              style={{
                marginLeft: rowIndex === 2 ? 'auto' : '0',
                marginRight: rowIndex === 0 ? 'auto' : '0',
              }}
            >
              {row.map((letter) => {
                const isVowel = VOWELS.includes(letter);
                return (
                  <button
                    key={letter}
                    onClick={() => handleLetterPress(letter)}
                    className="aspect-square rounded-xl shadow-lg 
                      transition-all duration-150
                      hover:scale-105 hover:shadow-xl
                      active:scale-95 active:shadow-sm
                      font-black select-none
                      touch-manipulation-none
                      relative"
                    style={{
                      width: 'clamp(3rem, 8vw, 5rem)',
                      height: 'clamp(3rem, 8vw, 5rem)',
                      background: `linear-gradient(135deg, ${LAYOUT_COLORS[selectedLayout]} 0%, ${LAYOUT_COLORS[selectedLayout]}dd 100%)`,
                      boxShadow: `0 6px 0 ${LAYOUT_COLORS[selectedLayout]}66`,
                    }}
                  >
                    <span 
                      className="text-3xl sm:text-4xl md:text-5xl relative"
                      style={{ 
                        color: 'white',
                        textShadow: '2px 2px 4px rgba(0,0,0,0.2)'
                      }}
                    >
                      {letter}
                      {isVowel && mode === 'sound' && (
                        <span className="absolute -top-1 -right-1 text-xs bg-yellow-400 text-yellow-900 rounded-full px-1">
                          🔊
                        </span>
                      )}
                    </span>
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
