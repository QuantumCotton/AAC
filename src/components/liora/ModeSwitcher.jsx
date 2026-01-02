import React, { useState } from 'react';
import { useLiora } from '../../contexts/LioraContext';

export default function ModeSwitcher({ onClose }) {
  const { userMode, changeMode, verifyPin, isParentMode, setIsParentMode, gridSize, changeGridSize, updatePin } = useLiora();
  const [pinInput, setPinInput] = useState('');
  const [showPinEntry, setShowPinEntry] = useState(!isParentMode);
  const [pinError, setPinError] = useState(false);
  const [newPin, setNewPin] = useState('');
  const [showPinChange, setShowPinChange] = useState(false);

  const handlePinSubmit = () => {
    if (verifyPin(pinInput)) {
      setIsParentMode(true);
      setShowPinEntry(false);
      setPinError(false);
    } else {
      setPinError(true);
      setPinInput('');
    }
  };

  const handlePinChange = () => {
    if (newPin.length >= 4) {
      updatePin(newPin);
      setShowPinChange(false);
      setNewPin('');
    }
  };

  const modes = [
    {
      id: 'babbler',
      name: 'The Babbler',
      age: '13 months+',
      emoji: '👶',
      color: '#FF6B6B',
      description: 'Big buttons, instant speech. Perfect for cause & effect learning.',
    },
    {
      id: 'bridge',
      name: 'The Bridge',
      age: '2.5 years+',
      emoji: '🌉',
      color: '#4ECDC4',
      description: 'Keyboard with predictions. Great for emerging readers.',
    },
    {
      id: 'discovery',
      name: 'The Discovery',
      age: '6 years+',
      emoji: '🚀',
      color: '#9B59B6',
      description: 'Chat interface with Liora\'s Library for exploration.',
    },
  ];

  if (showPinEntry) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <div className="bg-white rounded-3xl p-8 max-w-sm w-full mx-4 shadow-2xl">
          <div className="text-center mb-6">
            <span className="text-5xl mb-4 block">🔒</span>
            <h2 className="text-2xl font-bold text-gray-800">Parent Access</h2>
            <p className="text-gray-500 text-sm mt-2">Enter PIN to change settings</p>
          </div>
          
          <div className="flex justify-center gap-2 mb-6">
            {[0, 1, 2, 3].map(i => (
              <div
                key={i}
                className={`w-14 h-14 rounded-xl border-3 flex items-center justify-center text-2xl font-bold
                  ${pinInput.length > i ? 'bg-purple-100 border-purple-400' : 'bg-gray-100 border-gray-300'}
                  ${pinError ? 'border-red-400 bg-red-50' : ''}
                `}
              >
                {pinInput.length > i ? '●' : ''}
              </div>
            ))}
          </div>
          
          {pinError && (
            <p className="text-red-500 text-center text-sm mb-4">Incorrect PIN. Try again.</p>
          )}
          
          <div className="grid grid-cols-3 gap-2 mb-4">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, '', 0, '⌫'].map((num, i) => (
              <button
                key={i}
                onClick={() => {
                  if (num === '⌫') {
                    setPinInput(prev => prev.slice(0, -1));
                    setPinError(false);
                  } else if (num !== '' && pinInput.length < 4) {
                    setPinInput(prev => prev + num);
                    setPinError(false);
                  }
                }}
                className={`h-14 rounded-xl text-xl font-bold transition-all
                  ${num === '' ? 'invisible' : 'bg-gray-100 hover:bg-gray-200 active:scale-95'}
                `}
              >
                {num}
              </button>
            ))}
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 py-3 rounded-xl bg-gray-200 text-gray-700 font-bold hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              onClick={handlePinSubmit}
              disabled={pinInput.length !== 4}
              className="flex-1 py-3 rounded-xl bg-purple-500 text-white font-bold hover:bg-purple-600 disabled:opacity-50"
            >
              Unlock
            </button>
          </div>
          
          <p className="text-center text-xs text-gray-400 mt-4">Default PIN: 1234</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-3xl p-6 max-w-lg w-full shadow-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <span>⚙️</span> Settings
          </h2>
          <button
            onClick={onClose}
            className="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-xl"
          >
            ✕
          </button>
        </div>

        {/* Mode Selection */}
        <div className="mb-6">
          <h3 className="text-lg font-bold text-gray-700 mb-3">Choose Mode</h3>
          <div className="space-y-3">
            {modes.map(mode => (
              <button
                key={mode.id}
                onClick={() => changeMode(mode.id)}
                className={`w-full p-4 rounded-2xl border-3 transition-all text-left
                  ${userMode === mode.id 
                    ? 'border-purple-400 bg-purple-50 ring-2 ring-purple-200' 
                    : 'border-gray-200 hover:border-gray-300 bg-white'}
                `}
              >
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{mode.emoji}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-gray-800">{mode.name}</span>
                      <span className="text-xs bg-gray-100 px-2 py-0.5 rounded-full text-gray-500">{mode.age}</span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">{mode.description}</p>
                  </div>
                  {userMode === mode.id && <span className="text-2xl">✓</span>}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Grid Size (Babbler mode only) */}
        {userMode === 'babbler' && (
          <div className="mb-6">
            <h3 className="text-lg font-bold text-gray-700 mb-3">Grid Size</h3>
            <div className="flex gap-3">
              {['2x2', '3x3'].map(size => (
                <button
                  key={size}
                  onClick={() => changeGridSize(size)}
                  className={`flex-1 py-3 px-4 rounded-xl border-2 font-bold transition-all
                    ${gridSize === size 
                      ? 'border-purple-400 bg-purple-100 text-purple-700' 
                      : 'border-gray-200 bg-gray-50 text-gray-600 hover:border-gray-300'}
                  `}
                >
                  {size}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Change PIN */}
        <div className="mb-6">
          <h3 className="text-lg font-bold text-gray-700 mb-3">Security</h3>
          {showPinChange ? (
            <div className="bg-gray-50 p-4 rounded-xl">
              <input
                type="password"
                value={newPin}
                onChange={(e) => setNewPin(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="Enter new PIN (4-6 digits)"
                className="w-full p-3 rounded-lg border-2 border-gray-200 text-center text-xl tracking-widest mb-3"
              />
              <div className="flex gap-2">
                <button
                  onClick={() => setShowPinChange(false)}
                  className="flex-1 py-2 rounded-lg bg-gray-200 text-gray-700 font-bold"
                >
                  Cancel
                </button>
                <button
                  onClick={handlePinChange}
                  disabled={newPin.length < 4}
                  className="flex-1 py-2 rounded-lg bg-purple-500 text-white font-bold disabled:opacity-50"
                >
                  Save
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setShowPinChange(true)}
              className="w-full py-3 rounded-xl bg-gray-100 text-gray-700 font-bold hover:bg-gray-200"
            >
              🔑 Change PIN
            </button>
          )}
        </div>

        {/* Lock & Close */}
        <div className="flex gap-3">
          <button
            onClick={() => {
              setIsParentMode(false);
              onClose();
            }}
            className="flex-1 py-3 rounded-xl bg-gray-200 text-gray-700 font-bold hover:bg-gray-300"
          >
            🔒 Lock & Close
          </button>
          <button
            onClick={onClose}
            className="flex-1 py-3 rounded-xl bg-purple-500 text-white font-bold hover:bg-purple-600"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
