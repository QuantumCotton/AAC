import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { openDB } from 'idb';
import animalsData from '../data/animals.json';

const AssetContext = createContext();

// Priority order for downloading categories
const CATEGORY_PRIORITY = [
  'Farm',      // Most familiar to kids
  'Domestic',  // Pets
  'Forest',    // Common animals
  'Shallow Water', // Beach animals
  'Coral Reef',   // Colorful and engaging
  'Jungle',       // Exciting animals
  'Nocturnal',    // Mysterious
  'Arctic',       // Unique
  'Deep Sea',     // Fascinating
  'Ultra Deep Sea' // Most exotic
];

export function AssetProvider({ children }) {
  const [downloadedCategories, setDownloadedCategories] = useState(new Set());
  const [downloadingCategory, setDownloadingCategory] = useState(null);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [isInitialDownload, setIsInitialDownload] = useState(true);
  const [currentVersion, setCurrentVersion] = useState(null);

  const manifestRef = useRef(null);

  // Initialize IndexedDB
  useEffect(() => {
    initializeDB();
    checkDownloadStatus();
  }, []);

  const initializeDB = async () => {
    const db = await openDB('LioraAssets', 1, {
      upgrade(db) {
        db.createObjectStore('categories', { keyPath: 'name' });
        db.createObjectStore('animals', { keyPath: 'id' });
        db.createObjectStore('metadata', { keyPath: 'key' });
      }
    });
    return db;
  };

  const checkDownloadStatus = async () => {
    const db = await initializeDB();
    
    // Check for version updates
    try {
      const response = await fetch('/assets/manifest.json', { cache: 'no-store' });
      if (!response.ok) throw new Error('Failed to load manifest');
      const manifest = await response.json();
      const remoteVersion = manifest.version;
      
      const storedVersion = await db.get('metadata', 'version');
      
      if (storedVersion && storedVersion.value !== remoteVersion) {
        // Version mismatch - clear all downloaded data
        console.log('Version update detected, clearing cache...');
        await clearAllData(db);
        await db.put('metadata', { key: 'version', value: remoteVersion });
        setCurrentVersion(remoteVersion);
        return; // Will trigger fresh download
      }
      
      if (!storedVersion) {
        await db.put('metadata', { key: 'version', value: remoteVersion });
      }
      
      setCurrentVersion(remoteVersion);
    } catch (error) {
      console.error('Failed to check version:', error);
    }
    
    const categories = await db.getAll('categories');
    const downloaded = new Set(categories.map(c => c.name));
    setDownloadedCategories(downloaded);
    
    if (downloaded.size >= CATEGORY_PRIORITY.length) {
      setIsInitialDownload(false);
    } else {
      setIsInitialDownload(true);
    }
  };

  const loadManifest = async () => {
    if (manifestRef.current) return manifestRef.current;
    const response = await fetch('/assets/manifest.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('Failed to load manifest');
    const manifest = await response.json();
    manifestRef.current = manifest;
    return manifest;
  };

  const prefetchUrls = async (urls, { concurrency = 6, onProgress } = {}) => {
    if (!urls || urls.length === 0) return;

    const cache = await caches.open('liora-assets');
    let nextIndex = 0;
    let done = 0;
    let lastUiUpdate = 0;

    const worker = async () => {
      while (true) {
        const idx = nextIndex;
        nextIndex += 1;
        if (idx >= urls.length) return;

        const url = urls[idx];
        try {
          const existing = await cache.match(url);
          if (!existing) {
            const response = await fetch(url);
            if (response.ok) {
              await cache.put(url, response.clone());
            }
          }
        } catch (error) {
          // Ignore individual asset failures
        } finally {
          done += 1;
          if (typeof onProgress === 'function') {
            const now = performance.now();
            if (now - lastUiUpdate > 150 || done === urls.length) {
              lastUiUpdate = now;
              try {
                onProgress(done);
              } catch {}
            }
          }
        }
      }
    };

    const workers = Array.from({ length: Math.min(concurrency, urls.length) }, () => worker());
    await Promise.all(workers);
  };

  const clearAllData = async (db) => {
    // Clear IndexedDB
    await db.clear('categories');
    await db.clear('animals');
    
    // Clear caches
    const cacheNames = await caches.keys();
    for (const cacheName of cacheNames) {
      if (cacheName.includes('liora') || cacheName.includes('workbox')) {
        await caches.delete(cacheName);
      }
    }
    
    // Reset state
    setDownloadedCategories(new Set());
    setIsInitialDownload(true);
  };

  const downloadCategory = async (categoryName) => {
    if (downloadedCategories.has(categoryName)) return;

    // In dev/StrictMode the startup effect can run twice; also state might lag behind IDB.
    // Check IDB first so we don't re-download and then fail on writes.
    try {
      const db = await initializeDB();
      const existing = await db.get('categories', categoryName);
      if (existing) {
        setDownloadedCategories(prev => new Set([...prev, categoryName]));
        if (isInitialDownload) setIsInitialDownload(false);
        return;
      }
    } catch (e) {
      // Ignore and proceed with download.
    }
    
    setDownloadingCategory(categoryName);
    setDownloadProgress(0);

    try {
      const animals = animalsData.filter(a => a.category === categoryName);
      const manifest = await loadManifest().catch(() => null);

      const urls = [];
      for (const animal of animals) {
        const id = animal.id;
        const entry = manifest?.assets?.[id];
        if (entry?.files) {
          for (const relPath of Object.values(entry.files)) {
            if (relPath) urls.push(`/assets/${relPath}`);
          }
        } else {
          urls.push(`/assets/images/toy_mode/${id}.webp`);
          urls.push(`/assets/images/real_mode/${id}.webp`);
          urls.push(`/assets/audio/names/${id}_name.mp3`);
          urls.push(`/assets/audio/facts/${id}_fact.mp3`);
        }
      }

      const total = urls.length;
      await prefetchUrls(urls, {
        concurrency: 6,
        onProgress: (done) => {
          if (total > 0) setDownloadProgress((done / total) * 100);
        }
      });

      // Mark category as downloaded
      const db = await initializeDB();
      await db.put('categories', {
        name: categoryName,
        downloadedAt: Date.now(),
        animalCount: total
      });

      setDownloadedCategories(prev => new Set([...prev, categoryName]));

      const nextDownloadedSize = downloadedCategories.size + 1;
      if (nextDownloadedSize >= CATEGORY_PRIORITY.length) {
        setIsInitialDownload(false);
      }
    } catch (error) {
      console.error(`Failed to download ${categoryName}:`, error);
    } finally {
      setDownloadingCategory(null);
      setDownloadProgress(0);
    }
  };

  const downloadAllCategories = async () => {
    for (const category of CATEGORY_PRIORITY) {
      if (!downloadedCategories.has(category)) {
        await downloadCategory(category);
        // Small delay between categories
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }

    setIsInitialDownload(false);
  };

  const getDownloadProgress = () => {
    const totalCategories = CATEGORY_PRIORITY.length;
    const downloaded = downloadedCategories.size;
    return (downloaded / totalCategories) * 100;
  };

  const isCategoryDownloaded = (categoryName) => {
    // Only return true for dev mode if explicitly testing without downloads
    // For normal operation, always respect the download state
    return downloadedCategories.has(categoryName);
  };

  const value = {
    downloadedCategories,
    downloadingCategory,
    downloadProgress,
    isInitialDownload,
    downloadCategory,
    downloadAllCategories,
    getDownloadProgress,
    isCategoryDownloaded
  };

  return (
    <AssetContext.Provider value={value}>
      {children}
    </AssetContext.Provider>
  );
}

export function useAssets() {
  const context = useContext(AssetContext);
  if (!context) {
    throw new Error('useAssets must be used within an AssetProvider');
  }
  return context;
}
