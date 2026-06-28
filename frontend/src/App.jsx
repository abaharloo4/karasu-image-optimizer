import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import Header from './components/layout/Header';
import DropZone from './components/upload/DropZone';
import FileList from './components/upload/FileList';
import PresetGrid from './components/presets/PresetGrid';
import SettingsPanel from './components/settings/SettingsPanel';
import ProgressBar from './components/progress/ProgressBar';
import StatsPanel from './components/stats/StatsPanel';
import PreviewModal from './components/preview/PreviewModal';
import HistoryPanel from './components/history/HistoryPanel';
import { useTheme } from './hooks/useTheme';
import { useLanguage } from './hooks/useLanguage';
import { Play, RotateCcw } from 'lucide-react';

const DEFAULT_SETTINGS = {
  quality: 80,
  output_format: 'webp',
  target_width: 1920,
  target_height: '',
  maintain_aspect: true,
  smart_format: true,
  sharpen: 0,
  blur: 0,
  brightness: 1.0,
  contrast: 1.0,
  preserve_exif: false
};

export default function App() {
  const { t } = useTranslation();
  const { theme, toggleTheme } = useTheme();
  const { isRTL } = useLanguage();

  // App States
  const [files, setFiles] = useState([]);
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [selectedPreset, setSelectedPreset] = useState('web_optimized');
  const [previewFileId, setPreviewFileId] = useState(null);
  const [showHistory, setShowHistory] = useState(false);

  // Job & Processing States
  const [jobId, setJobId] = useState(null);
  const [processingStatus, setProcessingStatus] = useState('idle'); // idle, processing, done, error
  const [processingProgress, setProcessingProgress] = useState(0);
  const [processingError, setProcessingError] = useState(null);
  const [jobResult, setJobResult] = useState(null);

  const pollingIntervalRef = useRef(null);

  // Clean up polling on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  const handleUploadComplete = (newFiles) => {
    setFiles((prev) => [...prev, ...newFiles]);
  };

  const handleDeleteFile = (fileId) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId));
  };

  const handleUpdateSettings = (updates) => {
    setSettings((prev) => ({ ...prev, ...updates }));
  };

  const handleReset = () => {
    setFiles([]);
    setSettings(DEFAULT_SETTINGS);
    setSelectedPreset('web_optimized');
    setJobId(null);
    setProcessingStatus('idle');
    setProcessingProgress(0);
    setProcessingError(null);
    setJobResult(null);
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }
  };

  const handleStartProcessing = async () => {
    if (files.length === 0) return;

    setProcessingStatus('processing');
    setProcessingProgress(0);
    setProcessingError(null);

    const fileIds = files.map((f) => f.id);

    try {
      const response = await axios.post('/api/process', {
        file_ids: fileIds,
        settings: settings
      });

      const { job_id } = response.data;
      setJobId(job_id);

      // Start Polling status
      startPolling(job_id);
    } catch (err) {
      console.error(err);
      setProcessingStatus('error');
      setProcessingError(err.response?.data?.error || t('status.error'));
    }
  };

  const startPolling = (jobId) => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    pollingIntervalRef.current = setInterval(async () => {
      try {
        const response = await axios.get(`/api/jobs/${jobId}`);
        const { status, progress, total, results, error } = response.data;

        if (status === 'done') {
          clearInterval(pollingIntervalRef.current);
          setProcessingProgress(progress);
          setJobResult(response.data);
          setProcessingStatus('done');
        } else if (status === 'error') {
          clearInterval(pollingIntervalRef.current);
          setProcessingStatus('error');
          setProcessingError(error || t('status.error'));
        } else {
          // Still processing
          setProcessingProgress(progress);
        }
      } catch (err) {
        console.error(err);
        clearInterval(pollingIntervalRef.current);
        setProcessingStatus('error');
        setProcessingError(t('status.error'));
      }
    }, 500);
  };

  return (
    <div className={`min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 ${isRTL ? 'font-fa' : 'font-en'} transition-colors duration-200`}>
      <div className="max-w-5xl mx-auto px-4 pb-12">
        <Header
          theme={theme}
          toggleTheme={toggleTheme}
          showHistory={showHistory}
          onToggleHistory={() => setShowHistory(prev => !prev)}
        />

        {showHistory ? (
          <HistoryPanel onBack={() => setShowHistory(false)} />
        ) : processingStatus === 'done' ? (
          <div className="space-y-6">
            <StatsPanel jobResult={jobResult} onReset={handleReset} />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Progress Bar */}
            {processingStatus !== 'idle' && (
              <ProgressBar
                progress={processingProgress}
                total={files.length}
                status={processingStatus}
                error={processingError}
              />
            )}

            {files.length === 0 ? (
              <div className="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-800/80 rounded-3xl p-6 shadow-sm">
                <DropZone onUploadComplete={handleUploadComplete} onError={setProcessingError} />
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Column 1: Files List */}
                <div className="lg:col-span-7 space-y-4">
                  <div className="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-800/80 rounded-3xl p-5 shadow-sm space-y-5">
                    <FileList
                      files={files}
                      onDeleteFile={handleDeleteFile}
                      onSelectPreview={(id) => {
                        // Include a timestamp as cache buster inside preview settings
                        setSettings(prev => ({ ...prev, _cb: Date.now() }));
                        setPreviewFileId(id);
                      }}
                    />

                    {processingStatus === 'idle' && (
                      <div className="flex flex-col sm:flex-row gap-3 pt-2">
                        <button
                          onClick={handleStartProcessing}
                          className="flex-1 flex items-center justify-center space-x-2.5 rtl:space-x-reverse py-3.5 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-extrabold rounded-xl shadow-md hover:shadow-lg transition-all duration-200"
                        >
                          <Play className="w-5 h-5 fill-current" />
                          <span>{t('actions.process')}</span>
                        </button>
                        <button
                          onClick={handleReset}
                          className="flex-1 sm:flex-none flex items-center justify-center space-x-2.5 rtl:space-x-reverse py-3.5 px-6 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 font-extrabold rounded-xl transition-colors"
                        >
                          <RotateCcw className="w-5 h-5" />
                          <span>{t('actions.clear_all')}</span>
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Column 2: Presets & Settings */}
                <div className="lg:col-span-5 space-y-5">
                  {processingStatus === 'idle' && (
                    <>
                      <div className="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-800/80 rounded-3xl p-5 shadow-sm">
                        <PresetGrid
                          selectedPreset={selectedPreset}
                          onSelectPreset={setSelectedPreset}
                          onUpdateSettings={handleUpdateSettings}
                        />
                      </div>
                      <SettingsPanel
                        settings={settings}
                        onUpdateSettings={handleUpdateSettings}
                        selectedPreset={selectedPreset}
                        onSelectPreset={setSelectedPreset}
                      />
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Live Preview Modal */}
      {previewFileId && (
        <PreviewModal
          fileId={previewFileId}
          settings={settings}
          onClose={() => setPreviewFileId(null)}
        />
      )}
    </div>
  );
}
