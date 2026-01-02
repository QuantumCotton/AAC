import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useLiora } from '../../contexts/LioraContext';
import symbolsData from '../../data/liora_symbols_full.json';

// Liora's Library - Mini-book generator (simulated for now)
const SAMPLE_BOOKS = {
  'black holes': {
    title: 'Black Holes',
    emoji: '🕳️',
    pages: [
      { text: 'Black holes are regions in space where gravity is so strong that nothing can escape.', image: '🌌' },
      { text: 'They form when massive stars collapse at the end of their lives.', image: '⭐' },
      { text: 'The boundary around a black hole is called the event horizon.', image: '🔮' },
      { text: 'Time moves slower near a black hole due to its intense gravity.', image: '⏰' },
      { text: 'Scientists detect black holes by observing how they affect nearby stars and gas.', image: '🔭' },
    ],
  },
  'dinosaurs': {
    title: 'Dinosaurs',
    emoji: '🦕',
    pages: [
      { text: 'Dinosaurs lived on Earth for over 160 million years.', image: '🦖' },
      { text: 'The word dinosaur means "terrible lizard" in Greek.', image: '📚' },
      { text: 'Some dinosaurs were as small as chickens, while others were enormous!', image: '🐔' },
      { text: 'Many scientists believe birds evolved from small dinosaurs.', image: '🐦' },
      { text: 'Dinosaurs went extinct about 66 million years ago after an asteroid hit Earth.', image: '☄️' },
    ],
  },
  'ocean': {
    title: 'The Ocean',
    emoji: '🌊',
    pages: [
      { text: 'The ocean covers more than 70% of Earth\'s surface.', image: '🌍' },
      { text: 'The deepest part of the ocean is the Mariana Trench, over 36,000 feet deep.', image: '🏊' },
      { text: 'Coral reefs are home to millions of sea creatures.', image: '🐠' },
      { text: 'Whales are the largest animals ever to live on Earth.', image: '🐋' },
      { text: 'The ocean produces over half of the world\'s oxygen.', image: '💨' },
    ],
  },
  'space': {
    title: 'Outer Space',
    emoji: '🚀',
    pages: [
      { text: 'Space begins about 100 kilometers above Earth.', image: '🌍' },
      { text: 'There are more stars in the universe than grains of sand on Earth.', image: '⭐' },
      { text: 'Astronauts float in space because they are in free fall around Earth.', image: '👨‍🚀' },
      { text: 'The Moon is Earth\'s only natural satellite.', image: '🌙' },
      { text: 'Mars is called the Red Planet because of iron oxide on its surface.', image: '🔴' },
    ],
  },
};

