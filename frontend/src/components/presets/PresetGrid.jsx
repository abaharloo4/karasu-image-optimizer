import React from 'react';
import { useTranslation } from 'react-i18next';
import { Globe, Smartphone, Image as ImageIcon, Zap, Award, Share2 } from 'lucide-react';

const PRESET_ICONS = {
  web_optimized: Globe,
  mobile_optimized: Smartphone,
  thumbnail: ImageIcon,
  max_compression: Zap,
  high_quality: Award,
  social_media: Share2
};

const PRESETS_INFO = {
  web_optimized: {
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
  },
  mobile_optimized: {
    quality: 75,
    output_format: 'webp',
    target_width: 1080,
    target_height: '',
    maintain_aspect: true,
    smart_format: true,
    sharpen: 0,
    blur: 0,
    brightness: 1.0,
    contrast: 1.0,
    preserve_exif: false
  },
  thumbnail: {
    quality: 85,
    output_format: 'jpg',
    target_width: 300,
    target_height: 300,
    maintain_aspect: true,
    smart_format: false,
    sharpen: 1,
    blur: 0,
    brightness: 1.0,
    contrast: 1.0,
    preserve_exif: false
  },
  max_compression: {
    quality: 60,
    output_format: 'webp',
    target_width: 1280,
    target_height: '',
    maintain_aspect: true,
    smart_format: true,
    sharpen: 0,
    blur: 0,
    brightness: 1.0,
    contrast: 1.0,
    preserve_exif: false
  },
  high_quality: {
    quality: 95,
    output_format: 'png',
    target_width: '',
    target_height: '',
    maintain_aspect: true,
    smart_format: false,
    sharpen: 0,
    blur: 0,
    brightness: 1.0,
    contrast: 1.0,
    preserve_exif: true
  },
  social_media: {
    quality: 85,
    output_format: 'jpg',
    target_width: 1080,
    target_height: 1080,
    maintain_aspect: true,
    smart_format: false,
    sharpen: 0,
    blur: 0,
    brightness: 1.0,
    contrast: 1.0,
    preserve_exif: false
  }
};

export default function PresetGrid({ selectedPreset, onSelectPreset, onUpdateSettings }) {
  const { t } = useTranslation();

  const handleSelect = (presetKey) => {
    onSelectPreset(presetKey);
    onUpdateSettings(PRESETS_INFO[presetKey]);
  };

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-bold text-gray-700 dark:text-gray-300">
        {t('presets.title')}
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {Object.keys(PRESETS_INFO).map((presetKey) => {
          const IconComponent = PRESET_ICONS[presetKey] || ImageIcon;
          const isSelected = selectedPreset === presetKey;
          
          return (
            <button
              key={presetKey}
              onClick={() => handleSelect(presetKey)}
              className={`flex flex-col items-center justify-center p-4 border rounded-xl text-center transition-all duration-200 ${
                isSelected
                  ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-950/20 text-blue-600 dark:text-blue-400 ring-2 ring-blue-100 dark:ring-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700/60 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:border-blue-300 dark:hover:border-blue-800 hover:shadow-sm'
              }`}
            >
              <IconComponent className={`w-6 h-6 mb-2 ${isSelected ? 'text-blue-500' : 'text-gray-400 dark:text-gray-500'}`} />
              <span className="text-xs font-bold block truncate max-w-full">
                {t(`presets.${presetKey}`)}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
