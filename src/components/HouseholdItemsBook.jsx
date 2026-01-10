import React, { useState, useEffect } from 'react';
import { useAudio } from '../contexts/AudioContext';
import householdItemsData from '../data/household_items.json';

export default function HouseholdItemsBook({ onBack }) {
  const { playSound } = useAudio();
  const [items, setItems] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    setItems(householdItemsData.items);
  }, []);

  const handleItemPress = (item) => {
    playSound(`/assets/audio/household/${item.id}.mp3`, item.name);
  };

  const filteredItems = selectedCategory === 'all' 
    ? items 
    : items.filter(item => item.category === selectedCategory);

  const categoryColors = {
    'all': 'from-amber-400 to-orange-500',
    'Kitchen': 'from-red-400 to-orange-500',
    'Bedroom': 'from-purple-400 to-pink-500',
    'Bathroom': 'from-blue-400 to-cyan-500',
    'Living Room': 'from-yellow-400 to-amber-500',
    'Vehicles': 'from-green-400 to-emerald-500',
    'Food': 'from-orange-400 to-red-500',
    'Clothing': 'from-pink-400 to-rose-500',
    'Tools': 'from-gray-400 to-slate-500',
    'Sports': 'from-cyan-400 to-blue-500',
    'Music': 'from-purple-400 to-fuchsia-500',
    "School": 'from-lime-400 to-green-500',
    'Nature': 'from-teal-400 to-sky-500',
    'Toys': 'from-rose-400 to-pink-500'
  };

  const getCategoryGradient = (category) => {
    const color = categoryColors[category] || categoryColors['all'];
    return `bg-gradient-to-br from-${color} 0%, ${color} 100%`;
  };

  const getTextColor = (category) => {
    const color = categoryColors[category] || categoryColors['all'];
    return category === 'all' ? 'text-white' : 'text-gray-800';
  };

  const getCardBg = (item, category) => {
    const isSelected = selectedCategory === category;
    return isSelected ? `bg-gradient-to-br from-${categoryColors[category]} 0%, ${categoryColors[category]} 100%` : '';
  };

  return (
    <div className="fixed inset-0 min-h-screen bg-gradient-to-br from-sky-200 via-slate-900 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-slate-900/50">
        <button
          onClick={onBack}
          className="p-2 rounded-full bg-white/90 shadow-lg hover:bg-white transition-colors"
        >
          <span className="text-xl">←</span>
        </button>
        <h1 className="text-2xl md:text-3xl font-black text-white drop-shadow-lg">
          🏠 Household Items
        </h1>
      </div>

      {/* Category Navigation */}
      <div className="px-4 py-3 bg-slate-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="flex gap-2 overflow-x-auto pb-2">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-4 py-2 rounded-full text-sm font-bold whitespace-nowrap transition-all ${
                selectedCategory === 'all' 
                  ? 'scale-110 text-white shadow-xl ring-2 ring-white' 
                  : 'bg-white/70 text-gray-700 hover:bg-gray-600'
              }`}
              style={{
                background: getCategoryGradient('all')
              }}
            >
              📦 All
            </button>
            {householdItemsData.categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                  selectedCategory === category
                    ? 'scale-105 text-white shadow-xl ring-2 ring-white'
                    : 'bg-white/70 text-gray-700 hover:bg-gray-600'
                }`}
                style={{
                  background: getCategoryGradient(category)
                }}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Items Grid - Clean full-size cards */}
      <div className="flex-1 px-4 py-6 bg-slate-800">
        {filteredItems.length === 0 && (
          <div className="flex flex-col items-center justify-center h-64 text-gray-500">
            <div className="text-6xl font-bold mb-4">No items in this category</div>
            <div className="text-gray-400">Select a category above</div>
          </div>
        )}

        <div className={`grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4`}>
          {filteredItems.map((item) => (
            <button
              key={item.id}
              onClick={() => handleItemPress(item)}
              className={`
                relative aspect-square rounded-2xl shadow-2xl 
                transition-all duration-200 
                hover:scale-105 hover:shadow-xl
                active:scale-95 active:shadow-sm
                bg-white overflow-hidden
              `}
              style={{
                background: getCardBg(item, selectedCategory)
              }}
            >
              {/* Card Content - Clean layout without ring binder holes */}
              <div className="flex flex-col items-center justify-center h-full p-4">
                {/* Emoji/Icon */}
                <div className="text-6xl mb-4">
                  {item.emoji}
                </div>

                {/* Item Name */}
                <div 
                  className={`text-2xl md:text-3xl lg:text-4xl font-bold ${
                    selectedCategory === item.category 
                      ? 'text-white drop-shadow-lg' 
                      : 'text-gray-800 drop-shadow-md'
                  }`}
                >
                  {item.name}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
