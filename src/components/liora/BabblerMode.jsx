import React, { useState, useMemo, useRef, useCallback, useEffect } from 'react';
import { useLiora } from '../../contexts/LioraContext';
import symbolsData from '../../data/liora_symbols_full.json';

function SymbolButton({ symbol, categoryColor, categoryId, size, onAdd }) {
  const { language } = useLiora();
  const [isPressed, setIsPressed] = useState(false);
  const [showRipple, setShowRipple] = useState(false);
  const [imgError, setImgError] = useState(false);
  
  const imagePath = `/assets/images/liora/${categoryId}/${symbol.id}.png`;

  useEffect(() => {
    setImgError(false);
  }, [imagePath]);

  const handlePress = () => {
    setIsPressed(true);
    setShowRipple(true);
    
    onAdd(symbol);
    
    setTimeout(() => {
      setIsPressed(false);
      setShowRipple(false);
    }, 150);
  };

  const buttonSize = size === '2x2' ? 'h-36' : 'h-24';
  const labelSize = size === '2x2' ? 'text-lg' : 'text-sm';
  const iconSize = size === '2x2' ? 'text-5xl' : 'text-3xl';

  return (
    <button
      onPointerDown={handlePress}
      onContextMenu={(e) => e.preventDefault()}
      className={`
        relative rounded-2xl border-4 overflow-hidden
        transition-all duration-100 shadow-lg
        ${isPressed ? 'scale-90 brightness-110' : 'hover:scale-105 active:scale-95'}
        ${buttonSize}
      `}
      style={{
        backgroundColor: categoryColor + '35',
        borderColor: categoryColor,
      }}
    >
      {showRipple && (
        <div 
          className="absolute inset-0 bg-white/50 animate-ping rounded-2xl"
          style={{ animationDuration: '200ms' }}
        />
      )}
      
      <div className="flex flex-col items-center justify-center h-full gap-1 p-2">
        {!imgError ? (
          <img 
            src={imagePath} 
            alt={symbol.text}
            className={`${size === '2x2' ? 'w-16 h-16' : 'w-10 h-10'} object-contain`}
            onError={() => setImgError(true)}
          />
        ) : (
          <span className={iconSize}>{symbol.icon || '💬'}</span>
        )}
        <span 
          className={`font-black text-gray-800 ${labelSize} px-1 leading-tight text-center`}
          style={{ textShadow: '0 1px 2px rgba(255,255,255,0.9)' }}
        >
          {language === 'tl' ? (symbol.text_tl || symbol.text) : symbol.text}
        </span>
      </div>
    </button>
  );
}

