import React, { useState, useRef, useMemo, useCallback } from 'react';
import placesData from '../data/places.json';

function chunk(arr, size) {
  const out = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}

const typeIcons = {
  habitat: '🌿',
  landmark: '🏛️',
  city: '🏙️',
};

function PlaceCard({ place, continentColor, continentEmoji }) {
  const [isFlipped, setIsFlipped] = useState(false);

  const pressStartRef = useRef(0);
  const pressPointerIdRef = useRef(null);
  const didLongPressRef = useRef(false);
  const startPosRef = useRef({ x: 0, y: 0 });
  const holdTimerRef = useRef(null);
  const flipBackTimerRef = useRef(null);

  const HOLD_MS = 350;
  const MOVE_PX = 30;

  const scheduleFlipBack = () => {
    if (flipBackTimerRef.current) {
      window.clearTimeout(flipBackTimerRef.current);
    }
    flipBackTimerRef.current = window.setTimeout(() => {
      setIsFlipped(false);
    }, 500);
  };

  const speak = (text, { onDone } = {}) => {
    if (!('speechSynthesis' in window)) return;
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.onend = () => {
        try {
          if (typeof onDone === 'function') onDone();
        } catch {}
      };
      utterance.onerror = () => {
        try {
          if (typeof onDone === 'function') onDone();
        } catch {}
      };
      window.speechSynthesis.speak(utterance);
    } catch {}
  };

  const triggerFlipAndFact = () => {
    setIsFlipped(true);
    scheduleFlipBack();
    speak(place.fact, { onDone: scheduleFlipBack });
  };

  const handlePressStart = (e) => {
    pressPointerIdRef.current = e.pointerId;
    pressStartRef.current = performance.now();
    didLongPressRef.current = false;
    startPosRef.current = { x: e.clientX ?? 0, y: e.clientY ?? 0 };

    const pid = e.pointerId;
    if (holdTimerRef.current) window.clearTimeout(holdTimerRef.current);
    holdTimerRef.current = window.setTimeout(() => {
      if (pressPointerIdRef.current === pid) {
        didLongPressRef.current = true;
        triggerFlipAndFact();
      }
    }, HOLD_MS);

    const onUp = (ev) => {
      if (ev.pointerId !== pid) return;
      window.removeEventListener('pointerup', onUp, true);
      window.removeEventListener('pointercancel', onCancel, true);
      window.removeEventListener('pointermove', onMove, true);
      handlePressEnd(ev);
    };
    const onCancel = (ev) => {
      if (ev.pointerId !== pid) return;
      window.removeEventListener('pointerup', onUp, true);
      window.removeEventListener('pointercancel', onCancel, true);
      window.removeEventListener('pointermove', onMove, true);
      handlePressCancel(ev);
    };
    const onMove = (ev) => {
      if (ev.pointerId !== pid) return;
      const dx = (ev.clientX ?? 0) - (startPosRef.current.x ?? 0);
      const dy = (ev.clientY ?? 0) - (startPosRef.current.y ?? 0);
      if ((dx * dx + dy * dy) >= (MOVE_PX * MOVE_PX)) {
        window.removeEventListener('pointerup', onUp, true);
        window.removeEventListener('pointercancel', onCancel, true);
        window.removeEventListener('pointermove', onMove, true);
        if (!didLongPressRef.current && Math.abs(dy) > Math.abs(dx)) {
          didLongPressRef.current = true;
          triggerFlipAndFact();
        }
        pressPointerIdRef.current = null;
        if (holdTimerRef.current) window.clearTimeout(holdTimerRef.current);
      }
    };
    window.addEventListener('pointerup', onUp, true);
    window.addEventListener('pointercancel', onCancel, true);
    window.addEventListener('pointermove', onMove, true);
  };

  const handlePressEnd = (e) => {
    if (pressPointerIdRef.current !== e.pointerId) return;
    pressPointerIdRef.current = null;
    if (holdTimerRef.current) window.clearTimeout(holdTimerRef.current);

    const elapsed = performance.now() - (pressStartRef.current || 0);
    const isHold = didLongPressRef.current || elapsed >= HOLD_MS;

    if (isHold) {
      return;
    }

    if (isFlipped) setIsFlipped(false);
    speak(place.name);
  };

  const handlePressCancel = (e) => {
    if (holdTimerRef.current) window.clearTimeout(holdTimerRef.current);
    if (pressPointerIdRef.current === e.pointerId) {
      pressPointerIdRef.current = null;
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      className={
        `relative aspect-square rounded-2xl border-3 overflow-hidden ` +
        `transition-all duration-300 shadow-lg ` +
        `hover:scale-105 hover:shadow-xl active:scale-95 ` +
        (isFlipped ? 'ring-4 ring-teal-400 ring-offset-2 ' : '')
      }
      style={{
        backgroundColor: continentColor + '30',
        borderColor: continentColor,
      }}
      onPointerDown={handlePressStart}
      onContextMenu={(e) => e.preventDefault()}
    >
      <div className={`absolute inset-0 flex flex-col transition-opacity duration-300 ${isFlipped ? 'opacity-0' : 'opacity-100'}`}>
        <div className="absolute top-2 right-2 px-2 py-1 rounded-full bg-white/80 text-xs font-medium">
          {typeIcons[place.type]}
        </div>
        <div className="flex-1 flex items-center justify-center text-5xl opacity-30">
          {continentEmoji}
        </div>
        <div className="bg-white/90 backdrop-blur-sm p-2">
          <span className="text-sm font-bold text-gray-800 block text-center truncate">{place.name}</span>
        </div>
      </div>

      <div
        className={`absolute inset-0 p-3 flex flex-col justify-center transition-opacity duration-300 ${isFlipped ? 'opacity-100' : 'opacity-0'}`}
        style={{ backgroundColor: continentColor + '50' }}
      >
        <p className="text-xs text-gray-800 text-center leading-relaxed font-medium">{place.fact}</p>
      </div>
    </div>
  );
}

