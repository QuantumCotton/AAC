import React, { useState, useEffect } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { useAudio } from '../contexts/AudioContext';
import { useAssets } from '../contexts/AssetContext';
import { useFactLevel } from '../contexts/FactLevelContext';
import { getAssetPaths } from '../utils/slugify';
import loadAnimalsWithFacts from '../data/loadAnimals.js';

export default function AnimalGrid({ category, searchQuery }) {
  const { currentTheme } = useTheme();
  const { playSound, activeAnimalId } = useAudio();
  const { isCategoryDownloaded } = useAssets();
  const { isSimpleLevel } = useFactLevel();
  const [filteredAnimals, setFilteredAnimals] = useState([]);
  const [selectedAnimal, setSelectedAnimal] = useState(null);

  useEffect(() => {
    let filtered = loadAnimalsWithFacts;

    // Filter by category
    if (category !== 'All') {
      filtered = filtered.filter(animal => animal.category === category);
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(animal => 
        animal.name.toLowerCase().includes(query) ||
        animal.category.toLowerCase().includes(query)
      );
    }

    setFilteredAnimals(filtered);
  }, [category, searchQuery]);

  const handleAnimalClick = (animal) => {
    // Check if category is downloaded
    if (!isCategoryDownloaded(animal.category)) {
      return;
    }

    setSelectedAnimal(animal);
    const paths = getAssetPaths(animal.id);
    const audioPath = currentTheme === 'toy' ? paths.nameAudio : paths.nameAudio;
    playSound(audioPath, animal.id);
  };

  const handleLongPress = (animal) => {
    // Play fact audio on long press or detail view
    const paths = getAssetPaths(animal.id);
    playSound(paths.factAudio, animal.id);
  };

  const getFactText = (animal) => {
    if (isSimpleLevel) {
      return animal.fact_level_1 || animal.fact || "I'm an amazing animal!";
    } else {
      if (animal.fact_level_2) {
        return `Size: ${animal.fact_level_2.size_details}\n\nUnique Fact: ${animal.fact_level_2.unique_fact}\n\nHabitat: ${animal.fact_level_2.habitat}`;
      }
      return animal.fact || "I'm an amazing animal!";
    }
  };

  const getImagePath = (animal) => {
    const paths = getAssetPaths(animal.id);
    return currentTheme === 'toy' ? paths.toyImage : paths.realImage;
  };

  if (filteredAnimals.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-2xl text-gray-600">No animals found!</p>
        <p className="text-gray-500 mt-2">Try a different search or category</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
      {filteredAnimals.map(animal => {
        const isActive = activeAnimalId === animal.id;
        const isDownloaded = isCategoryDownloaded(animal.category);
        
        return (
          <div
            key={animal.id}
            className={`
              animal-card relative
              ${isActive ? 'active' : ''}
              ${!isDownloaded ? 'opacity-50 cursor-not-allowed' : ''}
            `}
            onClick={() => handleAnimalClick(animal)}
            onContextMenu={(e) => {
              e.preventDefault();
              if (isDownloaded) handleLongPress(animal);
            }}
          >
            <div className="aspect-square rounded-lg overflow-hidden bg-gray-100 mb-2">
              <img
                src={getImagePath(animal)}
                alt={animal.name}
                className="w-full h-full object-cover"
                loading="lazy"
                onError={(e) => {
                  e.target.src = '/assets/placeholder.webp';
                }}
              />
            </div>
            <h3 className="font-bold text-center text-sm md:text-base">
              {animal.name}
            </h3>
            {!isDownloaded && (
              <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-90 rounded-2xl">
                <span className="text-2xl">📥</span>
              </div>
            )}
            {isActive && (
              <div className="absolute top-2 right-2">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              </div>
            )}
          </div>
        );
      })}
      
      {/* Detail Modal */}
      {selectedAnimal && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedAnimal(null)}
        >
          <div 
            className="text-center p-8 bg-white rounded-3xl shadow-2xl max-w-md w-full mx-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="aspect-square rounded-xl overflow-hidden mb-4">
              <img
                src={getImagePath(selectedAnimal)}
                alt={selectedAnimal.name}
                className="w-full h-full object-cover"
              />
            </div>
            <h2 className="text-2xl font-bold mb-2">{selectedAnimal.name}</h2>
            <p className="text-gray-600 mb-4 whitespace-pre-line text-sm">
              {getFactText(selectedAnimal)}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  const paths = getAssetPaths(selectedAnimal.id);
                  playSound(paths.nameAudio, selectedAnimal.id);
                }}
                className="flex-1 py-2 bg-blue-500 text-white rounded-full font-bold hover:bg-blue-600"
              >
                🔊 Name
              </button>
              <button
                onClick={() => {
                  const paths = getAssetPaths(selectedAnimal.id);
                  playSound(paths.factAudio, selectedAnimal.id);
                }}
                className="flex-1 py-2 bg-green-500 text-white rounded-full font-bold hover:bg-green-600"
              >
                📢 Fact
              </button>
            </div>
            <button
              onClick={() => setSelectedAnimal(null)}
              className="w-full mt-2 py-2 bg-gray-200 text-gray-800 rounded-full font-bold hover:bg-gray-300"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
