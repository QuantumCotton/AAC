import React, { useMemo, useState, useCallback } from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { AudioProvider, useAudio } from './contexts/AudioContext';
import { AssetProvider } from './contexts/AssetContext';
import { FactLevelProvider } from './contexts/FactLevelContext';
import { AccessibilityProvider } from './contexts/AccessibilityContext';
import Header from './components/Header';
import HabitatRail from './components/HabitatRail';
import HabitatScene from './components/HabitatScene';
import SyncScreen from './components/SyncScreen';
import MainMenu from './components/MainMenu';
import LioraBook from './components/liora/LioraBook';
import PlacesBook from './components/PlacesBook';
import LeapFrogBook from './components/LeapFrogBook';
import AlphabetBook from './components/AlphabetBook';
import HouseholdItemsBook from './components/HouseholdItemsBook';
import { habitats } from './data/habitats';
import { useAssets } from './contexts/AssetContext';

function App() {
  const [currentBook, setCurrentBook] = useState(null); // null = main menu
  const [selectedHabitat, setSelectedHabitat] = useState(habitats[0]?.name || 'Forest');

  const [skipDownload, setSkipDownload] = useState(() => {
    return localStorage.getItem('liora-skip-download') === '1';
  });

  const handleSkip = () => {
    localStorage.setItem('liora-skip-download', '1');
    setSkipDownload(true);
  };

  const handleResetSkip = () => {
    localStorage.removeItem('liora-skip-download');
    setSkipDownload(false);
  };

  const handleSelectBook = (bookId) => {
    setCurrentBook(bookId);
  };

  const handleBackToMenu = () => {
    setCurrentBook(null);
  };

  // Animals Book Content - Now using LeapFrog style!
  const AnimalsBook = () => {
    const { getDownloadProgress, isInitialDownload } = useAssets();
    const overall = useMemo(() => getDownloadProgress(), [getDownloadProgress]);
    const showSync = !skipDownload && isInitialDownload && overall < 100;

    if (showSync) {
      return <SyncScreen onSkip={handleSkip} />;
    }

    // Use the new LeapFrog-style book interface
    return <LeapFrogBook onBack={handleBackToMenu} />;
  };

  const AppContent = () => {
    // Route to the appropriate book
    if (currentBook === null) {
      return <MainMenu onSelectBook={handleSelectBook} />;
    }
    
    if (currentBook === 'animals') {
      return <AnimalsBook />;
    }
    
    if (currentBook === 'asl') {
      return <LioraBook onBack={handleBackToMenu} />;
    }
    
    if (currentBook === 'places') {
      return <PlacesBook onBack={handleBackToMenu} />;
    }
    
    if (currentBook === 'alphabet') {
      return <AlphabetBook onBack={handleBackToMenu} />;
    }
    
    if (currentBook === 'household') {
      return <HouseholdItemsBook onBack={handleBackToMenu} />;
    }

    return <MainMenu onSelectBook={handleSelectBook} />;
  };

  return (
    <AccessibilityProvider>
      <ThemeProvider>
        <AudioProvider>
          <AssetProvider>
            <FactLevelProvider>
              <AppContent />
            </FactLevelProvider>
          </AssetProvider>
        </AudioProvider>
      </ThemeProvider>
    </AccessibilityProvider>
  );
}

export default App;
