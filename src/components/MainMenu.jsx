import React from 'react';

const books = [
  {
    id: 'animals',
    title: 'Animals',
    emoji: '🦁',
    description: 'Learn about amazing animals!',
    color: 'from-amber-400 to-orange-500',
    bgColor: 'bg-gradient-to-br from-amber-100 to-orange-200',
  },
  {
    id: 'asl',
    title: 'Liora AAC',
    emoji: '✨',
    description: 'Talk with Liora!',
    color: 'from-purple-400 to-pink-500',
    bgColor: 'bg-gradient-to-br from-purple-100 to-pink-200',
  },
  {
    id: 'places',
    title: 'Places',
    emoji: '🌍',
    description: 'Explore the world!',
    color: 'from-teal-400 to-cyan-500',
    bgColor: 'bg-gradient-to-br from-teal-100 to-cyan-200',
  },
];

export default function MainMenu({ onSelectBook }) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-200 via-sky-100 to-amber-100 flex flex-col items-center justify-center p-4">
      {/* Title */}
      <div className="text-center mb-8">
        <h1 className="text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 via-pink-500 to-orange-500 mb-2">
          Liora's Learning Library
        </h1>
        <p className="text-lg text-gray-600">Pick a book to explore!</p>
      </div>

      {/* Book Covers */}
      <div className="flex flex-wrap justify-center gap-6 max-w-4xl">
        {books.map((book) => (
          <button
            key={book.id}
            onClick={() => onSelectBook(book.id)}
            className={`
              group relative w-56 h-72 rounded-2xl shadow-xl 
              transform transition-all duration-300 
              hover:scale-105 hover:-rotate-2 hover:shadow-2xl
              active:scale-95
              ${book.bgColor}
              border-4 border-white/50
            `}
          >
            {/* Book Spine Effect */}
            <div className={`absolute left-0 top-0 bottom-0 w-4 bg-gradient-to-r ${book.color} rounded-l-2xl opacity-80`} />
            
            {/* Book Content */}
            <div className="relative h-full flex flex-col items-center justify-center p-6">
              {/* Emoji Icon */}
              <div className="text-7xl mb-4 transform group-hover:scale-110 transition-transform">
                {book.emoji}
              </div>
              
              {/* Title */}
              <h2 className={`text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r ${book.color} mb-2`}>
                {book.title}
              </h2>
              
              {/* Description */}
              <p className="text-sm text-gray-600 text-center">
                {book.description}
              </p>
              
              {/* Tap hint */}
              <div className="absolute bottom-4 text-xs text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
                Tap to open!
              </div>
            </div>

            {/* Decorative corner */}
            <div className="absolute top-2 right-2 w-8 h-8 bg-white/30 rounded-bl-xl" />
          </button>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-12 text-center text-gray-500 text-sm">
        <p>Made with ❤️ for Liora</p>
      </div>
    </div>
  );
}
