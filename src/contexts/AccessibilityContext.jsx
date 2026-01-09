import React, { createContext, useContext, useEffect, useRef, useState } from 'react';

const AccessibilityContext = createContext();

export function AccessibilityProvider({ children }) {
  const [isMultiTouchBlocked, setIsMultiTouchBlocked] = useState(false);
  const lastTouchTimeRef = useRef(0);
  const touchCountRef = useRef(0);
  const activeTouchesRef = useRef(new Map());
  const gestureBlockTimeoutRef = useRef(null);

  // Prevent multi-finger gestures and tab switching
  useEffect(() => {
    const handleTouchStart = (e) => {
      const touchCount = e.touches.length;
      const currentTime = Date.now();
      
      // Track active touches
      activeTouchesRef.current.clear();
      for (let i = 0; i < touchCount; i++) {
        activeTouchesRef.current.set(e.touches[i].identifier, {
          x: e.touches[i].clientX,
          y: e.touches[i].clientY,
          startTime: currentTime
        });
      }

      // Block multi-touch gestures (2+ fingers)
      if (touchCount >= 2) {
        e.preventDefault();
        setIsMultiTouchBlocked(true);
        
        // Clear block after a short delay
        if (gestureBlockTimeoutRef.current) {
          clearTimeout(gestureBlockTimeoutRef.current);
        }
        gestureBlockTimeoutRef.current = setTimeout(() => {
          setIsMultiTouchBlocked(false);
        }, 1000);
        
        return false;
      }

      // Detect rapid zigzag movements (accidental touches)
      if (touchCount === 1) {
        const timeSinceLastTouch = currentTime - lastTouchTimeRef.current;
        
        // If touches are too rapid (< 100ms apart), likely accidental
        if (timeSinceLastTouch < 100 && timeSinceLastTouch > 0) {
          e.preventDefault();
          return false;
        }
        
        lastTouchTimeRef.current = currentTime;
      }
    };

    const handleTouchMove = (e) => {
      const touchCount = e.touches.length;
      
      // Block multi-touch movements
      if (touchCount >= 2 || isMultiTouchBlocked) {
        e.preventDefault();
        return false;
      }

      // Track single finger movement for zigzag detection
      if (touchCount === 1 && !isMultiTouchBlocked) {
        const touch = e.touches[0];
        const touchId = touch.identifier;
        const trackedTouch = activeTouchesRef.current.get(touchId);
        
        if (trackedTouch) {
          const deltaX = Math.abs(touch.clientX - trackedTouch.x);
          const deltaY = Math.abs(touch.clientY - trackedTouch.y);
          const deltaTime = Date.now() - trackedTouch.startTime;
          
          // Detect rapid zigzag: quick direction changes within short time
          if (deltaTime < 200 && (deltaX > 100 || deltaY > 100)) {
            // This looks like an accidental swipe, block it
            e.preventDefault();
            return false;
          }
        }
      }
    };

    const handleTouchEnd = (e) => {
      const touchCount = e.touches.length;
      
      // Clean up touch tracking
      if (e.changedTouches.length > 0) {
        for (let i = 0; i < e.changedTouches.length; i++) {
          activeTouchesRef.current.delete(e.changedTouches[i].identifier);
        }
      }
      
      // Reset multi-touch block when all fingers are lifted
      if (touchCount === 0) {
        setIsMultiTouchBlocked(false);
        if (gestureBlockTimeoutRef.current) {
          clearTimeout(gestureBlockTimeoutRef.current);
        }
      }
    };

    const handleGestureStart = (e) => {
      e.preventDefault();
      return false;
    };

    // Prevent default iOS gestures
    document.addEventListener('touchstart', handleTouchStart, { passive: false });
    document.addEventListener('touchmove', handleTouchMove, { passive: false });
    document.addEventListener('touchend', handleTouchEnd, { passive: false });
    document.addEventListener('gesturestart', handleGestureStart, { passive: false });

    // Prevent pinch zoom and other multi-touch gestures
    document.addEventListener('touchstart', (e) => {
      if (e.touches.length > 1) {
        e.preventDefault();
      }
    }, { passive: false });

    // Prevent double-tap zoom
    let lastTouchEnd = 0;
    document.addEventListener('touchend', (e) => {
      const now = Date.now();
      if (now - lastTouchEnd <= 300) {
        e.preventDefault();
      }
      lastTouchEnd = now;
    }, { passive: false });

    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchmove', handleTouchMove);
      document.removeEventListener('touchend', handleTouchEnd);
      document.removeEventListener('gesturestart', handleGestureStart);
    };
  }, [isMultiTouchBlocked]);

  // Prevent navigation away from app
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      e.preventDefault();
      e.returnValue = 'Stay in Liora\'s Animal World?';
      return e.returnValue;
    };

    const handleVisibilityChange = () => {
      // If user tries to leave, bring focus back
      if (document.hidden) {
        setTimeout(() => {
          window.focus();
        }, 100);
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  const value = {
    isMultiTouchBlocked,
    isIntentionalTouch: (touchDuration, movementDistance) => {
      // Require intentional touches: longer duration + minimal movement
      return touchDuration > 200 && movementDistance < 30;
    }
  };

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
    </AccessibilityContext.Provider>
  );
}

export function useAccessibility() {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
}
