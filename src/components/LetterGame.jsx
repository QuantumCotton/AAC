import React, { useState, useCallback, useRef, useEffect, useMemo } from 'react';
import { useAudio } from '../contexts/AudioContext';
import { useAccessibility } from '../contexts/AccessibilityContext';
import { ALPHABET, ALPHABET_COLORS } from './AlphabetBook';

const WRONG_THRESHOLD = 10;
const ERROR_WINDOW = 3000;

export default function LetterGame() {
  const { playSound, playClick } = useAudio();
  const { isIntentionalTouch } = useAccessibility();
  
  const [currentLetterIndex, setCurrentLetterIndex] = useState(0);
  const [completedLetters, setCompletedLetters] = useState([]);
  const [wrongClicks, setWrongClicks] = useState(0);
  const [isErrorMode, setIsErrorMode] = useState(false);
  const [lastCorrectTime, setLastCorrectTime] = useState(Date.now());
  
  const wrongClicksRef = useRef([]);
  
  const letterPositions = useMemo(() => {
    const positions = [];
    const maxAttempts = 100;
    const minSpacing = 15;
    
    ALPHABET.forEach((letter, index) => {
      let attempts = 0;
      let x, y;
      
      while (attempts < maxAttempts) {
        const size = Math.random() * 10 + 10;
        x = Math.random() * 70 + 10;
        y = Math.random() * 60 + 15;
        const rotation = Math.random() * 40 - 20;
        
        const overlaps = positions.some(pos => {
          const dx = x - parseFloat(pos.left);
          const dy = y - parseFloat(pos.top);
          const distance = Math.sqrt(dx * dx + dy * dy);
          return distance < minSpacing;
        });
        
        if (!overlaps) {
          positions.push({
            letter,
            index,
            size: `${size}%`,
            left: `${x}%`,
            top: `${y}%`,
            transform: `rotate(${rotation}deg)`,
            zIndex: Math.floor(Math.random() * 10) + 1
          });
          break;
        }
        
        attempts++;
      }
      
      if (attempts >= maxAttempts) {
        const col = index % 5;
        const row = Math.floor(index / 5);
        const size = 15;
        x = col * 18 + 10;
        y = row * 18 + 10;
        
        positions.push({
          letter,
          index,
          size: `${size}%`,
          left: `${x}%`,
          top: `${y}%`,
          transform: 'rotate(0deg)',
          zIndex: 1
        });
      }
    });
    
    return positions;
  }, []);
  
  const playSoundEffect = useCallback((type) => {
    switch (type) {
      case 'correct':
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        // Exciting "pop" sound - higher pitch and louder
        osc.frequency.setValueAtTime(800, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(1200, ctx.currentTime + 0.08);
        gain.gain.setValueAtTime(0.5, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.2);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.2);
        break;
        
      case 'wrong':
        const ctxErr = new (window.AudioContext || window.webkitAudioContext)();
        const oscErr = ctxErr.createOscillator();
        const gainErr = ctxErr.createGain();
        oscErr.type = 'triangle';
        oscErr.frequency.setValueAtTime(150, ctxErr.currentTime);
        oscErr.frequency.exponentialRampToValueAtTime(100, ctxErr.currentTime + 0.1);
        gainErr.gain.setValueAtTime(0.2, ctxErr.currentTime);
        gainErr.gain.exponentialRampToValueAtTime(0.001, ctxErr.currentTime + 0.2);
        oscErr.connect(gainErr);
        gainErr.connect(ctxErr.destination);
        oscErr.start(ctxErr.currentTime);
        oscErr.stop(ctxErr.currentTime + 0.2);
        break;
        
      case 'ding':
        const ctxDing = new (window.AudioContext || window.webkitAudioContext)();
        const oscDing = ctxDing.createOscillator();
        const gainDing = ctxDing.createGain();
        oscDing.type = 'sine';
        // Brighter ding sound for kids
        oscDing.frequency.setValueAtTime(1500, ctxDing.currentTime);
        gainDing.gain.setValueAtTime(0.5, ctxDing.currentTime);
        gainDing.gain.exponentialRampToValueAtTime(0.001, ctxDing.currentTime + 0.4);
        oscDing.connect(gainDing);
        gainDing.connect(ctxDing.destination);
        oscDing.start(ctxDing.currentTime);
        oscDing.stop(ctxDing.currentTime + 0.4);
        break;
        
      case 'buzz':
        const ctxBuzz = new (window.AudioContext || window.webkitAudioContext)();
        const oscBuzz = ctxBuzz.createOscillator();
        const gainBuzz = ctxBuzz.createGain();
        oscBuzz.type = 'sawtooth';
        oscBuzz.frequency.setValueAtTime(80, ctxBuzz.currentTime);
        gainBuzz.gain.setValueAtTime(0.15, ctxBuzz.currentTime);
        gainBuzz.gain.exponentialRampToValueAtTime(0.001, ctxBuzz.currentTime + 0.4);
        oscBuzz.connect(gainBuzz);
        gainBuzz.connect(ctxBuzz.destination);
        oscBuzz.start(ctxBuzz.currentTime);
        oscBuzz.stop(ctxBuzz.currentTime + 0.4);
        break;
    }
  }, []);
  
  const handleLetterPress = useCallback((letter, index) => {
    const expectedLetter = ALPHABET[currentLetterIndex];
    const now = Date.now();
    
    if (!isIntentionalTouch(now, 0)) {
      return;
    }
    
    if (letter === expectedLetter) {
      playSoundEffect('correct');
      setCurrentLetterIndex(prev => prev + 1);
      setCompletedLetters(prev => [...prev, letter]);
      setWrongClicks(0);
      wrongClicksRef.current = [];
      setLastCorrectTime(now);
      setIsErrorMode(false);
      
      if (currentLetterIndex > 0 && currentLetterIndex % 5 === 0) {
        playSoundEffect('ding');
      }
      
      if (currentLetterIndex >= ALPHABET.length - 1) {
        playSoundEffect('ding');
      }
    } else {
      playSoundEffect('wrong');
      setWrongClicks(prev => prev + 1);
      wrongClicksRef.current.push(now);
      
      const recentClicks = wrongClicksRef.current.filter(t => now - t < ERROR_WINDOW);
      wrongClicksRef.current = recentClicks;
      
      if (recentClicks.length >= WRONG_THRESHOLD) {
        setIsErrorMode(true);
        playSoundEffect('buzz');
      }
    }
  }, [currentLetterIndex, isIntentionalTouch, playSoundEffect]);
  
  const resetGame = useCallback(() => {
    setCurrentLetterIndex(0);
    setCompletedLetters([]);
    setWrongClicks(0);
    wrongClicksRef.current = [];
    setIsErrorMode(false);
    setLastCorrectTime(Date.now());
    playClick();
  }, [playClick]);
  
  useEffect(() => {
    if (!isErrorMode && currentLetterIndex > 0) {
      const timeSinceCorrect = Date.now() - lastCorrectTime;
      if (timeSinceCorrect > 5000 && timeSinceCorrect < 5100) {
        playSoundEffect('ding');
      }
    }
  }, [currentLetterIndex, lastCorrectTime, isErrorMode, playSoundEffect]);
  
  useEffect(() => {
    if (isErrorMode) {
      const timeout = setTimeout(() => {
        setIsErrorMode(false);
        setWrongClicks(0);
        wrongClicksRef.current = [];
      }, 3000);
      
      return () => clearTimeout(timeout);
    }
  }, [isErrorMode]);
  
  const currentLetter = ALPHABET[currentLetterIndex];
  const isGameComplete = currentLetterIndex >= ALPHABET.length;

  return (
    <div 
      className="relative w-full h-full"
      style={{
        background: isErrorMode 
          ? 'linear-gradient(135deg, #7f1d1d 0%, #5b21b6 50%, #374151 100%)'
          : 'linear-gradient(135deg, #fef3c7 0%, #fde68a 50%, #fcd34d 100%)',
        transition: 'background 0.5s ease',
        opacity: isErrorMode ? 0.5 : 1,
      }}
    >
      {isErrorMode && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 z-50">
          <div className="text-center">
            <div className="text-6xl mb-4">⚠️</div>
            <div className="text-2xl font-bold text-white mb-2">
              Too many wrong taps!
            </div>
            <div className="text-lg text-white/80">
              Wait a moment...
            </div>
          </div>
        </div>
      )}
      
      {!isGameComplete && (
        <div className="absolute top-4 left-4 bg-white/90 rounded-full px-4 py-2 shadow-lg z-10">
          <div className="text-lg font-bold text-gray-800">
            Find: <span className="text-3xl text-red-500 ml-2">{currentLetter}</span>
          </div>
          <div className="text-sm text-gray-600 mt-1">
            {currentLetterIndex + 1} / {ALPHABET.length}
          </div>
        </div>
      )}
      
      {isGameComplete && (
        <div className="absolute inset-0 flex items-center justify-center z-10">
          <div className="bg-white/95 rounded-3xl p-8 shadow-2xl text-center max-w-md mx-4">
            <div className="text-8xl mb-4">🎉</div>
            <div className="text-3xl font-bold text-gray-800 mb-4">
              Amazing!
            </div>
            <div className="text-xl text-gray-600 mb-6">
              You completed the entire alphabet!
            </div>
            <button
              onClick={resetGame}
              className="px-8 py-3 bg-gradient-to-r from-green-400 to-blue-500 text-white font-bold rounded-full shadow-lg hover:scale-105 transition-transform"
            >
              Play Again
            </button>
          </div>
        </div>
      )}
      
      {!isGameComplete && !isErrorMode && letterPositions.map((pos) => {
        const isCompleted = completedLetters.includes(pos.letter);
        const isCurrentTarget = pos.letter === currentLetter;
        const color = ALPHABET_COLORS[pos.index];
        
        if (isCompleted) return null;
        
        return (
          <button
            key={pos.letter}
            onClick={() => handleLetterPress(pos.letter, pos.index)}
            className={`
              absolute font-black select-none
              hover:scale-110 transition-transform
              opacity-100
              ${isCurrentTarget ? 'z-20 ring-4 ring-yellow-400 ring-offset-2' : 'z-10'}
            `}
            style={{
              ...pos,
              background: `linear-gradient(135deg, ${color} 0%, ${color}dd 100%)`,
              boxShadow: `0 8px 0 ${color}66`,
              color: 'white',
              fontSize: `clamp(2rem, ${parseInt(pos.size)}vw, 4rem)`,
              textShadow: '2px 2px 4px rgba(0,0,0,0.2)',
              userSelect: 'none',
              WebkitUserSelect: 'none',
              touchAction: 'manipulation',
              borderRadius: '1rem',
              padding: '0.5rem',
            }}
          >
            {pos.letter}
          </button>
        );
      })}
      
      {!isGameComplete && !isErrorMode && wrongClicks > 0 && (
        <div className="absolute top-4 right-4 bg-white/90 rounded-full px-4 py-2 shadow-lg z-10">
          <div className="text-sm text-gray-600">
            Wrong taps: <span className="text-red-500 font-bold ml-1">{wrongClicks}</span>
          </div>
        </div>
      )}
    </div>
  );
}
