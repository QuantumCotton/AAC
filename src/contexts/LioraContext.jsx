import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react';

const LioraContext = createContext();

const DEFAULT_PIN = '1234';

export function LioraProvider({ children }) {
  // User modes: 'babbler' (13mo), 'bridge' (2.5yo), 'discovery' (6yo)
  const [userMode, setUserMode] = useState(() => {
    return localStorage.getItem('liora-mode') || 'babbler';
  });
  
  // Language: 'en' or 'tl' (Tagalog)
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('liora-lang') || 'en';
  });
  
  // Sentence strip for building sentences
  const [sentenceStrip, setSentenceStrip] = useState([]);
  
  // Saved phrases for Discovery mode
  const [savedPhrases, setSavedPhrases] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('liora-saved-phrases') || '[]');
    } catch {
      return [];
    }
  });
  
  // Parent settings lock
  const [isParentMode, setIsParentMode] = useState(false);
  const [parentPin, setParentPin] = useState(() => {
    return localStorage.getItem('liora-pin') || DEFAULT_PIN;
  });
  
  // Grid size for Babbler mode
  const [gridSize, setGridSize] = useState(() => {
    return localStorage.getItem('liora-grid') || '3x3';
  });
  
  // Practice mode toggle
  const [isPracticeMode, setIsPracticeMode] = useState(false);
  
  // TTS cache reference (uses IndexedDB via external util)
  const ttsCacheRef = useRef(new Map());
  
  // Speech synthesis
  const speak = useCallback((text, lang = 'en') => {
    if (!('speechSynthesis' in window)) return;
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.85;
      utterance.pitch = 1.1;
      // Try to use appropriate voice
      const voices = window.speechSynthesis.getVoices();
      if (lang === 'tl') {
        const filipinoVoice = voices.find(v => v.lang.includes('fil') || v.lang.includes('tl'));
        if (filipinoVoice) utterance.voice = filipinoVoice;
      } else {
        const englishVoice = voices.find(v => v.lang.includes('en-US'));
        if (englishVoice) utterance.voice = englishVoice;
      }
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.error('Speech error:', e);
    }
  }, []);
  
  // Add symbol to sentence strip
  const addToSentence = useCallback((symbol) => {
    setSentenceStrip(prev => [...prev, symbol]);
  }, []);
  
  // Remove last item from sentence
  const removeLastFromSentence = useCallback(() => {
    setSentenceStrip(prev => prev.slice(0, -1));
  }, []);
  
  // Clear sentence strip
  const clearSentence = useCallback(() => {
    setSentenceStrip([]);
  }, []);
  
  // Speak the entire sentence
  const speakSentence = useCallback(() => {
    const text = sentenceStrip
      .map(s => language === 'tl' ? (s.text_tl || s.text) : s.text)
      .join(' ');
    if (text) speak(text, language);
  }, [sentenceStrip, language, speak]);
  
  // Save phrase (Discovery mode)
  const savePhrase = useCallback((phrase) => {
    setSavedPhrases(prev => {
      const updated = [...prev, { ...phrase, savedAt: Date.now() }];
      localStorage.setItem('liora-saved-phrases', JSON.stringify(updated));
      return updated;
    });
  }, []);
  
  // Remove saved phrase
  const removeSavedPhrase = useCallback((index) => {
    setSavedPhrases(prev => {
      const updated = prev.filter((_, i) => i !== index);
      localStorage.setItem('liora-saved-phrases', JSON.stringify(updated));
      return updated;
    });
  }, []);
  
  // Verify parent PIN
  const verifyPin = useCallback((inputPin) => {
    return inputPin === parentPin;
  }, [parentPin]);
  
  // Update parent PIN
  const updatePin = useCallback((newPin) => {
    setParentPin(newPin);
    localStorage.setItem('liora-pin', newPin);
  }, []);
  
  // Toggle language
  const toggleLanguage = useCallback(() => {
    setLanguage(prev => {
      const next = prev === 'en' ? 'tl' : 'en';
      localStorage.setItem('liora-lang', next);
      return next;
    });
  }, []);
  
  // Change user mode
  const changeMode = useCallback((mode) => {
    setUserMode(mode);
    localStorage.setItem('liora-mode', mode);
    clearSentence();
  }, [clearSentence]);
  
  // Change grid size
  const changeGridSize = useCallback((size) => {
    setGridSize(size);
    localStorage.setItem('liora-grid', size);
  }, []);
  
  // Load voices when available
  useEffect(() => {
    const loadVoices = () => {
      window.speechSynthesis.getVoices();
    };
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }, []);
  
  const value = {
    // State
    userMode,
    language,
    sentenceStrip,
    savedPhrases,
    isParentMode,
    gridSize,
    isPracticeMode,
    
    // Actions
    speak,
    addToSentence,
    removeLastFromSentence,
    clearSentence,
    speakSentence,
    savePhrase,
    removeSavedPhrase,
    verifyPin,
    updatePin,
    toggleLanguage,
    changeMode,
    changeGridSize,
    setIsParentMode,
    setIsPracticeMode,
  };
  
  return (
    <LioraContext.Provider value={value}>
      {children}
    </LioraContext.Provider>
  );
}

export function useLiora() {
  const context = useContext(LioraContext);
  if (!context) {
    throw new Error('useLiora must be used within a LioraProvider');
  }
  return context;
}
