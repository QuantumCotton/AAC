import React from 'react';
import { useAssets } from '../contexts/AssetContext';

export default function CategoryNav({ selectedCategory, onCategorySelect }) {
  const { isCategoryDownloaded } = useAssets();
  
  const categories = [
    { name: 'All', color: 'bg-gray-500' },
    { name: 'Farm', color: 'bg-green-500' },
    { name: 'Domestic', color: 'bg-yellow-500' },
    { name: 'Forest', color: 'bg-emerald-600' },
    { name: 'Jungle', color: 'bg-green-600' },
    { name: 'Nocturnal', color: 'bg-purple-600' },
    { name: 'Arctic', color: 'bg-blue-500' },
    { name: 'Shallow Water', color: 'bg-cyan-500' },
    { name: 'Coral Reef', color: 'bg-sky-500' },
    { name: 'Deep Sea', color: 'bg-slate-700' },
    { name: 'Ultra Deep Sea', color: 'bg-slate-900' }
  ];

  return (
    <nav className="flex flex-wrap gap-2 mb-6 p-4 bg-white rounded-xl shadow-sm">
      {categories.map(category => {
        const isDownloaded = category.name === 'All' || isCategoryDownloaded(category.name);
        const isSelected = selectedCategory === category.name;
        
        return (
          <button
            key={category.name}
            onClick={() => onCategorySelect(category.name)}
            disabled={!isDownloaded}
            className={`
              category-button px-4 py-2 rounded-full font-bold text-sm transition-all duration-200
              ${isSelected ? 'scale-105 ring-4 ring-offset-2' : 'hover:scale-105'}
              ${isDownloaded 
                ? `${category.color} text-white shadow-md` 
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }
            `}
          >
            {category.name}
            {!isDownloaded && category.name !== 'All' && ' 📥'}
          </button>
        );
      })}
    </nav>
  );
}
