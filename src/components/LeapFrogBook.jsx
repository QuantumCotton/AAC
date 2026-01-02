import React, { useState, useMemo, useCallback, useRef } from 'react';
import loadAnimalsWithFacts from '../data/loadAnimals';
import AnimalCard from './AnimalCard';
import { useAudio } from '../contexts/AudioContext';
import { useTheme } from '../contexts/ThemeContext';
import { useFactLevel } from '../contexts/FactLevelContext';
import { habitats } from '../data/habitats';

// Chunk animals into pages of N items
function chunk(arr, size) {
  const out = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}

// Spiral ring colors - bright rainbow like LeapFrog
const SPIRAL_COLORS = [
  '#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', 
  '#3b82f6', '#8b5cf6', '#ec4899', '#ef4444', '#f97316',
  '#eab308', '#22c55e', '#06b6d4', '#3b82f6', '#8b5cf6',
  '#ec4899', '#ef4444', '#f97316', '#eab308', '#22c55e',
];

export default function LeapFrogBook({ onBack }) {
  const { playClick } = useAudio();
  const { isToyTheme, toggleTheme } = useTheme();
  const { isSimpleLevel, toggleFactLevel } = useFactLevel();

  const [currentSpread, setCurrentSpread] = useState(0);
  const [isFlipping, setIsFlipping] = useState(false);
  const [flipDirection, setFlipDirection] = useState(null);

  // Build all pages across all habitats - 9 animals per page (3x3)
  const { allPages, habitatPageRanges } = useMemo(() => {
    const pages = [];
    const ranges = {};
    let pageIndex = 0;

    habitats.forEach((habitat) => {
      const animals = loadAnimalsWithFacts
        .filter((a) => a.category === habitat.name)
        .sort((a, b) => a.name.localeCompare(b.name));

      if (animals.length === 0) return;

      const habitatPages = chunk(animals, 9); // 9 animals per page (3x3 grid)
      ranges[habitat.name] = {
        start: pageIndex,
        end: pageIndex + habitatPages.length - 1,
        habitat,
      };

      habitatPages.forEach((pageAnimals) => {
        pages.push({
          animals: pageAnimals,
          habitat: habitat,
          pageNum: pageIndex,
        });
        pageIndex++;
      });
    });

    return { allPages: pages, habitatPageRanges: ranges };
  }, []);

  // Create spreads (pairs of pages)
  const spreads = useMemo(() => {
    const result = [];
    for (let i = 0; i < allPages.length; i += 2) {
      result.push({
        left: allPages[i] || null,
        right: allPages[i + 1] || null,
      });
    }
    return result;
  }, [allPages]);

  const totalSpreads = spreads.length;

  // Get current habitat based on visible pages
  const currentHabitat = useMemo(() => {
    const spread = spreads[currentSpread];
    if (!spread) return habitats[0];
    return spread.left?.habitat || spread.right?.habitat || habitats[0];
  }, [spreads, currentSpread]);

  // Find which habitats are visible on current spread
  const visibleHabitats = useMemo(() => {
    const spread = spreads[currentSpread];
    if (!spread) return [];
    const visible = new Set();
    if (spread.left) visible.add(spread.left.habitat.name);
    if (spread.right) visible.add(spread.right.habitat.name);
    return Array.from(visible);
  }, [spreads, currentSpread]);

  // Flip to a specific spread with book-like animation
  const flipToSpread = useCallback((targetSpread, direction) => {
    if (isFlipping || targetSpread < 0 || targetSpread >= totalSpreads) return;
    if (targetSpread === currentSpread) return;

    const dir = direction || (targetSpread > currentSpread ? 'left' : 'right');
    setFlipDirection(dir);
    setIsFlipping(true);
    playClick();

    // Longer animation for more dramatic book flip
    setTimeout(() => {
      setCurrentSpread(targetSpread);
      setTimeout(() => {
        setFlipDirection(null);
        setIsFlipping(false);
      }, 300);
    }, 350);
  }, [currentSpread, totalSpreads, isFlipping, playClick]);

  // Navigate to a specific habitat
  const goToHabitat = useCallback((habitatName) => {
    const range = habitatPageRanges[habitatName];
    if (!range) return;
    const targetSpread = Math.floor(range.start / 2);
    flipToSpread(targetSpread, targetSpread > currentSpread ? 'left' : 'right');
  }, [habitatPageRanges, currentSpread, flipToSpread]);

  // Swipe handling
  const touchRef = useRef({ startX: 0, startY: 0 });

  const handleTouchStart = (e) => {
    if (isFlipping) return;
    touchRef.current.startX = e.touches?.[0]?.clientX || e.clientX || 0;
    touchRef.current.startY = e.touches?.[0]?.clientY || e.clientY || 0;
  };

  const handleTouchEnd = (e) => {
    if (isFlipping) return;
    const endX = e.changedTouches?.[0]?.clientX || e.clientX || 0;
    const endY = e.changedTouches?.[0]?.clientY || e.clientY || 0;
    const dx = endX - touchRef.current.startX;
    const dy = endY - touchRef.current.startY;

    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) {
      if (dx < 0 && currentSpread < totalSpreads - 1) {
        flipToSpread(currentSpread + 1, 'left');
      } else if (dx > 0 && currentSpread > 0) {
        flipToSpread(currentSpread - 1, 'right');
      }
    }
  };

  // Get background gradient for a habitat
  const getHabitatGradient = (habitat) => {
    const gradients = {
      'Farm': 'linear-gradient(135deg, #86efac 0%, #fef08a 100%)',
      'Domestic': 'linear-gradient(135deg, #fde68a 0%, #fed7aa 100%)',
      'Forest': 'linear-gradient(135deg, #6ee7b7 0%, #34d399 100%)',
      'Jungle': 'linear-gradient(135deg, #4ade80 0%, #22c55e 100%)',
      'Nocturnal': 'linear-gradient(135deg, #c4b5fd 0%, #a78bfa 100%)',
      'Arctic': 'linear-gradient(135deg, #bae6fd 0%, #7dd3fc 100%)',
      'Shallow Water': 'linear-gradient(135deg, #67e8f9 0%, #22d3ee 100%)',
      'Coral Reef': 'linear-gradient(135deg, #5eead4 0%, #2dd4bf 100%)',
      'Deep Sea': 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
      'Ultra Deep Sea': 'linear-gradient(135deg, #475569 0%, #334155 100%)',
    };
    return gradients[habitat?.name] || 'linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%)';
  };

  // Render a single page - fills the space
  const renderPage = (page, side) => {
    if (!page) {
      return (
        <div className={`flex-1 flex items-center justify-center`}
          style={{ background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)' }}>
          <span className="text-6xl opacity-40">📖</span>
        </div>
      );
    }

    return (
      <div
        className="flex-1 flex flex-col overflow-hidden"
        style={{ background: getHabitatGradient(page.habitat) }}
      >
        {/* Page header - compact */}
        <div className="flex items-center justify-between px-2 py-1 bg-black/10">
          <div className="flex items-center gap-1">
            <span className="text-xl">{page.habitat.emoji}</span>
            <span className="text-xs font-black text-white drop-shadow-md">
              {page.habitat.name}
            </span>
          </div>
          <div className="bg-white/70 rounded-full px-2 py-0.5 text-xs font-bold text-gray-700">
            {page.pageNum + 1}
          </div>
        </div>

        {/* Animal grid - 3x3 fills the page */}
        <div className="flex-1 p-1 overflow-hidden min-h-0">
          <div className="grid grid-cols-3 grid-rows-3 gap-1 h-full">
            {page.animals.map((animal) => (
              <AnimalCard key={animal.id} animal={animal} />
            ))}
          </div>
        </div>
      </div>
    );
  };

  // Render spiral binding - taller to fill the book
  const renderSpiral = () => (
    <div className="w-6 flex flex-col items-center justify-around py-2 bg-gradient-to-b from-amber-200 via-amber-100 to-amber-200 shadow-inner relative z-10">
      {SPIRAL_COLORS.map((color, i) => (
        <div
          key={i}
          className="w-4 h-3 rounded-full"
          style={{
            background: `linear-gradient(180deg, ${color} 0%, ${color}aa 100%)`,
            boxShadow: `0 2px 3px ${color}88, inset 0 1px 1px rgba(255,255,255,0.6)`,
          }}
        />
      ))}
    </div>
  );

  // Get habitat tabs - split into passed (left) and upcoming (right)
  const getHabitatIndex = (habitatName) => habitats.findIndex(h => h.name === habitatName);
  const currentHabitatIndex = getHabitatIndex(currentHabitat.name);

  const passedHabitats = habitats.slice(0, currentHabitatIndex);
  const currentAndUpcoming = habitats.slice(currentHabitatIndex);

  return (
    <div className="fixed inset-0 flex flex-col overflow-hidden" style={{ background: 'linear-gradient(135deg, #0ea5e9 0%, #10b981 50%, #f59e0b 100%)' }}>
      {/* Top bar with controls */}
      <div className="flex items-center justify-between px-2 py-1 bg-black/20 shrink-0">
        <button
          onClick={onBack}
          className="p-1.5 rounded-full bg-white/90 shadow-lg hover:bg-white transition-colors"
        >
          <span className="text-lg">🏠</span>
        </button>
        <h1 className="text-base font-black text-white drop-shadow-lg">
          🐾 Animal Book 🐾
        </h1>
        {/* Theme & Level toggles */}
        <div className="flex items-center gap-1">
          {/* Kids/Education toggle */}
          <button
            onClick={() => { toggleFactLevel(); playClick(); }}
            className={`px-2 py-1 rounded-full text-xs font-bold shadow transition-all ${
              isSimpleLevel 
                ? 'bg-pink-400 text-white' 
                : 'bg-blue-500 text-white'
            }`}
            title={isSimpleLevel ? 'Kids Mode' : 'Education Mode'}
          >
            {isSimpleLevel ? '👶 Kids' : '🎓 Edu'}
          </button>
          {/* Toy/Real toggle */}
          <button
            onClick={() => { toggleTheme(); playClick(); }}
            className={`px-2 py-1 rounded-full text-xs font-bold shadow transition-all ${
              isToyTheme 
                ? 'bg-yellow-400 text-yellow-900' 
                : 'bg-emerald-500 text-white'
            }`}
            title={isToyTheme ? 'Toy Images' : 'Real Images'}
          >
            {isToyTheme ? '🧸' : '📷'}
          </button>
        </div>
      </div>

      {/* Main book area - fills screen */}
      <div className="flex-1 flex items-stretch justify-center p-1 relative overflow-hidden min-h-0">
        {/* Left habitat tabs - stacked like book pages */}
        {passedHabitats.length > 0 && (
          <div className="absolute left-0 top-0 bottom-0 z-30 flex flex-col justify-center gap-0.5 py-4">
            {passedHabitats.slice(-8).map((h, i) => (
              <button
                key={h.name}
                onClick={() => goToHabitat(h.name)}
                disabled={isFlipping}
                className={`flex items-center px-1 py-1 rounded-r-lg text-white font-bold shadow transition-all hover:translate-x-1 ${h.color}`}
                style={{ 
                  opacity: 0.7 + (i * 0.03),
                  transform: `translateX(${-2 + i * 0.5}px)`,
                }}
              >
                <span className="text-sm">{h.emoji}</span>
              </button>
            ))}
          </div>
        )}

        {/* Right habitat tabs */}
        <div className="absolute right-0 top-0 bottom-0 z-30 flex flex-col justify-center gap-0.5 py-4">
          {currentAndUpcoming.slice(0, 8).map((h, i) => {
            const isCurrent = h.name === currentHabitat.name;
            return (
              <button
                key={h.name}
                onClick={() => goToHabitat(h.name)}
                disabled={isFlipping}
                className={`flex items-center px-1 py-1 rounded-l-lg text-white font-bold shadow transition-all hover:-translate-x-1 ${h.color} ${isCurrent ? 'ring-2 ring-yellow-300 z-10' : ''}`}
                style={{ 
                  opacity: isCurrent ? 1 : 0.7 - (i * 0.05),
                  transform: isCurrent ? 'translateX(0) scale(1.1)' : `translateX(${2 - i * 0.5}px)`,
                }}
              >
                <span className="text-sm">{h.emoji}</span>
              </button>
            );
          })}
        </div>

        {/* The Book - fills available space */}
        <div
          className={`book-wrapper flex flex-1 mx-6 rounded-2xl shadow-2xl overflow-hidden border-4 border-amber-400 relative
            ${flipDirection === 'left' ? 'page-flip-left' : ''}
            ${flipDirection === 'right' ? 'page-flip-right' : ''}`}
          style={{ background: '#fef3c7' }}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
          onMouseDown={handleTouchStart}
          onMouseUp={handleTouchEnd}
        >
          {/* Left page */}
          {renderPage(spreads[currentSpread]?.left, 'left')}

          {/* Spiral binding */}
          {renderSpiral()}

          {/* Right page */}
          {renderPage(spreads[currentSpread]?.right, 'right')}

          {/* Page turn overlays - tap areas */}
          {currentSpread > 0 && (
            <div
              onClick={() => flipToSpread(currentSpread - 1, 'right')}
              className="absolute left-0 top-0 bottom-0 w-16 cursor-pointer z-20 flex items-center justify-start pl-1"
            >
              <div className="w-8 h-8 rounded-full bg-white/60 flex items-center justify-center text-lg shadow hover:bg-white/90 transition-all">
                ◀
              </div>
            </div>
          )}
          {currentSpread < totalSpreads - 1 && (
            <div
              onClick={() => flipToSpread(currentSpread + 1, 'left')}
              className="absolute right-0 top-0 bottom-0 w-16 cursor-pointer z-20 flex items-center justify-end pr-1"
            >
              <div className="w-8 h-8 rounded-full bg-white/60 flex items-center justify-center text-lg shadow hover:bg-white/90 transition-all">
                ▶
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Minimal bottom indicator */}
      <div className="flex items-center justify-center py-1 bg-black/20">
        <span className="text-xs font-bold text-white drop-shadow">
          {currentSpread * 2 + 1}-{Math.min(currentSpread * 2 + 2, allPages.length)} / {allPages.length}
        </span>
      </div>
    </div>
  );
}
