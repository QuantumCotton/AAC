import React, { useState } from 'react';
import { LioraProvider, useLiora } from '../../contexts/LioraContext';
import ModeSwitcher from './ModeSwitcher';
import BabblerMode from './BabblerMode';
import BridgeMode from './BridgeMode';
import DiscoveryMode from './DiscoveryMode';

function LioraHeader({ onBack, onSettings }) {
  const { userMode, language, toggleLanguage, isPracticeMode, setIsPracticeMode } = useLiora();
  
  const modeInfo = {
    babbler: { name: 'Babbler', emoji: '👶', color: '#FF6B6B' },
    bridge: { name: 'Bridge', emoji: '🌉', color: '#4ECDC4' },
    discovery: { name: 'Discovery', emoji: '🚀', color: '#9B59B6' },
  };
  
  const current = modeInfo[userMode];
  
  return (
    <div 
      className="sticky top-0 z-30 text-white shadow-lg"
      style={{ background: `linear-gradient(90deg, ${current.color}, #8B5CF6)` }}
    >
      <div className="flex items-center gap-3 p-3">
        <button 
          onClick={onBack} 
          className="p-2 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
        >
          <span className="text-xl">🏠</span>
        </button>
        
        <div className="flex items-center gap-2 flex-1">
          <span className="text-3xl">✨</span>
          <div>
            <h1 className="text-xl font-bold">Liora</h1>
            <p className="text-xs text-white/80 flex items-center gap-1">
              <span>{current.emoji}</span>
              <span>{current.name} Mode</span>
            </p>
          </div>
        </div>
        
        {/* Language Toggle */}
        <button
          onClick={toggleLanguage}
          className="px-3 py-1.5 rounded-full bg-white/20 hover:bg-white/30 text-sm font-bold flex items-center gap-1"
        >
          {language === 'en' ? '🇺🇸 EN' : '🇵🇭 TL'}
        </button>
        
        {/* Practice Mode Toggle */}
        <button
          onClick={() => setIsPracticeMode(!isPracticeMode)}
          className={`px-3 py-1.5 rounded-full text-sm font-bold flex items-center gap-1 transition-all
            ${isPracticeMode ? 'bg-yellow-400 text-yellow-900' : 'bg-white/20 hover:bg-white/30'}
          `}
          title={isPracticeMode ? 'Practice Mode (Liora sprite active)' : 'Talker Mode'}
        >
          {isPracticeMode ? '🎮' : '💬'}
        </button>
        
        {/* Settings */}
        <button
          onClick={onSettings}
          className="p-2 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
        >
          <span className="text-xl">⚙️</span>
        </button>
      </div>
    </div>
  );
}

function LioraContent() {
  const { userMode, isPracticeMode } = useLiora();
  
  // Render the appropriate mode
  switch (userMode) {
    case 'babbler':
      return <BabblerMode />;
    case 'bridge':
      return <BridgeMode />;
    case 'discovery':
      return <DiscoveryMode />;
    default:
      return <BabblerMode />;
  }
}

function LioraSprite({ visible }) {
  if (!visible) return null;
  
  return (
    <div className="fixed bottom-24 right-4 z-40 animate-bounce">
      <div className="relative">
        <div className="w-20 h-20 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full shadow-xl flex items-center justify-center border-4 border-white">
          <span className="text-4xl">🧚</span>
        </div>
        <div className="absolute -top-12 -left-4 bg-white rounded-xl px-3 py-2 shadow-lg border-2 border-purple-200 max-w-[150px]">
          <p className="text-xs text-gray-700 font-medium">
            Can you tell me what you want? 💬
          </p>
          <div className="absolute bottom-0 right-4 transform translate-y-1/2 rotate-45 w-3 h-3 bg-white border-r-2 border-b-2 border-purple-200"></div>
        </div>
      </div>
    </div>
  );
}

function LioraApp({ onBack }) {
  const [showSettings, setShowSettings] = useState(false);
  const { isPracticeMode } = useLiora();
  
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <LioraHeader 
        onBack={onBack} 
        onSettings={() => setShowSettings(true)} 
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <LioraContent />
      </div>
      
      {/* Liora Sprite for Practice Mode */}
      <LioraSprite visible={isPracticeMode} />
      
      {/* Settings Modal */}
      {showSettings && (
        <ModeSwitcher onClose={() => setShowSettings(false)} />
      )}
    </div>
  );
}

export default function LioraBook({ onBack }) {
  return (
    <LioraProvider>
      <LioraApp onBack={onBack} />
    </LioraProvider>
  );
}