function MagicStrip({ sentence, language, onSpeak, onClear, onRemoveLast }) {
  if (sentence.length === 0) {
    return (
      <div className="bg-gradient-to-r from-purple-100 to-pink-100 border-b-4 border-purple-300 p-4">
        <div className="flex items-center justify-center gap-3 text-purple-400">
          <span className="text-2xl">✨</span>
          <span className="font-bold text-lg">Tap words to build a sentence...</span>
          <span className="text-2xl">✨</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-purple-100 via-pink-50 to-purple-100 border-b-4 border-purple-400 p-3 shadow-lg">
      <div className="flex items-center gap-3">
        <div className="flex-1 flex gap-2 overflow-x-auto py-1 px-2">
          {sentence.map((item, idx) => (
            <div
              key={idx}
              className="flex-shrink-0 bg-white rounded-xl px-4 py-2 flex items-center gap-2 border-3 border-purple-400 shadow-md transform hover:scale-105 transition-transform"
            >
              <span className="text-3xl">{item.icon}</span>
              <span className="font-black text-gray-800 text-lg">
                {language === 'tl' ? (item.text_tl || item.text) : item.text}
              </span>
            </div>
          ))}
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={onRemoveLast}
            className="w-14 h-14 rounded-xl bg-yellow-500 text-white text-2xl flex items-center justify-center shadow-lg hover:bg-yellow-600 active:scale-90 transition-all"
            title="Undo"
          >
            ⌫
          </button>
          <button
            onClick={onClear}
            className="w-14 h-14 rounded-xl bg-red-500 text-white text-2xl flex items-center justify-center shadow-lg hover:bg-red-600 active:scale-90 transition-all"
            title="Clear"
          >
            ✕
          </button>
          <button
            onClick={onSpeak}
            className="w-20 h-14 rounded-xl bg-green-500 text-white text-2xl flex items-center justify-center gap-1 shadow-lg hover:bg-green-600 active:scale-90 transition-all font-bold"
            title="Speak"
          >
            <span>▶</span>
            <span className="text-lg">PLAY</span>
          </button>
        </div>
      </div>
    </div>
  );
}

function CoreDock({ coreSymbols, language, onAdd }) {
  return (
    <div className="bg-gradient-to-t from-gray-800 to-gray-700 border-t-4 border-purple-500 p-3 shadow-2xl">
      <div className="flex justify-center gap-3 max-w-2xl mx-auto">
        {coreSymbols.map((symbol) => (
          <button
            key={symbol.id}
            onClick={() => onAdd(symbol)}
            className="flex-1 max-w-24 h-20 rounded-2xl bg-gradient-to-b from-white to-gray-100 flex flex-col items-center justify-center gap-1 
                       hover:from-purple-100 hover:to-purple-200 active:scale-90 
                       border-3 border-purple-400 shadow-lg transition-all"
          >
            <span className="text-3xl">{symbol.icon}</span>
            <span className="text-sm font-black text-gray-800">
              {language === 'tl' ? (symbol.text_tl || symbol.text) : symbol.text}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

export default function BabblerMode() {
  const { gridSize, language, speak } = useLiora();
  const [currentCategoryIdx, setCurrentCategoryIdx] = useState(0);
  const [sentence, setSentence] = useState([]);
  
  const category = symbolsData.categories[currentCategoryIdx];
  
  const coreSymbols = useMemo(() => {
    const core = symbolsData.categories.find(c => c.id === 'core');
    return core ? core.symbols.filter(s => 
      ['core_i', 'core_you', 'core_want', 'core_need', 'core_like', 'core_more'].includes(s.id)
    ) : [];
  }, []);
  
  const displaySymbols = useMemo(() => {
    const prioritySymbols = category.symbols.filter(s => s.priority === 1);
    const count = gridSize === '2x2' ? 4 : 9;
    return prioritySymbols.slice(0, count);
  }, [category, gridSize]);

  const gridCols = gridSize === '2x2' ? 'grid-cols-2' : 'grid-cols-3';

  const handleAddToSentence = useCallback((symbol) => {
    setSentence(prev => [...prev, symbol]);
  }, []);

  const handleRemoveLast = useCallback(() => {
    setSentence(prev => prev.slice(0, -1));
  }, []);

  const handleClear = useCallback(() => {
    setSentence([]);
  }, []);

  const handleSpeak = useCallback(() => {
    if (sentence.length === 0) return;
    
    const text = sentence
      .map(s => language === 'tl' ? (s.text_tl || s.text) : s.text)
      .join(' ');
    
    speak(text, language);
    
    setTimeout(() => {
      setSentence([]);
    }, 1500);
  }, [sentence, language, speak]);

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-purple-50 to-pink-50">
      {/* Magic Strip - The Brain */}
      <MagicStrip 
        sentence={sentence}
        language={language}
        onSpeak={handleSpeak}
        onClear={handleClear}
        onRemoveLast={handleRemoveLast}
      />

      {/* Category Rail */}
      <div className="bg-white/90 backdrop-blur border-b-2 border-gray-200 px-2 py-2">
        <div className="flex gap-2 overflow-x-auto pb-1">
          {symbolsData.categories.filter(c => c.id !== 'core').map((cat, idx) => (
            <button
              key={cat.id}
              onClick={() => setCurrentCategoryIdx(symbolsData.categories.indexOf(cat))}
              className={`
                flex-shrink-0 px-3 py-1.5 rounded-xl flex items-center gap-1.5
                transition-all font-bold text-sm
                ${symbolsData.categories[currentCategoryIdx]?.id === cat.id 
                  ? 'scale-105 shadow-lg ring-2 ring-white' 
                  : 'opacity-70 hover:opacity-100'}
              `}
              style={{ 
                backgroundColor: symbolsData.categories[currentCategoryIdx]?.id === cat.id ? cat.color : cat.color + '60',
                color: symbolsData.categories[currentCategoryIdx]?.id === cat.id ? 'white' : 'inherit'
              }}
            >
              <span className="text-lg">{cat.emoji}</span>
              <span className="hidden sm:inline text-xs">{cat.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid */}
      <div className="flex-1 p-3 overflow-auto">
        <div className={`grid ${gridCols} gap-3 max-w-xl mx-auto`}>
          {displaySymbols.map((symbol) => (
            <SymbolButton 
              key={symbol.id} 
              symbol={symbol} 
              categoryColor={category.color}
              categoryId={category.id}
              size={gridSize}
              onAdd={handleAddToSentence}
            />
          ))}
        </div>
      </div>

      {/* Core Dock - Persistent Footer */}
      <CoreDock 
        coreSymbols={coreSymbols}
        language={language}
        onAdd={handleAddToSentence}
      />
    </div>
  );
}
