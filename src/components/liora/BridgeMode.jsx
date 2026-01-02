import React, { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import { useLiora } from '../../contexts/LioraContext';
import symbolsData from '../../data/liora_symbols_full.json';

function VisualKey({ letter, hint, onClick, isActive }) {
  return (
    <button
      onClick={() => onClick(letter)}
      className={`
        relative h-12 sm:h-14 rounded-xl font-bold text-lg sm:text-xl
        transition-all duration-100 border-2
        ${isActive 
          ? 'bg-purple-500 text-white border-purple-600 scale-105' 
          : 'bg-white hover:bg-gray-50 border-gray-300 active:scale-95'}
      `}
    >
      <span>{letter}</span>
      {hint && (
        <span className="absolute -top-1 -right-1 text-xs opacity-70">{hint}</span>
      )}
    </button>
  );
}

function PredictionBar({ predictions, onSelect, language }) {
  if (!predictions || predictions.length === 0) {
    return (
      <div className="h-20 bg-gradient-to-r from-purple-100 to-pink-100 flex items-center justify-center rounded-2xl border-2 border-purple-200">
        <span className="text-gray-400 text-sm">Start typing to see predictions...</span>
      </div>
    );
  }

  return (
    <div className="h-20 bg-gradient-to-r from-purple-100 to-pink-100 flex items-center gap-2 px-3 rounded-2xl border-2 border-purple-200 overflow-x-auto">
      {predictions.map((pred, idx) => (
        <button
          key={idx}
          onClick={() => onSelect(pred)}
          className="flex-shrink-0 bg-white rounded-xl px-4 py-2 flex items-center gap-2 shadow-md hover:shadow-lg hover:scale-105 transition-all border-2 border-purple-300 active:scale-95"
        >
          <span className="text-2xl">{pred.icon}</span>
          <span className="font-bold text-gray-800">{pred.word}</span>
        </button>
      ))}
    </div>
  );
}

function MessageWindow({ sentence, language, onSpeak, onClear, onBackspace }) {
  const displayText = sentence
    .map(s => language === 'tl' ? (s.text_tl || s.text || s.word) : (s.text || s.word))
    .join(' ');

  return (
    <div className="bg-white rounded-2xl border-3 border-gray-200 shadow-lg p-4 min-h-32">
      <div className="flex items-start gap-3">
        <div className="flex-1">
          {sentence.length === 0 ? (
            <p className="text-gray-400 text-lg">Tap keys or symbols to build a sentence...</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {sentence.map((item, idx) => (
                <div
                  key={idx}
                  className="bg-purple-100 rounded-lg px-3 py-1.5 flex items-center gap-2 border border-purple-300"
                >
                  {item.icon && <span className="text-xl">{item.icon}</span>}
                  <span className="font-semibold text-gray-800">
                    {language === 'tl' ? (item.text_tl || item.text || item.word) : (item.text || item.word)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="flex flex-col gap-2">
          <button
            onClick={onSpeak}
            disabled={sentence.length === 0}
            className="w-12 h-12 rounded-xl bg-green-500 text-white text-xl flex items-center justify-center shadow hover:bg-green-600 disabled:opacity-50 active:scale-95"
          >
            🔊
          </button>
          <button
            onClick={onBackspace}
            disabled={sentence.length === 0}
            className="w-12 h-12 rounded-xl bg-yellow-500 text-white text-xl flex items-center justify-center shadow hover:bg-yellow-600 disabled:opacity-50 active:scale-95"
          >
            ⌫
          </button>
          <button
            onClick={onClear}
            disabled={sentence.length === 0}
            className="w-12 h-12 rounded-xl bg-red-400 text-white text-xl flex items-center justify-center shadow hover:bg-red-500 disabled:opacity-50 active:scale-95"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
}

export default function BridgeMode() {
  const { language, toggleLanguage, speak, addToSentence, sentenceStrip, clearSentence, removeLastFromSentence, speakSentence } = useLiora();
  const [typedText, setTypedText] = useState('');
  const [currentCategoryIdx, setCurrentCategoryIdx] = useState(0);
  
  const category = symbolsData.categories[currentCategoryIdx];
  const letterHints = symbolsData.letterHints;
  
  // Get predictions based on typed text
  const predictions = useMemo(() => {
    if (!typedText) return [];
    const firstLetter = typedText[0].toUpperCase();
    const basePredictions = symbolsData.predictions[firstLetter] || [];
    
    // Filter predictions that start with typed text
    return basePredictions.filter(p => 
      p.word.toLowerCase().startsWith(typedText.toLowerCase())
    );
  }, [typedText]);

  const handleKeyPress = useCallback((letter) => {
    setTypedText(prev => prev + letter);
  }, []);

  const handleBackspace = useCallback(() => {
    if (typedText.length > 0) {
      setTypedText(prev => prev.slice(0, -1));
    } else {
      removeLastFromSentence();
    }
  }, [typedText, removeLastFromSentence]);

  const handlePredictionSelect = useCallback((prediction) => {
    addToSentence({
      text: prediction.word,
      text_tl: prediction.word, // Would need translation mapping
      icon: prediction.icon,
    });
    setTypedText('');
  }, [addToSentence]);

  const handleSymbolSelect = useCallback((symbol) => {
    addToSentence(symbol);
    speak(language === 'tl' ? (symbol.text_tl || symbol.text) : symbol.text, language);
  }, [addToSentence, speak, language]);

  const handleSpeak = useCallback(() => {
    speakSentence();
  }, [speakSentence]);

  const handleClear = useCallback(() => {
    clearSentence();
    setTypedText('');
  }, [clearSentence]);

  // Keyboard layout
  const keyboardRows = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
  ];

  // Word order based on language (Tagalog is VSO)
  const isTagalog = language === 'tl';

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-blue-50 to-purple-50">
      {/* Top 40%: Message Window */}
      <div className="flex-[4] p-3 flex flex-col gap-2">
        {/* Language Toggle */}
        <div className="flex items-center justify-between mb-1">
          <button
            onClick={toggleLanguage}
            className={`px-4 py-2 rounded-xl font-bold text-sm flex items-center gap-2 transition-all
              ${isTagalog ? 'bg-yellow-400 text-yellow-900' : 'bg-blue-500 text-white'}
            `}
          >
            <span>{isTagalog ? '🇵🇭' : '🇺🇸'}</span>
            <span>{isTagalog ? 'Tagalog' : 'English'}</span>
          </button>
          
          {isTagalog && (
            <div className="text-xs bg-yellow-100 px-3 py-1 rounded-full text-yellow-800 font-medium">
              Word Order: Verb → Subject → Object
            </div>
          )}
        </div>
        
        <MessageWindow
          sentence={sentenceStrip}
          language={language}
          onSpeak={handleSpeak}
          onClear={handleClear}
          onBackspace={handleBackspace}
        />
        
        {/* Quick Symbol Categories */}
        <div className="flex gap-2 overflow-x-auto py-1">
          {symbolsData.categories.slice(0, 5).map((cat, idx) => (
            <button
              key={cat.id}
              onClick={() => setCurrentCategoryIdx(idx)}
              className={`flex-shrink-0 px-3 py-1.5 rounded-lg flex items-center gap-1.5 text-sm font-bold transition-all
                ${idx === currentCategoryIdx ? 'ring-2 ring-white shadow-lg scale-105' : 'opacity-70'}
              `}
              style={{ 
                backgroundColor: cat.color,
                color: 'white'
              }}
            >
              <span>{cat.emoji}</span>
              <span className="hidden sm:inline">{cat.name}</span>
            </button>
          ))}
        </div>
        
        {/* Quick Symbols Row */}
        <div className="flex gap-2 overflow-x-auto py-1">
          {category.symbols.slice(0, 8).map((symbol) => (
            <button
              key={symbol.id}
              onClick={() => handleSymbolSelect(symbol)}
              className="flex-shrink-0 bg-white rounded-xl px-3 py-2 flex items-center gap-2 shadow border-2 hover:scale-105 transition-all active:scale-95"
              style={{ borderColor: category.color }}
            >
              <span className="text-xl">{symbol.icon}</span>
              <span className="font-bold text-sm text-gray-700">
                {language === 'tl' ? (symbol.text_tl || symbol.text) : symbol.text}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Middle 20%: Prediction Bar */}
      <div className="flex-[2] px-3 py-2">
        <PredictionBar
          predictions={predictions}
          onSelect={handlePredictionSelect}
          language={language}
        />
        
        {/* Current typed text */}
        {typedText && (
          <div className="mt-2 text-center">
            <span className="bg-white px-4 py-1 rounded-full text-lg font-bold text-purple-600 shadow">
              {typedText}_
            </span>
          </div>
        )}
      </div>

      {/* Bottom 40%: QWERTY Keyboard */}
      <div className="flex-[4] bg-gray-100 p-3 rounded-t-3xl shadow-inner">
        <div className="max-w-xl mx-auto space-y-2">
          {keyboardRows.map((row, rowIdx) => (
            <div 
              key={rowIdx} 
              className="flex gap-1 justify-center"
              style={{ paddingLeft: rowIdx === 1 ? '1rem' : rowIdx === 2 ? '2rem' : 0 }}
            >
              {row.map((letter) => (
                <div key={letter} className="flex-1 max-w-12">
                  <VisualKey
                    letter={letter}
                    hint={letterHints[letter]}
                    onClick={handleKeyPress}
                    isActive={typedText.toUpperCase().includes(letter)}
                  />
                </div>
              ))}
            </div>
          ))}
          
          {/* Bottom row with space and backspace */}
          <div className="flex gap-2 justify-center mt-2">
            <button
              onClick={handleBackspace}
              className="px-6 py-3 rounded-xl bg-yellow-500 text-white font-bold text-lg hover:bg-yellow-600 active:scale-95"
            >
              ⌫ Back
            </button>
            <button
              onClick={() => setTypedText(prev => prev + ' ')}
              className="flex-1 max-w-xs py-3 rounded-xl bg-white border-2 border-gray-300 font-bold text-gray-600 hover:bg-gray-50 active:scale-95"
            >
              Space
            </button>
            <button
              onClick={handleSpeak}
              className="px-6 py-3 rounded-xl bg-green-500 text-white font-bold text-lg hover:bg-green-600 active:scale-95"
            >
              🔊 Speak
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
