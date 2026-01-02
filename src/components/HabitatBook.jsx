import React, { useEffect, useMemo, useRef, useState, useCallback } from 'react';
import loadAnimalsWithFacts from '../data/loadAnimals';
import AnimalCard from './AnimalCard';
import { useTheme } from '../contexts/ThemeContext';
import { useFactLevel } from '../contexts/FactLevelContext';
import { useAudio } from '../contexts/AudioContext';
import { getHabitatBackgroundStyle } from '../utils/habitatBackground';
import { habitats } from '../data/habitats';

function chunk(arr, size) {
  const out = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}

export default function HabitatBook({ habitat, onAnnounceHabitat }) {
  const { isToyTheme } = useTheme();
  const { isSimpleLevel } = useFactLevel();
  const { playClick } = useAudio();
  const mode = isToyTheme && isSimpleLevel ? 'kid' : 'education';

  const [currentPage, setCurrentPage] = useState(0);
  const [flipDirection, setFlipDirection] = useState(null); // 'left' | 'right' | null
  const [isFlipping, setIsFlipping] = useState(false);

  const scrollerRef = useRef(null);
  const dragRef = useRef({ pending: false, active: false, pointerId: null, startX: 0, startScrollLeft: 0 });
  const rafRef = useRef(0);
  const prevHabitatRef = useRef(habitat);

  const animals = useMemo(() => {
    return loadAnimalsWithFacts
      .filter((a) => a.category === habitat)
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [habitat]);

  const pages = useMemo(() => chunk(animals, 12), [animals]);

  const habitatMeta = useMemo(() => {
    return habitats.find((h) => h.name === habitat) || { emoji: '📘', color: 'bg-slate-600' };
  }, [habitat]);

  const getPageWidth = () => {
    if (!scrollerRef.current) return 0;
    return scrollerRef.current.clientWidth || 0;
  };

  const flipToPage = useCallback((targetIdx) => {
    if (!scrollerRef.current || isFlipping) return;
    const w = getPageWidth();
    if (!w) return;

    const direction = targetIdx > currentPage ? 'left' : 'right';
    setFlipDirection(direction);
    setIsFlipping(true);
    playClick();

    // Animate flip then scroll
    setTimeout(() => {
      scrollerRef.current?.scrollTo({ left: w * targetIdx, behavior: 'auto' });
      setCurrentPage(targetIdx);
      setTimeout(() => {
        setFlipDirection(null);
        setIsFlipping(false);
      }, 150);
    }, 200);
  }, [currentPage, isFlipping, playClick]);

  const scrollToPage = (idx) => {
    flipToPage(idx);
  };

  const snapToNearestPage = () => {
    if (!scrollerRef.current) return;
    const w = getPageWidth();
    if (!w) return;
    const idx = Math.max(0, Math.min(pages.length - 1, Math.round(scrollerRef.current.scrollLeft / w)));
    scrollerRef.current.scrollTo({ left: w * idx, behavior: 'smooth' });
  };

  // Reset to page 0 when habitat changes and announce
  useEffect(() => {
    if (habitat !== prevHabitatRef.current) {
      setCurrentPage(0);
      if (scrollerRef.current) {
        scrollerRef.current.scrollTo({ left: 0, behavior: 'auto' });
      }
      onAnnounceHabitat?.(habitat);
      prevHabitatRef.current = habitat;
    }
  }, [habitat, onAnnounceHabitat]);

  useEffect(() => {
    if (!scrollerRef.current) return;
    const el = scrollerRef.current;
    const onScroll = () => {
      if (isFlipping) return;
      cancelAnimationFrame(rafRef.current);
      rafRef.current = requestAnimationFrame(() => {
        const w = el.clientWidth || 1;
        const idx = Math.max(0, Math.min(pages.length - 1, Math.round(el.scrollLeft / w)));
        setCurrentPage(idx);
      });
    };
    el.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    return () => {
      el.removeEventListener('scroll', onScroll);
      cancelAnimationFrame(rafRef.current);
    };
  }, [pages.length, isFlipping]);

  const flipClass = flipDirection === 'left' ? 'book-flip-left' : flipDirection === 'right' ? 'book-flip-right' : '';

  return (
    <div className="relative">
      <div className="mx-auto max-w-5xl">
        <div
          className={`book-container rounded-[2rem] backdrop-blur border border-white/60 shadow-2xl overflow-hidden ${flipClass}`}
          style={getHabitatBackgroundStyle(habitat, mode)}
        >
          {/* Page tabs on left (pages already read) */}
          {pages.length > 1 && currentPage > 0 && (
            <div className="absolute left-0 top-4 bottom-4 z-20 flex flex-col justify-center gap-1 pl-1">
              {pages
                .map((_, idx) => idx)
                .filter((idx) => idx < currentPage)
                .reverse()
                .slice(0, 5)
                .map((idx) => (
                  <button
                    key={`left-tab-${idx}`}
                    type="button"
                    onClick={() => scrollToPage(idx)}
                    disabled={isFlipping}
                    className={`book-tab-left pointer-events-auto w-8 h-8 flex items-center justify-center rounded-r-lg shadow-md text-white text-sm font-black ${habitatMeta.color} opacity-70 hover:opacity-100 hover:w-10 transition-all`}
                    aria-label={`Page ${idx + 1}`}
                  >
                    {idx + 1}
                  </button>
                ))}
            </div>
          )}

          {/* Page tabs on right (pages ahead) */}
          {pages.length > 1 && currentPage < pages.length - 1 && (
            <div className="absolute right-0 top-4 bottom-4 z-20 flex flex-col justify-center gap-1 pr-1 items-end">
              {pages
                .map((_, idx) => idx)
                .filter((idx) => idx > currentPage)
                .slice(0, 5)
                .map((idx) => (
                  <button
                    key={`right-tab-${idx}`}
                    type="button"
                    onClick={() => scrollToPage(idx)}
                    disabled={isFlipping}
                    className={`book-tab-right pointer-events-auto w-8 h-8 flex items-center justify-center rounded-l-lg shadow-md text-white text-sm font-black ${habitatMeta.color} opacity-70 hover:opacity-100 hover:w-10 transition-all`}
                    aria-label={`Page ${idx + 1}`}
                  >
                    {idx + 1}
                  </button>
                ))}
            </div>
          )}

          <div
            className="habitat-scroll flex overflow-x-auto snap-x snap-mandatory"
            style={{ WebkitOverflowScrolling: 'touch' }}
            ref={scrollerRef}
            onWheel={(e) => {
              if (!scrollerRef.current || isFlipping) return;
              const absY = Math.abs(e.deltaY);
              const absX = Math.abs(e.deltaX);
              if (absY > absX && Math.abs(e.deltaY) > 30) {
                const dir = e.deltaY > 0 ? 1 : -1;
                const next = Math.max(0, Math.min(pages.length - 1, currentPage + dir));
                if (next !== currentPage) flipToPage(next);
              }
            }}
            onPointerDown={(e) => {
              if (!scrollerRef.current || isFlipping) return;
              dragRef.current.pending = true;
              dragRef.current.active = false;
              dragRef.current.pointerId = e.pointerId;
              dragRef.current.startX = e.clientX;
              dragRef.current.startScrollLeft = scrollerRef.current.scrollLeft;
            }}
            onPointerMove={(e) => {
              if (!scrollerRef.current || isFlipping) return;
              if (!dragRef.current.pending) return;
              const dx = e.clientX - dragRef.current.startX;
              if (!dragRef.current.active) {
                if (Math.abs(dx) < 10) return;
                dragRef.current.active = true;
                scrollerRef.current.setPointerCapture?.(e.pointerId);
              }
              scrollerRef.current.scrollLeft = dragRef.current.startScrollLeft - dx;
            }}
            onPointerUp={(e) => {
              const wasDragging = dragRef.current.active;
              const dx = e.clientX - dragRef.current.startX;
              dragRef.current.pending = false;
              dragRef.current.active = false;
              dragRef.current.pointerId = null;
              if (wasDragging && Math.abs(dx) > 50) {
                const dir = dx < 0 ? 1 : -1;
                const next = Math.max(0, Math.min(pages.length - 1, currentPage + dir));
                flipToPage(next);
              } else if (wasDragging) {
                snapToNearestPage();
              }
            }}
            onPointerCancel={() => {
              dragRef.current.pending = false;
              dragRef.current.active = false;
              dragRef.current.pointerId = null;
              snapToNearestPage();
            }}
          >
            {pages.map((page, idx) => (
              <section
                key={idx}
                className="book-page snap-start shrink-0 w-full px-4 py-4"
              >
                {/* Minimal header: just icon + page indicator */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{habitatMeta.emoji}</span>
                    <span className="text-sm font-bold text-gray-600 hidden sm:inline">{habitat}</span>
                  </div>
                  <div className="text-xs font-bold text-gray-500 bg-white/50 rounded-full px-2 py-1">
                    {idx + 1} / {pages.length}
                  </div>
                </div>

                <div className="grid grid-cols-3 sm:grid-cols-3 md:grid-cols-4 gap-2 sm:gap-3">
                  {page.map((animal) => (
                    <AnimalCard key={animal.id} animal={animal} />
                  ))}
                </div>
              </section>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
