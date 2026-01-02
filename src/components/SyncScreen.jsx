import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useAssets } from '../contexts/AssetContext';

export default function SyncScreen({ onSkip }) {
  const { downloadAllCategories, getDownloadProgress, downloadingCategory, downloadProgress } = useAssets();
  const [isDownloading, setIsDownloading] = useState(false);

  const overall = useMemo(() => getDownloadProgress(), [getDownloadProgress]);

  const startDownload = useCallback(async () => {
    if (isDownloading) return;
    setIsDownloading(true);
    try {
      await downloadAllCategories();
    } finally {
      setIsDownloading(false);
    }
  }, [downloadAllCategories, isDownloading]);

  useEffect(() => {
    startDownload();
  }, [startDownload]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-green-50">
      <div className="text-center p-8 bg-white rounded-3xl shadow-2xl max-w-md w-full mx-4">
        <div className="mb-8">
          <div className="w-32 h-32 mx-auto mb-4 relative">
            <div className="absolute inset-0 bg-blue-100 rounded-full animate-pulse"></div>
            <div className="absolute inset-2 bg-blue-200 rounded-full animate-ping"></div>
            <div className="absolute inset-4 bg-blue-300 rounded-full flex items-center justify-center text-4xl">
              🦁
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Getting Liora Ready!
          </h1>
          <p className="text-gray-600">
            Downloading animal library for offline play...
          </p>
        </div>

        <div className="mb-6">
          <div className="w-full h-4 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 to-green-500 transition-all duration-500 ease-out"
              style={{ width: `${overall}%` }}
            />
          </div>
          <p className="text-sm text-gray-500 mt-2">
            {Math.round(overall)}% Complete
          </p>
        </div>

        <div className="space-y-2 text-sm text-gray-600">
          <p>
            {downloadingCategory
              ? `Downloading: ${downloadingCategory} (${Math.round(downloadProgress)}%)`
              : isDownloading
                ? 'Starting downloads...'
                : 'Done!'}
          </p>
        </div>

        <div className="mt-6 flex items-center justify-center gap-3">
          <button
            type="button"
            onClick={onSkip}
            className="px-4 py-2 rounded-full font-bold bg-white/80 backdrop-blur border border-white/60 shadow hover:bg-white"
          >
            Skip for now
          </button>
        </div>

        <div className="mt-6 flex justify-center space-x-2">
          <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce"></div>
          <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>
    </div>
  );
}
