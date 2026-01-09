import React, { useState, useEffect } from 'react';
import { useAudio } from '../contexts/AudioContext';
import householdItemsData from '../data/household_items.json';

export default function HouseholdItemsBook({ onBack }) {
  const { playSound, playClick } = useAudio();
  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    setItems(householdItemsData.items);
    setCategories(['all', ...householdItemsData.categories]);
  }, []);

  const filteredItems = selectedCategory === 'all' 
    ? items 
    : items.filter(item => item.category === selectedCategory);

  const handleItemPress = (item) => {
    playSound(`/assets/audio/household/${item.id}.mp3`, item.name);
  };

  const getCategoryColor = (category) => {
    const colors = {
      'all': '#9333ea',
      'Kitchen': '#f59e0b',
      'Bedroom': '#8b5cf6',
      'Bathroom': '#06b6d4',
      'Living Room': '#10b981',
      'Vehicles': '#ef4444',
      'Food': '#22c55e',
      'Clothing': '#ec4899',
      'Tools': '#f97316',
      'Nature': '#14b8a6',
      'Sports': '#6366f1',
      'Music': '#a855f7',
      'School': '#0ea5e9'
    };
    return colors[category] || '#6b7280';
  };

  return (
    <div className="fixed inset-0 flex flex-col overflow-hidden"
         style={{ background: 'linear-gradient(135deg, #fef3c7 0%, #60a5fa 50%, #a78bfa 100%)' }}>
      
      {/* Top bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-black/20 shrink-0">
        <button
          onClick={onBack}
          className="p-2 rounded-full bg-white/90 shadow-lg hover:bg-white transition-colors"
        >
          <span className="text-xl">🏠</span>
        </button>
        
        <h1 className="text-xl font-black text-white drop-shadow-lg">
          🏠 Household Items 🏠
        </h1>
        
        <div className="w-10"></div>
      </div>

      {/* Category navigation */}
      <div className="px-4 py-3 bg-white/10 overflow-x-auto">
        <div className="flex gap-2 min-w-max">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => {
                setSelectedCategory(category);
                playClick();
              }}
              className={`px-4 py-2 rounded-full text-sm font-bold shadow transition-all whitespace-nowrap ${
                selectedCategory === category
                  ? 'scale-110 text-white'
                  : 'bg-white/70 text-gray-700 hover:scale-105'
              }`}
              style={
                selectedCategory === category
                  ? { background: getCategoryColor(category) }
                  : {}
              }
            >
              {category === 'all' ? '📦 All' : category}
            </button>
          ))}
        </div>
      </div>

      {/* Items grid - ring binder style */}
      <div className="flex-1 overflow-auto p-4">
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-4">
          {filteredItems.map((item) => (
            <button
              key={item.id}
              onClick={() => handleItemPress(item)}
              className="relative aspect-square rounded-2xl shadow-lg 
                         transition-all duration-150
                         hover:scale-105 hover:shadow-xl
                         active:scale-95 active:shadow-sm
                         bg-white/95 overflow-hidden"
              style={{
                boxShadow: '0 8px 0 rgba(0,0,0,0.2)',
              }}
            >
              {/* Ring binder holes */}
              <div className="absolute top-2 left-1/2 -translate-x-1/2 flex gap-1">
                <div className="w-2 h-2 rounded-full bg-gray-400/50"></div>
                <div className="w-2 h-2 rounded-full bg-gray-400/50"></div>
                <div className="w-2 h-2 rounded-full bg-gray-400/50"></div>
              </div>

              {/* Item content */}
              <div className="flex flex-col items-center justify-center h-full p-2 pt-6">
                {/* Emoji/icon placeholder */}
                <div 
                  className="text-4xl sm:text-5xl md:text-6xl mb-2"
                  style={{ textShadow: '2px 2px 4px rgba(0,0,0,0.1)' }}
                >
                  {item.emoji || '📦'}
                </div>
                
                {/* Item name */}
                <div 
                  className="text-xs sm:text-sm font-bold text-gray-800 text-center leading-tight"
                  style={{ textShadow: '1px 1px 2px rgba(255,255,255,0.8)' }}
                >
                  {item.name}
                </div>
              </div>
            </button>
          ))}
        </div>
        
        {filteredItems.length === 0 && (
          <div className="flex items-center justify-center h-full text-white text-xl font-bold">
            No items in this category
          </div>
        )}
      </div>
    </div>
  );
}
