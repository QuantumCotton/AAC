import React from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { useFactLevel } from '../contexts/FactLevelContext';
import { useAssets } from '../contexts/AssetContext';
import { themes } from '../contexts/ThemeContext';
import { factLevels } from '../contexts/FactLevelContext';

const MODES = {
  KID: 'kid',
  EDUCATION: 'education'
};

export default function Header() {
  const { currentTheme, setTheme, isToyTheme } = useTheme();
  const { currentLevel, setFactLevel, isSimpleLevel } = useFactLevel();
  const { getDownloadProgress } = useAssets();

  const mode = isToyTheme && isSimpleLevel ? MODES.KID : MODES.EDUCATION;

  return (
    <header className={`theme-${currentTheme} shadow-lg`}>
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-3xl font-bold text-gray-800">
              🦁 Liora's Animal World
            </h1>
            <div className="hidden sm:block">
              <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500 transition-all duration-500"
                  style={{ width: `${getDownloadProgress()}%` }}
                />
              </div>
              <p className="text-xs text-gray-600 mt-1">
                {Math.round(getDownloadProgress())}% Downloaded
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => {
                if (mode === MODES.KID) {
                  // Switch to Education mode
                  setTheme(themes.REAL);
                  setFactLevel(factLevels.DETAILED);
                } else {
                  // Switch to Kid mode
                  setTheme(themes.TOY);
                  setFactLevel(factLevels.SIMPLE);
                }
              }}
              className="px-6 py-3 rounded-full font-bold text-white transition-all duration-200 hover:scale-105 shadow-md"
              style={{
                backgroundColor: mode === MODES.KID ? '#FF6B6B' : '#2563EB'
              }}
            >
              {mode === MODES.KID ? '🧸 Kid Mode' : '🎓 Education Mode'}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
