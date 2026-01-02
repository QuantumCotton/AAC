import React from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { useAudio } from '../contexts/AudioContext';
import { useFactLevel } from '../contexts/FactLevelContext';
import { getAssetPaths } from '../utils/slugify';

export default function AnimalDetailModal({ animal, onClose }) {
  const { currentTheme } = useTheme();
  const { playSound, playClick } = useAudio();
  const { isSimpleLevel } = useFactLevel();

  const IconSpeaker = ({ className }) => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden="true">
      <path d="M11 5 6 9H2v6h4l5 4V5Z" />
      <path d="M15.5 8.5a4.5 4.5 0 0 1 0 7" />
      <path d="M19 6a8 8 0 0 1 0 12" />
    </svg>
  );

  const IconSparkle = ({ className }) => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden="true">
      <path d="M12 2l1.2 4.3L17.5 8l-4.3 1.2L12 13.5l-1.2-4.3L6.5 8l4.3-1.7L12 2Z" />
      <path d="M19 12l.7 2.6L22 16l-2.3.6L19 19l-.7-2.4L16 16l2.3-.6L19 12Z" />
      <path d="M4 13l.7 2.6L7 17l-2.3.6L4 20l-.7-2.4L1 17l2.3-.6L4 13Z" />
    </svg>
  );

  const IconBook = ({ className }) => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden="true">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z" />
    </svg>
  );

  if (!animal) return null;

  const paths = getAssetPaths(animal.id);
  const imagePath = currentTheme === 'toy' ? paths.toyImage : paths.realImage;

  const getFactText = () => {
    if (isSimpleLevel) {
      return animal.fact_level_1 || animal.fact || "I'm an amazing animal!";
    }
    if (animal.fact_level_2) {
      return `Size: ${animal.fact_level_2.size_details}\n\nUnique Fact: ${animal.fact_level_2.unique_fact}\n\nHabitat: ${animal.fact_level_2.habitat}`;
    }
    return animal.fact || "I'm an amazing animal!";
  };

  const simpleFactSrc = paths.factAudioSimple || paths.factAudioLegacy;
  const detailedFactSrc = paths.factAudioDetailed || paths.factAudioLegacy;

  const handleFact = () => {
    const src = isSimpleLevel ? simpleFactSrc : detailedFactSrc;
    playSound([src, paths.factAudioLegacy].filter(Boolean), animal.id);
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <div
        className="text-center p-6 bg-white rounded-3xl shadow-2xl max-w-md w-full mx-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="aspect-square rounded-xl overflow-hidden mb-4">
          <img src={imagePath} alt={animal.name} className="w-full h-full object-cover" />
        </div>
        <h2 className="text-2xl font-bold mb-2">{animal.name}</h2>
        <p className="text-gray-600 mb-4 whitespace-pre-line text-sm">{getFactText()}</p>
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => {
              playClick();
              playSound(paths.nameAudio, animal.id);
            }}
            className="flex-1 py-2 bg-blue-500 text-white rounded-full font-bold hover:bg-blue-600"
            aria-label="Play name"
          >
            <span className="inline-flex items-center justify-center gap-2">
              <IconSpeaker className="w-5 h-5" />
              <span>Name</span>
            </span>
          </button>
          <button
            onClick={() => {
              playClick();
              handleFact();
            }}
            className="flex-1 py-2 bg-green-500 text-white rounded-full font-bold hover:bg-green-600"
            aria-label="Play fact"
          >
            <span className="inline-flex items-center justify-center gap-2">
              {isSimpleLevel ? (
                <IconSparkle className="w-5 h-5" />
              ) : (
                <IconBook className="w-5 h-5" />
              )}
              <span>Fact</span>
            </span>
          </button>
        </div>
        <button
          onClick={onClose}
          className="w-full mt-2 py-2 bg-gray-200 text-gray-800 rounded-full font-bold hover:bg-gray-300"
        >
          Close
        </button>
      </div>
    </div>
  );
}
