import React, { useEffect, useRef } from 'react';
import { useAudio } from '../contexts/AudioContext';
import { ALPHABET, ALPHABET_COLORS, VOWELS } from './AlphabetBook';

export default function AlphabetGrid({ mode, alphabetColors }) {
  const { playSound } = useAudio();
  const audioRef = useRef(null);
  const secondAudioRef = useRef(null);
  const isPlayingRef = useRef(false);

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
  
  const handleLetterPress = (letter, index) => {
    const color = alphabetColors[index];
    const soundPath = getSoundPath(letter);
    
    // Stop any currently playing audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
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
      
      // Create audio element for the long sound
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
      if (audioRef.current) {
        audioRef.current.pause();
      }
      if (secondAudioRef.current) {
        secondAudioRef.current.pause();
      }
    };
  }, []);

  return (
    <div className="grid grid-cols-5 sm:grid-cols-6 md:grid-cols-5 gap-2 sm:gap-3 p-4 sm:p-6 w-full h-full overflow-auto">
      {ALPHABET.map((letter, index) => {
        const color = alphabetColors[index];
        const isVowel = VOWELS.includes(letter);
        
        return (
          <button
            key={letter}
            onClick={() => handleLetterPress(letter, index)}
            className={`
              aspect-square rounded-xl sm:rounded-2xl shadow-lg 
              transition-all duration-150
              hover:scale-105 hover:shadow-xl
              active:scale-95 active:shadow-sm
              font-black
              select-none
              touch-manipulation-none
              ${isVowel && mode === 'sound' ? 'ring-2 ring-yellow-300' : ''}
            `}
            style={{
              background: `linear-gradient(135deg, ${color} 0%, ${color}dd 100%)`,
              boxShadow: `0 6px 0 ${color}66`,
              minWidth: 'min(100%, 60px)',
            }}
          >
            <span 
              className="text-4xl sm:text-6xl md:text-7xl lg:text-8xl relative"
              style={{ 
                color: 'white',
                textShadow: '2px 2px 4px rgba(0,0,0,0.2)'
              }}
            >
              {letter}
              {isVowel && mode === 'sound' && (
                <span className="absolute -top-1 -right-1 text-[10px] sm:text-xs bg-yellow-400 text-yellow-900 rounded-full px-1">
                  🔊
                </span>
              )}
            </span>
          </button>
        );
      })}
    </div>
  );
}
