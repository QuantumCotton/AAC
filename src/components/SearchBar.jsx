import React from 'react';

export default function SearchBar({ value, onChange }) {
  return (
    <div className="mb-6 relative">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <span className="text-gray-400 text-xl">🔍</span>
      </div>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search for animals... (e.g., 'lion', 'cat')"
        className="w-full pl-10 pr-4 py-3 text-lg border-2 border-gray-300 rounded-full focus:outline-none focus:border-blue-500 transition-colors duration-200"
      />
      {value && (
        <button
          onClick={() => onChange('')}
          className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
        >
          ✕
        </button>
      )}
    </div>
  );
}
