import React, { useState, useEffect } from 'react';
import { useAudio } from '../contexts/AudioContext';
import householdItemsData from '../data/household_items.json';

export default function HouseholdItemsBook({ onBack, onSelectBook }) {
  const { playSound } = useAudio();
  const [currentPage, setCurrentPage] = useState(1); // Left page shows items 1-6, Right page shows 7-12
  
  // Calculate pagination
  const itemsPerPage = 6; // 6 items per page
  const totalPages = Math.ceil(householdItemsData.items.length / itemsPerPage);
  
  // Get current page's items
  const getPageItems = (page) => {
    const startIndex = (page - 1) * itemsPerPage;
    return householdItemsData.items.slice(startIndex, startIndex + itemsPerPage);
  };

  // Navigate to previous page
  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
      playSound('/assets/audio/alphabet/letter_back_name.mp3');
    }
  };

  // Navigate to next page
  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
      playSound('/assets/audio/alphabet/letter_back_name.mp3');
    }
  };

  // Handle item press
  const handleItemPress = (item) => {
    playSound(`/assets/audio/household/${item.id}.mp3`, item.name);
  };

  // Determine which side's items are being displayed
  const leftPageItems = currentPage;
  const rightPageItems = currentPage > 1 ? currentPage : null; // Page 2+ displays items 7-12
  const leftPageIndex = currentPage;
  const rightPageIndex = currentPage + 1;

  return (
    <div className="fixed inset-0 min-h-screen bg-gradient-to-br from-sky-200 via-blue-100 to-slate-900 flex flex-col">
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

      {/* Page Navigation - Book Spine Style */}
      <div className="px-4 py-2 bg-slate-900/50">
        <div className="flex items-center justify-center gap-4">
          {/* Page Indicator - Left Side */}
          <div className="flex-1">
            <button
              onClick={() => {
                if (currentPage > 1) {
                  handlePrevPage();
                }
              }}
              className={`p-2 rounded-full transition-all ${
                currentPage === leftPageIndex 
                  ? 'bg-white text-slate-900 shadow-lg ring-2 ring-white' 
                  : 'bg-slate-800 text-slate-500 hover:bg-slate-700 hover:shadow-lg'
              }`}
            >
              <span className="text-4xl">←</span>
            </button>
            <div className="flex items-center gap-2">
              <div className={`text-2xl font-bold transition-all ${
                currentPage === leftPageIndex ? 'text-white' : 'text-slate-300'
              }`}>
                {leftPageIndex}
              </div>
              <span className="text-lg text-slate-500">items</span>
            </div>
          </div>

          {/* Page Indicator - Right Side */}
          <div className="flex-1">
            <button
              onClick={() => {
                if (currentPage < totalPages) {
                  handleNextPage();
                }
              }}
              className={`p-2 rounded-full transition-all ${
                currentPage === rightPageIndex 
                  ? 'bg-white text-slate-900 shadow-lg ring-2 ring-white' 
                  : 'bg-slate-800 text-slate-500 hover:bg-slate-700 hover:shadow-lg'
              }`}
            >
              <span className="text-4xl">→</span>
            </button>
            <div className="flex items-center gap-2">
              <div className={`text-2xl font-bold transition-all ${
                currentPage === rightPageIndex ? 'text-white' : 'text-slate-300'
              }`}>
                {currentPage < totalPages ? rightPageIndex : currentPage}
              </div>
              <span className="text-lg text-slate-500">items</span>
            </div>
          </div>

          {/* Divider - Book Spine */}
          <div className="w-16 h-1 bg-white/20"></div>
        </div>
      </div>

      {/* Pages Container - Two Page Spread */}
      <div className="flex-1 px-4 py-6 bg-slate-800 flex gap-4">
        {/* Left Page */}
        {leftPageIndex && (
          <div className="flex-1">
            <div className="w-full max-w-md mx-auto">
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-3 gap-4">
                {getPageItems(leftPageIndex).map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleItemPress(item)}
                    className="relative aspect-[4/3] rounded-2xl shadow-2xl transition-all duration-200 hover:scale-105 hover:shadow-xl active:scale-95 active:shadow-sm bg-white overflow-hidden border-2 border-gray-200"
                  >
                    <div className="flex flex-col items-center justify-center h-full p-4">
                      {/* Emoji/Icon */}
                      <div className="text-6xl mb-4">
                        {item.emoji}
                      </div>

                      {/* Item Name */}
                      <div className="text-3xl md:text-4xl lg:text-5xl font-bold text-slate-800 leading-tight text-center">
                        {item.name}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Right Page */}
        {rightPageIndex && (
          <div className="flex-1">
            <div className="w-full max-w-md mx-auto">
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-3 gap-4">
                {getPageItems(rightPageIndex).map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleItemPress(item)}
                    className="relative aspect-[4/3] rounded-2xl shadow-2xl transition-all duration-200 hover:scale-105 hover:shadow-xl active:scale-95 active:shadow-sm bg-white overflow-hidden border-2 border-gray-200"
                  >
                    <div className="flex flex-col items-center justify-center h-full p-4">
                      {/* Emoji/Icon */}
                      <div className="text-6xl mb-4">
                        {item.emoji}
                      </div>

                      {/* Item Name */}
                      <div className="text-3xl md:text-4xl lg:text-5xl font-bold text-slate-800 leading-tight text-center">
                        {item.name}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
