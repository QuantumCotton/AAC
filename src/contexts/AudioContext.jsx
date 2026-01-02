import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import { Howl, Howler } from 'howler';

const AudioContext = createContext();

export function AudioProvider({ children }) {
  const [currentSound, setCurrentSound] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeAnimalId, setActiveAnimalId] = useState(null);

  const unlockedRef = useRef(false);
  const onEndRef = useRef(null);
  const onStopRef = useRef(null);
  const soundCacheRef = useRef(new Map());
  const cacheOrderRef = useRef([]);
  const MAX_CACHED_SOUNDS = 40;

  const cacheKeyFor = (sources) => {
    const arr = Array.isArray(sources) ? sources : [sources];
    return arr.filter(Boolean).join('|');
  };

  const getOrCreateSound = (sources) => {
    const key = cacheKeyFor(sources);
    const existing = soundCacheRef.current.get(key);
    if (existing) return existing;

    const sound = new Howl({
      src: Array.isArray(sources) ? sources : [sources],
      preload: true,
      onplay: () => {
        setIsPlaying(true);
      },
      onend: () => {
        setIsPlaying(false);
        setActiveAnimalId(null);
        try {
          const cb = onEndRef.current;
          onEndRef.current = null;
          onStopRef.current = null;
          if (typeof cb === 'function') cb();
        } catch {}
      },
      onstop: () => {
        setIsPlaying(false);
        setActiveAnimalId(null);
        try {
          const cb = onStopRef.current;
          onEndRef.current = null;
          onStopRef.current = null;
          if (typeof cb === 'function') cb();
        } catch {}
      },
      onloaderror: (_id, _err) => {
        try {
          const s2 = new Howl({
            src: Array.isArray(sources) ? sources : [sources],
            preload: true,
            html5: true,
            onplay: () => setIsPlaying(true),
            onend: () => {
              setIsPlaying(false);
              setActiveAnimalId(null);
              try {
                const cb = onEndRef.current;
                onEndRef.current = null;
                onStopRef.current = null;
                if (typeof cb === 'function') cb();
              } catch {}
            },
            onstop: () => {
              setIsPlaying(false);
              setActiveAnimalId(null);
              try {
                const cb = onStopRef.current;
                onEndRef.current = null;
                onStopRef.current = null;
                if (typeof cb === 'function') cb();
              } catch {}
            }
          });
          soundCacheRef.current.set(key, s2);
        } catch {}
      }
    });

    soundCacheRef.current.set(key, sound);
    cacheOrderRef.current.push(key);
    if (cacheOrderRef.current.length > MAX_CACHED_SOUNDS) {
      const evict = cacheOrderRef.current.shift();
      const toDrop = soundCacheRef.current.get(evict);
      if (toDrop) {
        try {
          toDrop.unload();
        } catch {}
      }
      soundCacheRef.current.delete(evict);
    }

    return sound;
  };

  useEffect(() => {
    const unlock = async () => {
      if (unlockedRef.current) return;
      try {
        if (Howler?.ctx?.state === 'suspended') {
          await Howler.ctx.resume();
        }
      } catch {}
      unlockedRef.current = true;
      window.removeEventListener('pointerdown', unlock);
      window.removeEventListener('touchstart', unlock);
      window.removeEventListener('mousedown', unlock);
    };

    window.addEventListener('pointerdown', unlock, { passive: true });
    window.addEventListener('touchstart', unlock, { passive: true });
    window.addEventListener('mousedown', unlock, { passive: true });
    return () => {
      window.removeEventListener('pointerdown', unlock);
      window.removeEventListener('touchstart', unlock);
      window.removeEventListener('mousedown', unlock);
    };
  }, []);

  const playClick = () => {
    if (!unlockedRef.current) {
      try {
        Howler?.ctx?.resume?.();
      } catch {}
      unlockedRef.current = true;
    }

    const ctx = Howler?.ctx;
    if (!ctx) return;

    try {
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(820, now);
      gain.gain.setValueAtTime(0.0001, now);
      gain.gain.exponentialRampToValueAtTime(0.18, now + 0.004);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.045);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.05);
    } catch {}
  };

  const playSound = (src, animalId = null, opts = null) => {
    if (!unlockedRef.current) {
      try {
        Howler?.ctx?.resume?.();
      } catch {}
      unlockedRef.current = true;
    }

    const sources = Array.isArray(src) ? src : [src];
    const sound = getOrCreateSound(sources);

    // Stop current sound if playing
    if (currentSound && currentSound !== sound) {
      onEndRef.current = null;
      onStopRef.current = null;
      currentSound.stop();
    }

    setActiveAnimalId(animalId);
    setCurrentSound(sound);
    try {
      if (sound.playing()) {
        onEndRef.current = null;
        onStopRef.current = null;
        sound.stop();
      }
    } catch {}
    onEndRef.current = opts?.onEnd ?? null;
    onStopRef.current = opts?.onStop ?? null;
    sound.play();

    // Track interaction
    if (animalId) {
      trackInteraction(animalId);
    }
  };

  const stopSound = () => {
    if (currentSound) {
      currentSound.stop();
    }
  };

  const trackInteraction = (animalId) => {
    const key = `stats_${animalId}_clicks`;
    const current = parseInt(localStorage.getItem(key) || '0');
    localStorage.setItem(key, (current + 1).toString());
  };

  const value = {
    playSound,
    playClick,
    stopSound,
    isPlaying,
    activeAnimalId
  };

  return (
    <AudioContext.Provider value={value}>
      {children}
    </AudioContext.Provider>
  );
}

export function useAudio() {
  const context = useContext(AudioContext);
  if (!context) {
    throw new Error('useAudio must be used within an AudioProvider');
  }
  return context;
}