function ChatMessage({ message, isUser, onSavePhrase }) {
  const { speak, language } = useLiora();
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-purple-500 text-white rounded-br-sm'
            : 'bg-white border-2 border-gray-200 rounded-bl-sm shadow'
        }`}
      >
        {!isUser && message.isBook ? (
          <MiniBook book={message.book} onSavePhrase={onSavePhrase} />
        ) : (
          <>
            <p className={isUser ? 'text-white' : 'text-gray-800'}>{message.text}</p>
            {!isUser && (
              <div className="flex gap-2 mt-2">
                <button
                  onClick={() => speak(message.text, language)}
                  className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded-lg flex items-center gap-1"
                >
                  🔊 Read
                </button>
                <button
                  onClick={() => onSavePhrase({ text: message.text })}
                  className="text-xs bg-purple-100 hover:bg-purple-200 px-2 py-1 rounded-lg flex items-center gap-1"
                >
                  💾 Save
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function MiniBook({ book, onSavePhrase }) {
  const { speak, language } = useLiora();
  const [currentPage, setCurrentPage] = useState(0);
  
  const page = book.pages[currentPage];
  
  return (
    <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-4 border-2 border-amber-200 min-w-[280px]">
      {/* Book Header */}
      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-amber-200">
        <span className="text-3xl">{book.emoji}</span>
        <h3 className="font-bold text-gray-800">{book.title}</h3>
      </div>
      
      {/* Page Content */}
      <div className="text-center py-4">
        <span className="text-6xl mb-4 block">{page.image}</span>
        <p className="text-gray-700 leading-relaxed">{page.text}</p>
      </div>
      
      {/* Page Actions */}
      <div className="flex gap-2 mb-3">
        <button
          onClick={() => speak(page.text, language)}
          className="flex-1 py-2 bg-green-500 text-white rounded-lg text-sm font-bold hover:bg-green-600 flex items-center justify-center gap-1"
        >
          🔊 Read Aloud
        </button>
        <button
          onClick={() => onSavePhrase({ text: page.text, icon: page.image })}
          className="py-2 px-3 bg-purple-500 text-white rounded-lg text-sm font-bold hover:bg-purple-600"
          title="Keep This Fact"
        >
          💾
        </button>
      </div>
      
      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setCurrentPage(p => Math.max(0, p - 1))}
          disabled={currentPage === 0}
          className="px-3 py-1 bg-amber-200 rounded-lg text-amber-800 font-bold disabled:opacity-30"
        >
          ← Back
        </button>
        <span className="text-sm text-gray-500">
          {currentPage + 1} / {book.pages.length}
        </span>
        <button
          onClick={() => setCurrentPage(p => Math.min(book.pages.length - 1, p + 1))}
          disabled={currentPage === book.pages.length - 1}
          className="px-3 py-1 bg-amber-200 rounded-lg text-amber-800 font-bold disabled:opacity-30"
        >
          Next →
        </button>
      </div>
    </div>
  );
}

function SavedPhrasesPanel({ phrases, onUse, onRemove, onClose }) {
  const { speak, language } = useLiora();
  
  return (
    <div className="absolute right-0 top-0 bottom-0 w-72 bg-white shadow-2xl border-l-2 border-gray-200 flex flex-col z-20">
      <div className="p-3 border-b border-gray-200 flex items-center justify-between bg-purple-50">
        <h3 className="font-bold text-purple-800 flex items-center gap-2">
          <span>📚</span> Saved Phrases
        </h3>
        <button onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2">
        {phrases.length === 0 ? (
          <p className="text-center text-gray-400 text-sm p-4">
            Drag sentences here from Liora's Library to save them!
          </p>
        ) : (
          <div className="space-y-2">
            {phrases.map((phrase, idx) => (
              <div
                key={idx}
                className="bg-purple-50 rounded-xl p-3 border border-purple-200"
              >
                <p className="text-sm text-gray-700 mb-2">{phrase.text}</p>
                <div className="flex gap-1">
                  <button
                    onClick={() => speak(phrase.text, language)}
                    className="flex-1 py-1 bg-green-500 text-white rounded text-xs font-bold"
                  >
                    🔊
                  </button>
                  <button
                    onClick={() => onUse(phrase)}
                    className="flex-1 py-1 bg-purple-500 text-white rounded text-xs font-bold"
                  >
                    Use
                  </button>
                  <button
                    onClick={() => onRemove(idx)}
                    className="py-1 px-2 bg-red-400 text-white rounded text-xs font-bold"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function DiscoveryMode() {
  const { speak, language, savePhrase, savedPhrases, removeSavedPhrase, addToSentence, sentenceStrip, speakSentence, clearSentence } = useLiora();
  const [messages, setMessages] = useState([
    { id: 1, text: "Hi! I'm Liora 🌟 Ask me about anything you want to learn about!", isUser: false }
  ]);
  const [inputText, setInputText] = useState('');
  const [showSavedPhrases, setShowSavedPhrases] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = useCallback(() => {
    if (!inputText.trim()) return;
    
    const userMessage = { id: Date.now(), text: inputText, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    
    // Check if we have a book for this topic
    const topic = inputText.toLowerCase().trim();
    const bookKeys = Object.keys(SAMPLE_BOOKS);
    const matchedKey = bookKeys.find(key => topic.includes(key) || key.includes(topic));
    
    setTimeout(() => {
      if (matchedKey) {
        const book = SAMPLE_BOOKS[matchedKey];
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          isBook: true,
          book: book,
          isUser: false,
        }]);
      } else {
        // Default response for unknown topics
        const suggestions = bookKeys.slice(0, 3).join(', ');
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          text: `That's a great topic! I'm still learning about that. Try asking me about: ${suggestions}, or type any question!`,
          isUser: false,
        }]);
      }
    }, 500);
    
    setInputText('');
  }, [inputText]);

  const handleSavePhrase = useCallback((phrase) => {
    savePhrase(phrase);
  }, [savePhrase]);

  const handleUsePhrase = useCallback((phrase) => {
    addToSentence({ text: phrase.text, icon: phrase.icon || '💬' });
  }, [addToSentence]);

  // Quick topic suggestions
  const topicSuggestions = [
    { emoji: '🕳️', topic: 'Black Holes' },
    { emoji: '🦕', topic: 'Dinosaurs' },
    { emoji: '🌊', topic: 'Ocean' },
    { emoji: '🚀', topic: 'Space' },
  ];

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-indigo-50 to-purple-50 relative">
      {/* Header with sentence strip */}
      {sentenceStrip.length > 0 && (
        <div className="bg-white/90 backdrop-blur border-b-2 border-purple-200 p-2">
          <div className="flex items-center gap-2">
            <div className="flex-1 flex gap-1 overflow-x-auto">
              {sentenceStrip.map((item, idx) => (
                <span key={idx} className="bg-purple-100 rounded-lg px-2 py-1 text-sm flex items-center gap-1">
                  {item.icon && <span>{item.icon}</span>}
                  <span className="font-medium">{item.text}</span>
                </span>
              ))}
            </div>
            <button onClick={speakSentence} className="p-2 bg-green-500 text-white rounded-lg">🔊</button>
            <button onClick={clearSentence} className="p-2 bg-red-400 text-white rounded-lg">✕</button>
          </div>
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            isUser={message.isUser}
            onSavePhrase={handleSavePhrase}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Topics */}
      <div className="px-4 pb-2">
        <div className="flex gap-2 overflow-x-auto">
          {topicSuggestions.map((item) => (
            <button
              key={item.topic}
              onClick={() => setInputText(item.topic)}
              className="flex-shrink-0 bg-white rounded-full px-3 py-1.5 flex items-center gap-1.5 shadow border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-all text-sm"
            >
              <span>{item.emoji}</span>
              <span className="font-medium text-gray-700">{item.topic}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t-2 border-gray-200">
        <div className="flex gap-2 max-w-2xl mx-auto">
          <button
            onClick={() => setShowSavedPhrases(!showSavedPhrases)}
            className={`p-3 rounded-xl border-2 transition-all ${
              showSavedPhrases ? 'bg-purple-500 text-white border-purple-500' : 'bg-gray-100 border-gray-200 hover:bg-gray-200'
            }`}
          >
            📚
          </button>
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask Liora anything..."
            className="flex-1 px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-400 focus:outline-none text-lg"
          />
          <button
            onClick={handleSend}
            disabled={!inputText.trim()}
            className="px-6 py-3 bg-purple-500 text-white rounded-xl font-bold hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send 🚀
          </button>
        </div>
      </div>

      {/* Saved Phrases Panel */}
      {showSavedPhrases && (
        <SavedPhrasesPanel
          phrases={savedPhrases}
          onUse={handleUsePhrase}
          onRemove={removeSavedPhrase}
          onClose={() => setShowSavedPhrases(false)}
        />
      )}
    </div>
  );
}
