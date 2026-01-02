import React, { createContext, useContext, useState, useEffect } from 'react';

const FactLevelContext = createContext();

export const factLevels = {
  SIMPLE: 'simple',
  DETAILED: 'detailed'
};

export function FactLevelProvider({ children }) {
  const [currentLevel, setCurrentLevel] = useState(() => {
    // Load from localStorage on initial render
    const saved = localStorage.getItem('liora-fact-level');
    return saved || factLevels.SIMPLE;
  });

  // Save to localStorage when level changes
  useEffect(() => {
    localStorage.setItem('liora-fact-level', currentLevel);
  }, [currentLevel]);

  const toggleFactLevel = () => {
    setCurrentLevel(prev => prev === factLevels.SIMPLE ? factLevels.DETAILED : factLevels.SIMPLE);
  };

  const setFactLevel = (level) => {
    setCurrentLevel(level);
  };

  const value = {
    currentLevel,
    toggleFactLevel,
    setFactLevel,
    isSimpleLevel: currentLevel === factLevels.SIMPLE,
    isDetailedLevel: currentLevel === factLevels.DETAILED
  };

  return (
    <FactLevelContext.Provider value={value}>
      {children}
    </FactLevelContext.Provider>
  );
}

export function useFactLevel() {
  const context = useContext(FactLevelContext);
  if (!context) {
    throw new Error('useFactLevel must be used within a FactLevelProvider');
  }
  return context;
}
