import React, { useState, useRef, useMemo, useCallback } from 'react';
import aslData from '../data/asl_words.json';

function chunk(arr, size) {
  const out = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}

function slugify(text) {
  return text.lower().replace(" ", "_").replace("'", "").replace("-", "_") + ".png";
}

function WordCard({ word, categoryColor, categoryEmoji, categoryId }) {
  const [isPressed, setIsPressed] = useState(false);
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

  const triggerFlipAndBackSpeech = () => {
    setIsFlipped(true);
    scheduleFlipBack();
    speak(`How to sign ${word}`, { onDone: scheduleFlipBack });
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
        triggerFlipAndBackSpeech();
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
          triggerFlipAndBackSpeech();
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

    setIsPressed(true);
    speak(word);
    setTimeout(() => setIsPressed(false), 150);
  };

  const handlePressCancel = (e) => {
    if (holdTimerRef.current) window.clearTimeout(holdTimerRef.current);
    if (pressPointerIdRef.current === e.pointerId) {
      pressPointerIdRef.current = null;
    }
  };

  // Construct image path: /assets/images/asl/{categoryId}/{slug}.png
  const slug = word.toLowerCase().replace(/ /g, '_').replace(/'/g, '').replace(/-/g, '_');
  const imagePath = `/assets/images/asl/${categoryId}/${slug}.png`;

  return (
    <div
      role="button"
      tabIndex={0}
      onPointerDown={handlePressStart}
      onContextMenu={(e) => e.preventDefault()}
      className={`
        relative aspect-square rounded-2xl border-3 overflow-hidden
        transition-all duration-150 shadow-lg
        hover:scale-105 hover:shadow-xl
        active:scale-95
        ${(isPressed || isFlipped) ? 'ring-4 ring-purple-400 ring-offset-2' : ''}
      `}
      style={{
        backgroundColor: categoryColor + '30',
        borderColor: categoryColor,
        perspective: '1000px',
      }}
    >
      <div
        className="absolute inset-0 transition-transform duration-500 ease-out"
        style={{
          transformStyle: 'preserve-3d',
          transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
        }}
      >
        <div
          className="absolute inset-0"
          style={{ backfaceVisibility: 'hidden' }}
        >
          <img
            src={imagePath}
            alt={`${word} sign`}
            className="absolute inset-0 w-full h-full object-cover opacity-90"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />

          <div className="absolute inset-0 hidden items-center justify-center text-4xl opacity-30">
            {categoryEmoji}
          </div>

          <div className="absolute bottom-0 left-0 right-0 bg-white/90 backdrop-blur-sm p-2">
            <span className="text-sm font-bold text-gray-800 block text-center truncate">{word}</span>
          </div>
        </div>

        <div
          className="absolute inset-0 flex flex-col items-center justify-center p-3"
          style={{
            backfaceVisibility: 'hidden',
            transform: 'rotateY(180deg)',
            backgroundColor: categoryColor + '55',
          }}
        >
          <p className="text-xs text-gray-800 text-center leading-relaxed font-bold">
            How to sign
          </p>
          <p className="text-sm text-gray-900 text-center leading-tight font-black mt-1">
            {word}
          </p>
        </div>
      </div>
    </div>
  );
}

export default function ASLBook({ onBack }) {
  const [currentCategoryIdx, setCurrentCategoryIdx] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);
  const [flipDirection, setFlipDirection] = useState(null);
  const [isFlipping, setIsFlipping] = useState(false);
  const scrollerRef = useRef(null);

  const category = aslData.categories[currentCategoryIdx];
  const pages = useMemo(() => chunk(category.words, 12), [category]);

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

  const handleCategoryChange = (idx) => {
    setCurrentCategoryIdx(idx);
    setCurrentPage(0);
    if (scrollerRef.current) {
      scrollerRef.current.scrollTo({ left: 0, behavior: 'auto' });
    }
  };

  const flipClass = flipDirection === 'left' ? 'book-flip-left' : flipDirection === 'right' ? 'book-flip-right' : '';

  return (
    <div className="min-h-screen" style={{ background: `linear-gradient(135deg, ${category.color}40 0%, #fdf2f8 50%, ${category.color}20 100%)` }}>
      {/* Header */}
      <div className="sticky top-0 z-30 text-white shadow-lg" style={{ background: `linear-gradient(90deg, ${category.color}, #ec4899)` }}>
        <div className="flex items-center gap-3 p-3">
          <button onClick={onBack} className="p-2 rounded-full bg-white/20 hover:bg-white/30 transition-colors">
            <span className="text-xl">🏠</span>
          </button>
          <span className="text-3xl">🤟</span>
          <h1 className="text-xl font-bold flex-1">Sign Language</h1>
          <span className="text-xs bg-white/20 rounded-full px-2 py-1">
            {aslData.categories.reduce((sum, c) => sum + c.words.length, 0)} signs
          </span>
        </div>
      </div>

      {/* Category Rail - Left Side */}
      <div className="fixed left-0 top-20 bottom-0 z-20 w-12 flex flex-col items-center py-4 gap-2 overflow-y-auto">
        {aslData.categories.map((cat, idx) => (
          <button
            key={cat.id}
            onClick={() => handleCategoryChange(idx)}
            className={`
              w-10 h-10 rounded-xl flex items-center justify-center text-lg
              transition-all shadow-md
              ${idx === currentCategoryIdx ? 'scale-110 ring-2 ring-white' : 'opacity-70 hover:opacity-100'}
            `}
            style={{ backgroundColor: cat.color }}
            title={cat.name}
          >
            {cat.emoji}
          </button>
        ))}
      </div>

      {/* Main Book Content */}
      <div className="ml-14 p-4">
        <div className="mx-auto max-w-5xl">
          <div
            className={`book-container rounded-[2rem] backdrop-blur border-4 border-white/60 shadow-2xl overflow-hidden ${flipClass}`}
            style={{ backgroundColor: category.color + '15' }}
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
                      style={{ backgroundColor: category.color }}
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
                      style={{ backgroundColor: category.color }}
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
              {pages.map((pageWords, idx) => (
                <section key={idx} className="book-page snap-start shrink-0 w-full px-6 py-4">
                  {/* Page header */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <span className="text-3xl">{category.emoji}</span>
                      <span className="text-lg font-bold" style={{ color: category.color }}>{category.name}</span>
                    </div>
                    <div className="text-xs font-bold text-gray-500 bg-white/70 rounded-full px-3 py-1">
                      {idx + 1} / {pages.length}
                    </div>
                  </div>

                  {/* Words Grid - 12 per page */}
                  <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-4 gap-3">
                    {pageWords.map((word, wIdx) => (
                      <WordCard 
                        key={wIdx} 
                        word={word} 
                        categoryColor={category.color}
                        categoryEmoji={category.emoji}
                        categoryId={category.id}
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
