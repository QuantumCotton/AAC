import React, { useMemo } from 'react';
import { habitats } from '../data/habitats';
import { useAssets } from '../contexts/AssetContext';

export default function HabitatRail({ selectedHabitat, onSelectHabitat }) {
  const { isCategoryDownloaded } = useAssets();

  const currentIndex = useMemo(() => {
    return habitats.findIndex((h) => h.name === selectedHabitat);
  }, [selectedHabitat]);

  // Habitats before current (show on left like read pages)
  const passedHabitats = useMemo(() => {
    return habitats.slice(0, currentIndex);
  }, [currentIndex]);

  // Current and upcoming habitats (show on right like unread pages)
  const upcomingHabitats = useMemo(() => {
    return habitats.slice(currentIndex);
  }, [currentIndex]);

  const TabButton = ({ h, isSelected, side }) => {
    const isDownloaded = isCategoryDownloaded(h.name);
    return (
      <button
        key={h.name}
        type="button"
        onClick={() => onSelectHabitat(h.name)}
        className={
          `group flex items-center gap-1 px-2 py-2 transition-all duration-200 text-white shadow-md ` +
          (side === 'left' ? 'rounded-r-xl ' : 'rounded-l-xl ') +
          (isSelected ? 'ring-2 ring-offset-1 scale-105 ' : 'opacity-80 hover:opacity-100 hover:scale-105 ') +
          (isDownloaded ? h.color : 'bg-gray-400')
        }
        title={h.name}
      >
        <span className="text-base">{h.emoji}</span>
        {isSelected && (
          <span className="text-xs font-bold whitespace-nowrap max-w-[60px] truncate">
            {h.name}
          </span>
        )}
      </button>
    );
  };

  return (
    <>
      {/* Left side - passed habitats (like read book pages) */}
      {passedHabitats.length > 0 && (
        <div className="fixed left-0 top-1/2 -translate-y-1/2 z-40 flex flex-col gap-1 pl-0">
          {passedHabitats.slice(-5).map((h) => (
            <TabButton key={h.name} h={h} isSelected={false} side="left" />
          ))}
        </div>
      )}

      {/* Right side - current and upcoming habitats (like unread book pages) */}
      <div className="fixed right-0 top-1/2 -translate-y-1/2 z-40 flex flex-col gap-1 pr-0">
        {upcomingHabitats.slice(0, 6).map((h) => (
          <TabButton key={h.name} h={h} isSelected={h.name === selectedHabitat} side="right" />
        ))}
      </div>
    </>
  );
}