export default function PlacesBook({ onBack }) {
  const [currentContinentIdx, setCurrentContinentIdx] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);
  const [flipDirection, setFlipDirection] = useState(null);
  const [isFlipping, setIsFlipping] = useState(false);
  const scrollerRef = useRef(null);

  const continent = placesData.continents[currentContinentIdx];
  const pages = useMemo(() => chunk(continent.places, 12), [continent]);

  const flipToPage = useCallback((targetIdx) => {
    if (isFlipping || targetIdx < 0 || targetIdx >= pages.length) return;
    const direction = targetIdx > currentPage ? 'left' : 'right';
    setFlipDirection(direction);
    setIsFlipping(true);

    setTimeout(() => {
      setCurrentPage(targetIdx);
      if (scrollerRef.current) {
        scrollerRef.current.scrollTo({ left: scrollerRef.current.clientWidth * targetIdx, behavior: 'auto' });
      }
      setTimeout(() => {
        setFlipDirection(null);
        setIsFlipping(false);
      }, 150);
    }, 200);
  }, [currentPage, isFlipping, pages.length]);

  const handleContinentChange = (idx) => {
    setCurrentContinentIdx(idx);
    setCurrentPage(0);
    if (scrollerRef.current) {
      scrollerRef.current.scrollTo({ left: 0, behavior: 'auto' });
    }
  };

  const flipClass = flipDirection === 'left' ? 'book-flip-left' : flipDirection === 'right' ? 'book-flip-right' : '';

  return (
    <div className="min-h-screen" style={{ background: `linear-gradient(135deg, ${continent.color}40 0%, #ecfeff 50%, ${continent.color}20 100%)` }}>
      {/* Header */}
      <div className="sticky top-0 z-30 text-white shadow-lg" style={{ background: `linear-gradient(90deg, ${continent.color}, #06b6d4)` }}>
        <div className="flex items-center gap-3 p-3">
          <button onClick={onBack} className="p-2 rounded-full bg-white/20 hover:bg-white/30 transition-colors">
            <span className="text-xl">🏠</span>
          </button>
          <span className="text-3xl">🌍</span>
          <h1 className="text-xl font-bold flex-1">Explore Places</h1>
          <span className="text-xs bg-white/20 rounded-full px-2 py-1">
            {placesData.continents.reduce((sum, c) => sum + c.places.length, 0)} places
          </span>
        </div>
      </div>

      {/* Continent Rail - Left Side */}
      <div className="fixed left-0 top-20 bottom-0 z-20 w-12 flex flex-col items-center py-4 gap-2 overflow-y-auto">
        {placesData.continents.map((cont, idx) => (
          <button
            key={cont.id}
            onClick={() => handleContinentChange(idx)}
            className={`
              w-10 h-10 rounded-xl flex items-center justify-center text-lg
              transition-all shadow-md
              ${idx === currentContinentIdx ? 'scale-110 ring-2 ring-white' : 'opacity-70 hover:opacity-100'}
            `}
            style={{ backgroundColor: cont.color }}
            title={cont.name}
          >
            {cont.emoji}
          </button>
        ))}
      </div>

      {/* Main Book Content */}
      <div className="ml-14 p-4">
        <div className="mx-auto max-w-5xl">
          <div
            className={`book-container rounded-[2rem] backdrop-blur border-4 border-white/60 shadow-2xl overflow-hidden ${flipClass}`}
            style={{ backgroundColor: continent.color + '15' }}
          >
            {/* Page tabs on left */}
            {pages.length > 1 && currentPage > 0 && (
              <div className="absolute left-0 top-4 bottom-4 z-20 flex flex-col justify-center gap-1 pl-1">
                {Array.from({ length: Math.min(5, currentPage) }, (_, i) => currentPage - 1 - i)
                  .filter(idx => idx >= 0)
                  .map((idx) => (
                    <button
                      key={`left-${idx}`}
                      onClick={() => flipToPage(idx)}
                      disabled={isFlipping}
                      className="w-8 h-8 flex items-center justify-center rounded-r-lg shadow-md text-white text-sm font-black opacity-70 hover:opacity-100 hover:w-10 transition-all"
                      style={{ backgroundColor: continent.color }}
                    >
                      {idx + 1}
                    </button>
                  ))}
              </div>
            )}

            {/* Page tabs on right */}
            {pages.length > 1 && currentPage < pages.length - 1 && (
              <div className="absolute right-0 top-4 bottom-4 z-20 flex flex-col justify-center gap-1 pr-1 items-end">
                {Array.from({ length: Math.min(5, pages.length - currentPage - 1) }, (_, i) => currentPage + 1 + i)
                  .map((idx) => (
                    <button
                      key={`right-${idx}`}
                      onClick={() => flipToPage(idx)}
                      disabled={isFlipping}
                      className="w-8 h-8 flex items-center justify-center rounded-l-lg shadow-md text-white text-sm font-black opacity-70 hover:opacity-100 hover:w-10 transition-all"
                      style={{ backgroundColor: continent.color }}
                    >
                      {idx + 1}
                    </button>
                  ))}
              </div>
            )}

            {/* Scrollable Pages */}
            <div
              ref={scrollerRef}
              className="habitat-scroll flex overflow-x-auto snap-x snap-mandatory"
              style={{ WebkitOverflowScrolling: 'touch' }}
            >
              {pages.map((pagePlaces, idx) => (
                <section key={idx} className="book-page snap-start shrink-0 w-full px-6 py-4">
                  {/* Page header */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <span className="text-3xl">{continent.emoji}</span>
                      <span className="text-lg font-bold" style={{ color: continent.color }}>{continent.name}</span>
                    </div>
                    <div className="text-xs font-bold text-gray-500 bg-white/70 rounded-full px-3 py-1">
                      {idx + 1} / {pages.length}
                    </div>
                  </div>

                  {/* Places Grid - up to 12 per page */}
                  <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-4 gap-3">
                    {pagePlaces.map((place, pIdx) => (
                      <PlaceCard 
                        key={pIdx} 
                        place={place} 
                        continentColor={continent.color}
                        continentEmoji={continent.emoji}
                        continentId={continent.id}
                      />
                    ))}
                  </div>
                </section>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
