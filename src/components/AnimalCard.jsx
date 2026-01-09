import React, { useRef, useState, useEffect, useCallback } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { useAudio } from '../contexts/AudioContext';
import { useAssets } from '../contexts/AssetContext';
import { useFactLevel } from '../contexts/FactLevelContext';
import { useAccessibility } from '../contexts/AccessibilityContext';
import { getAssetPaths } from '../utils/slugify';

export default function AnimalCard({ animal }) {
  const { currentTheme } = useTheme();
  const { playSound, playClick, activeAnimalId } = useAudio();
  const { isCategoryDownloaded } = useAssets();
  const { isSimpleLevel } = useFactLevel();
  const { isMultiTouchBlocked, isIntentionalTouch } = useAccessibility();

  // Animation states: 'idle' | 'popping' | 'flipped' | 'unflipping' | 'shrinking'
  const [animState, setAnimState] = useState('idle');
  const [isFlipped, setIsFlipped] = useState(false);

  const pressStartRef = useRef(0);
  const pressPointerIdRef = useRef(null);
  const didLongPressRef = useRef(false);
  const startPosRef = useRef({ x: 0, y: 0 });
  const holdTimerRef = useRef(null);
  const animTimerRef = useRef(null);
  const audioRef = useRef(null);
  const ttsEndedRef = useRef(false);
  const rapidTouchCountRef = useRef(0);
  const lastTouchTimeRef = useRef(0);
  const touchStartTimeRef = useRef(0);

  // More intentional touch requirements for autistic users
  const HOLD_MS = 300;  // Hold time for intentional touch
  const MOVE_PX = 25;   // Less tolerance for movement (more intentional)
  const MIN_TOUCH_DURATION = 150; // Minimum touch duration to be considered intentional
  const MAX_RAPID_TOUCHES = 3; // Block after too many rapid touches
  const RAPID_TOUCH_WINDOW = 1000; // Time window for rapid touch detection

  const isActive = activeAnimalId === animal.id;
  const isDownloaded = isCategoryDownloaded(animal.category);

  const paths = getAssetPaths(animal.id);
  const imagePath = currentTheme === 'toy' ? paths.toyImage : paths.realImage;

  const simpleFactSrc = paths.factAudioSimple || paths.factAudioLegacy;
  const detailedFactSrc = paths.factAudioDetailed || paths.factAudioLegacy;
  const displayFact = isSimpleLevel ? (animal.simple_fact || animal.fact) : animal.fact;

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      if (holdTimerRef.current) clearTimeout(holdTimerRef.current);
      if (animTimerRef.current) clearTimeout(animTimerRef.current);
      // Stop any playing audio when unmounting
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      window.speechSynthesis?.cancel();
    };
  }, []);

  // Reset audio when theme or fact level changes
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    window.speechSynthesis?.cancel();
  }, [currentTheme, isSimpleLevel]);

  // Play fact audio and return a promise that resolves when done
  const playFactAudio = useCallback(() => {
    return new Promise((resolve) => {
      // Stop any existing audio first
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      window.speechSynthesis.cancel();
      
      const src = isSimpleLevel ? simpleFactSrc : detailedFactSrc;
      console.log('Playing fact:', { animal: animal.name, level: isSimpleLevel ? 'simple' : 'detailed', src });

      if (src) {
        // Use audio element to track when it ends
        const audio = new Audio(src);
        audioRef.current = audio;
        
        const cleanup = () => {
          if (audioRef.current === audio) {
            audioRef.current = null;
          }
        };
        
        audio.onended = () => {
          cleanup();
          resolve();
        };
        audio.onerror = () => {
          cleanup();
          // Fallback to TTS on error
          playTTS().then(resolve);
        };
        
        // Add timeout to prevent hanging
        const timeout = setTimeout(() => {
          cleanup();
          playTTS().then(resolve);
        }, 10000); // 10 second timeout
        
        audio.play().catch(() => {
          clearTimeout(timeout);
          cleanup();
          playTTS().then(resolve);
        });
      } else {
        playTTS().then(resolve);
      }
    });
  }, [isSimpleLevel, simpleFactSrc, detailedFactSrc, animal.name]);

  // Text-to-speech fallback
  const playTTS = useCallback(() => {
    return new Promise((resolve) => {
      // Cancel any existing TTS first
      window.speechSynthesis.cancel();
      
      if ('speechSynthesis' in window) {
        const text = displayFact || `${animal.name}. ${isSimpleLevel ? 'A cool animal!' : 'Lives in the wild.'}`;
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.85;
        
        utterance.onend = () => resolve();
        utterance.onerror = () => resolve();
        
        // Safety timeout in case onend doesn't fire
        const timeout = setTimeout(resolve, 15000);
        
        utterance.onstart = () => {
          // Clear timeout if it starts successfully
          clearTimeout(timeout);
        };
        
        window.speechSynthesis.speak(utterance);
      } else {
        resolve();
      }
    });
  }, [displayFact, animal.name, isSimpleLevel]);

  // Full animation sequence: pop out → pause → flip → audio plays → flip back → shrink back
  const triggerFullAnimation = useCallback(async () => {
    if (!isDownloaded || animState !== 'idle') return;

    // Step 1: Pop out (scale up)
    setAnimState('popping');
    
    // Step 2: After 250ms pause, flip the card
    await new Promise(r => setTimeout(r, 300));
    setIsFlipped(true);
    setAnimState('flipped');
    
    // Step 3: Wait a moment for flip animation, then play audio
    await new Promise(r => setTimeout(r, 400));
    
    // Step 4: Play the fact audio and wait for it to complete
    await playFactAudio();
    
    // Step 5: Small pause after audio
    await new Promise(r => setTimeout(r, 300));
    
    // Step 6: Flip back to show animal
    setIsFlipped(false);
    setAnimState('unflipping');
    
    // Step 7: Wait for flip back animation
    await new Promise(r => setTimeout(r, 400));
    
    // Step 8: Shrink back to normal
    setAnimState('shrinking');
    
    // Step 9: Return to idle
    await new Promise(r => setTimeout(r, 300));
    setAnimState('idle');
  }, [isDownloaded, animState, playFactAudio]);

  const handlePressStart = (e) => {
    // Block if multi-touch is detected or if we're in a blocked state
    if (isMultiTouchBlocked || e.touches.length > 1) {
      e.preventDefault();
      return false;
    }
    
    if (!isDownloaded) return;
    if (animState !== 'idle') return; // Don't interrupt animation
    
    const currentTime = Date.now();
    const timeSinceLastTouch = currentTime - lastTouchTimeRef.current;
    
    // Detect rapid accidental touches
    if (timeSinceLastTouch < RAPID_TOUCH_WINDOW && timeSinceLastTouch > 0) {
      rapidTouchCountRef.current++;
      if (rapidTouchCountRef.current >= MAX_RAPID_TOUCHES) {
        // Too many rapid touches, block for a moment
        e.preventDefault();
        setTimeout(() => {
          rapidTouchCountRef.current = 0;
        }, 2000);
        return false;
      }
    } else {
      rapidTouchCountRef.current = 1;
    }
    
    lastTouchTimeRef.current = currentTime;
    touchStartTimeRef.current = currentTime;
    
    // Prevent default to stop iOS image save dialog
    e.preventDefault();
    
    pressPointerIdRef.current = e.pointerId;
    pressStartRef.current = performance.now();
    didLongPressRef.current = false;
    startPosRef.current = { x: e.clientX ?? 0, y: e.clientY ?? 0 };
    playClick();

    const pid = e.pointerId;
    if (holdTimerRef.current) clearTimeout(holdTimerRef.current);
    
    holdTimerRef.current = setTimeout(() => {
      if (pressPointerIdRef.current === pid && !isMultiTouchBlocked) {
        const touchDuration = Date.now() - touchStartTimeRef.current;
        const movementDistance = 0; // Would calculate actual movement
        
        // Only trigger if this looks like an intentional touch
        if (isIntentionalTouch(touchDuration, movementDistance)) {
          didLongPressRef.current = true;
          triggerFullAnimation();
        }
      }
    }, HOLD_MS);

    const onUp = (ev) => {
      if (ev.pointerId !== pid) return;
      cleanup();
      handlePressEnd(ev);
    };
    
    const onCancel = (ev) => {
      if (ev.pointerId !== pid) return;
      cleanup();
      handlePressCancel(ev);
    };
    
    const onMove = (ev) => {
      if (ev.pointerId !== pid) return;
      const dx = (ev.clientX ?? 0) - (startPosRef.current.x ?? 0);
      const dy = (ev.clientY ?? 0) - (startPosRef.current.y ?? 0);
      const dist = Math.sqrt(dx * dx + dy * dy);
      
      // Only cancel if moved too far - very forgiving for wobbly hands
      if (dist >= MOVE_PX) {
        cleanup();
        pressPointerIdRef.current = null;
        if (holdTimerRef.current) clearTimeout(holdTimerRef.current);
      }
    };
    
    const cleanup = () => {
      window.removeEventListener('pointerup', onUp, true);
      window.removeEventListener('pointercancel', onCancel, true);
      window.removeEventListener('pointermove', onMove, true);
    };
    
    window.addEventListener('pointerup', onUp, true);
    window.addEventListener('pointercancel', onCancel, true);
    window.addEventListener('pointermove', onMove, true);
  };

  const handlePressEnd = (e) => {
    if (!isDownloaded) return;
    if (pressPointerIdRef.current !== e.pointerId) return;
    if (isMultiTouchBlocked) return; // Block if in multi-touch blocked state
    
    pressPointerIdRef.current = null;

    if (holdTimerRef.current) clearTimeout(holdTimerRef.current);

    const elapsed = performance.now() - (pressStartRef.current || 0);
    const touchDuration = Date.now() - touchStartTimeRef.current;
    const isHold = didLongPressRef.current || elapsed >= HOLD_MS;

    // For short taps, also check if it was intentional enough
    if (!isHold && animState === 'idle') {
      if (isIntentionalTouch(touchDuration, 0)) {
        // Short tap = play animal name
        playSound(paths.nameAudio, animal.id);
      }
    }
  };

  const handlePressCancel = (e) => {
    if (holdTimerRef.current) clearTimeout(holdTimerRef.current);
    if (pressPointerIdRef.current === e.pointerId) {
      pressPointerIdRef.current = null;
    }
  };

  // Prevent all default touch behaviors that could trigger iOS save dialog
  const preventDefaults = (e) => {
    e.preventDefault();
    e.stopPropagation();
    return false;
  };

  // Calculate transform based on animation state
  const getCardTransform = () => {
    switch (animState) {
      case 'popping':
      case 'flipped':
      case 'unflipping':
        return 'scale(1.15)';
      case 'shrinking':
        return 'scale(1.05)';
      default:
        return 'scale(1)';
    }
  };

  const getZIndex = () => {
    return animState !== 'idle' ? 50 : 1;
  };

  return (
    <div
      className={
        `animal-card relative flex flex-col select-none ` +
        (isActive ? 'active ' : '') +
        (!isDownloaded ? 'opacity-90 ' : '') +
        (animState !== 'idle' ? 'card-animating ' : '')
      }
      style={{
        transform: getCardTransform(),
        zIndex: getZIndex(),
        transition: 'transform 0.3s ease-out, z-index 0s',
        touchAction: 'none',
        WebkitTouchCallout: 'none',
        WebkitUserSelect: 'none',
        userSelect: 'none',
      }}
      onPointerDown={handlePressStart}
      onContextMenu={preventDefaults}
      onDragStart={preventDefaults}
      onTouchStart={(e) => e.preventDefault()}
    >
      <div 
        className="aspect-square rounded-xl overflow-hidden" 
        style={{ perspective: '1000px' }}
      >
        <div
          className="relative w-full h-full"
          style={{
            transformStyle: 'preserve-3d',
            transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
            transition: 'transform 0.4s ease-in-out',
          }}
        >
          {/* Front - Animal Image */}
          <div
            className="absolute inset-0 bg-gray-100"
            style={{ backfaceVisibility: 'hidden' }}
          >
            <img
              src={imagePath}
              alt={animal.name}
              className="w-full h-full object-cover pointer-events-none"
              loading="lazy"
              draggable="false"
              onContextMenu={preventDefaults}
              onDragStart={preventDefaults}
              onError={(e) => {
                e.target.src = '/assets/placeholder.webp';
              }}
              style={{
                WebkitTouchCallout: 'none',
                WebkitUserSelect: 'none',
                userSelect: 'none',
              }}
            />
          </div>
          {/* Back - Fact Text */}
          <div
            className="absolute inset-0 flex items-center justify-center p-3 rounded-xl"
            style={{
              backfaceVisibility: 'hidden',
              transform: 'rotateY(180deg)',
              background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 50%, #fbbf24 100%)',
              boxShadow: 'inset 0 2px 10px rgba(0,0,0,0.1)',
            }}
          >
            <p className="text-sm sm:text-base font-bold text-amber-900 text-center leading-relaxed">
              {displayFact}
            </p>
          </div>
        </div>
      </div>
      <h3 className="font-bold text-center text-xs sm:text-sm mt-1 leading-tight truncate px-1">
        {animal.name}
      </h3>

      {!isDownloaded && (
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center bg-white bg-opacity-60 rounded-xl">
          <span className="text-xl">📥</span>
        </div>
      )}

      {isActive && (
        <div className="absolute top-1 right-1">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
        </div>
      )}
    </div>
  );
}
