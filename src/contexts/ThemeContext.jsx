import React, { createContext, useContext, useState } from 'react';

const ThemeContext = createContext();

export const themes = {
  TOY: 'toy',
  REAL: 'real'
};

export function ThemeProvider({ children }) {
  const [currentTheme, setCurrentTheme] = useState(themes.TOY);

  const toggleTheme = () => {
    setCurrentTheme(prev => prev === themes.TOY ? themes.REAL : themes.TOY);
  };

  const setTheme = (theme) => {
    setCurrentTheme(theme);
  };

  const value = {
    currentTheme,
    toggleTheme,
    setTheme,
    isToyTheme: currentTheme === themes.TOY,
    isRealTheme: currentTheme === themes.REAL
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
