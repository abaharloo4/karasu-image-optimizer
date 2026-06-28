import React from 'react';
import { useTranslation } from 'react-i18next';
import { X, Eye } from 'lucide-react';
import BeforeAfter from './BeforeAfter';

export default function PreviewModal({ fileId, settings, onClose }) {
  const { t } = useTranslation();

  if (!fileId) return null;

  // Build original URL
  const originalSrc = `/api/preview/${fileId}?original=true`;

  // Build preview URL with current settings
  const queryParams = new URLSearchParams({
    quality: settings.quality.toString(),
    output_format: settings.output_format || 'webp',
    target_width: (settings.target_width || '').toString(),
    target_height: (settings.target_height || '').toString(),
    maintain_aspect: settings.maintain_aspect ? 'true' : 'false',
    smart_format: settings.smart_format ? 'true' : 'false',
    sharpen: settings.sharpen.toString(),
    blur: settings.blur.toString(),
    brightness: settings.brightness.toString(),
    contrast: settings.contrast.toString(),
    // Cache buster
    _cb: settings._cb || Date.now()
  });

  const previewSrc = `/api/preview/${fileId}?${queryParams.toString()}`;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-3xl w-full max-w-4xl shadow-2xl flex flex-col max-h-[90vh] border border-gray-100 dark:border-gray-700/60 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-gray-100 dark:border-gray-700/60">
          <div className="flex items-center space-x-2.5 rtl:space-x-reverse text-blue-500">
            <Eye className="w-5 h-5" />
            <h3 className="text-sm font-extrabold text-gray-800 dark:text-gray-200">
              {t('actions.preview')}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700/80 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 flex flex-col justify-center">
          <BeforeAfter originalSrc={originalSrc} previewSrc={previewSrc} />
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-bold text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/30 p-4 rounded-2xl">
            <div>
              <span>{t('settings.quality')}: </span>
              <span className="text-blue-500">{settings.quality}%</span>
            </div>
            <div>
              <span>{t('settings.format')}: </span>
              <span className="text-blue-500">
                {settings.smart_format ? t('settings.smart_format') : settings.output_format.toUpperCase()}
              </span>
            </div>
            <div>
              <span>ابعاد: </span>
              <span className="text-blue-500">
                {settings.target_width || 'Auto'} x {settings.target_height || 'Auto'}
              </span>
            </div>
            <div>
              <span>افکت‌ها: </span>
              <span className="text-blue-500">
                {settings.sharpen > 0 ? `Sharpen(${settings.sharpen}) ` : ''}
                {settings.blur > 0 ? `Blur(${settings.blur}) ` : ''}
                {settings.brightness !== 1.0 ? `Bright(${settings.brightness}) ` : ''}
                {settings.contrast !== 1.0 ? `Contrast(${settings.contrast}) ` : ''}
                {settings.sharpen === 0 && settings.blur === 0 && settings.brightness === 1.0 && settings.contrast === 1.0 ? 'None' : ''}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
