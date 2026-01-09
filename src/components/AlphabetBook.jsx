import React, { useState, useCallback } from 'react';
import { useAudio } from '../contexts/AudioContext';
import { useTheme } from '../contexts/ThemeContext';

// Import page components
import AlphabetGrid from './AlphabetGrid';
import KeyboardLayout from './KeyboardLayout';
import LetterGame from './LetterGame';

const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
const ALPHABET_COLORS = [
  '#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', 
  '#3b82f6', '#8b5cf6', '#ec4899', '#ef4444', '#f97316',
  '#eab308', '#22c55e', '#06b6d4', '#3b82f6', '#8b5cf6',
  '#ec4899', '#ef4444', '#f97316', '#eab308', '#22c55e',
  '#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899'
];

// Vowels that have long and short sounds
const VOWELS = ['A', 'E', 'I', 'O', 'U'];

export default function AlphabetBook({ onBack }) {
  const { playClick } = useAudio();
  const { isToyTheme } = useTheme();
  
  const [currentPage, setCurrentPage] = useState(0); // 0: Alphabet, 1: Keyboards, 2: Game
  const [mode, setMode] = useState('name'); // 'name' or 'sound'
  
  const pages = [
    { id: 0, title: '🔤 Alphabet', component: AlphabetGrid },
    { id: 1, title: '⌨️ Keyboards', component: KeyboardLayout },
    { id: 2, title: '🎮 Game', component: LetterGame },
  ];
  
  const PageComponent = pages[currentPage].component;
  
  const toggleMode = useCallback(() => {
    setMode(prev => prev === 'name' ? 'sound' : 'name');
    playClick();
  }, [playClick]);
  
  const goToPage = useCallback((pageIndex) => {
    if (pageIndex !== currentPage) {
      setCurrentPage(pageIndex);
      playClick();
    }
  }, [currentPage, playClick]);
  
  const getModeLabel = () => {
    return mode === 'name' ? 'ABC' : 'Sound';
  };

  return (
    <div className="fixed inset-0 flex flex-col overflow-hidden" 
         style={{ background: 'linear-gradient(135deg, #fbbf24 0%, #60a5fa 50%, #a78bfa 100%)' }}>
      
      {/* Top bar with controls */}
      <div className="flex items-center justify-between px-4 py-2 bg-black/20 shrink-0">
        <button
          onClick={onBack}
          className="p-2 rounded-full bg-white/90 shadow-lg hover:bg-white transition-colors"
        >
          <span className="text-xl">🏠</span>
        </button>
        
        <h1 className="text-xl font-black text-white drop-shadow-lg">
          📚 Alphabet Book 📚
        </h1>
        
        {/* Mode toggle (ABC / Sound) - only on page 0 */}
        {currentPage === 0 && (
          <button
            onClick={toggleMode}
            className={`px-4 py-2 rounded-full text-sm font-bold shadow transition-all ${
              mode === 'name' 
                ? 'bg-purple-500 text-white' 
                : 'bg-green-500 text-white'
            }`}
            title={mode === 'name' ? 'Letter Names' : 'Phonetic Sounds'}
          >
            {getModeLabel()}
          </button>
        )}
      </div>

      {/* Page navigation tabs */}
      <div className="flex justify-center gap-2 px-4 py-2 bg-black/10 shrink-0">
        {pages.map((page, index) => (
          <button
            key={page.id}
            onClick={() => goToPage(index)}
            className={`px-3 py-1 rounded-full text-sm font-bold shadow transition-all ${
              currentPage === index
                ? 'bg-yellow-400 text-yellow-900 scale-110'
                : 'bg-white/70 text-gray-700 hover:scale-105'
            }`}
          >
            {page.title}
          </button>
        ))}
      </div>

      {/* Main content area */}
      <div className="flex-1 flex items-center justify-center p-4 overflow-hidden">
        <div className="w-full h-full max-w-6xl mx-auto">
          <PageComponent mode={mode} alphabetColors={ALPHABET_COLORS} />
        </div>
      </div>
    </div>
  );
}

// Export for use in other components
export { ALPHABET, ALPHABET_COLORS, VOWELS };
