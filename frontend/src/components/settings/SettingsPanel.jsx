import React from 'react';
import { useTranslation } from 'react-i18next';
import { Sliders, Eye } from 'lucide-react';

export default function SettingsPanel({ settings, onUpdateSettings, selectedPreset, onSelectPreset }) {
  const { t } = useTranslation();

  const handleSettingChange = (key, value) => {
    if (selectedPreset !== 'custom') {
      onSelectPreset('custom');
    }
    onUpdateSettings({ [key]: value });
  };

  const handleCheckboxChange = (key, e) => {
    handleSettingChange(key, e.target.checked);
  };

  const handleInputChange = (key, e) => {
    const val = e.target.value;
    if (val === '') {
      handleSettingChange(key, '');
    } else {
      const num = parseFloat(val);
      handleSettingChange(key, isNaN(num) ? val : num);
    }
  };

  return (
    <div className="w-full bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700/60 rounded-2xl p-5 shadow-sm space-y-6">
      <div className="flex items-center space-x-2 rtl:space-x-reverse pb-3 border-b border-gray-100 dark:border-gray-700/60">
        <Sliders className="w-5 h-5 text-blue-500" />
        <h3 className="text-sm font-extrabold text-gray-800 dark:text-gray-200">
          {t('settings.title')}
          {selectedPreset === 'custom' && (
            <span className="ml-2 rtl:mr-2 text-xs font-normal text-blue-500 bg-blue-50 dark:bg-blue-950/20 px-2 py-0.5 rounded-full">
              {t('settings.custom')}
            </span>
          )}
        </h3>
      </div>

      <div className="space-y-4">
        {/* Quality Slider */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-bold text-gray-600 dark:text-gray-400">
            <label htmlFor="quality-slider">{t('settings.quality')}</label>
            <span className="text-blue-500">{settings.quality}%</span>
          </div>
          <input
            id="quality-slider"
            type="range"
            min="10"
            max="100"
            value={settings.quality}
            onChange={(e) => handleSettingChange('quality', parseInt(e.target.value))}
            className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        {/* Output Format and Smart Format */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <label htmlFor="format-select" className="text-xs font-bold text-gray-600 dark:text-gray-400">
              {t('settings.format')}
            </label>
            <select
              id="format-select"
              value={settings.output_format}
              disabled={settings.smart_format}
              onChange={(e) => handleSettingChange('output_format', e.target.value)}
              className="w-full p-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-xs font-bold text-gray-700 dark:text-gray-300 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="jpg">JPEG (JPG)</option>
              <option value="png">PNG</option>
              <option value="webp">WebP</option>
            </select>
          </div>

          <div className="flex items-center justify-center pt-6">
            <label htmlFor="smart-format-checkbox" className="flex items-center space-x-2.5 rtl:space-x-reverse cursor-pointer text-xs font-bold text-gray-600 dark:text-gray-400">
              <input
                id="smart-format-checkbox"
                type="checkbox"
                checked={settings.smart_format}
                onChange={(e) => {
                  const checked = e.target.checked;
                  handleSettingChange('smart_format', checked);
                  if (checked) {
                    // Smart format will automatically select best format, but default placeholder
                    handleSettingChange('output_format', 'webp');
                  }
                }}
                className="w-4.5 h-4.5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 dark:border-gray-700 dark:bg-gray-900"
              />
              <span>{t('settings.smart_format')}</span>
            </label>
          </div>
        </div>

        {/* Width and Height */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <label htmlFor="width-input" className="text-xs font-bold text-gray-600 dark:text-gray-400">
              {t('settings.width')}
            </label>
            <input
              id="width-input"
              type="number"
              min="1"
              value={settings.target_width || ''}
              placeholder="Auto"
              onChange={(e) => handleInputChange('target_width', e)}
              className="w-full p-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-xs font-bold text-gray-700 dark:text-gray-300 focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="height-input" className="text-xs font-bold text-gray-600 dark:text-gray-400">
              {t('settings.height')}
            </label>
            <input
              id="height-input"
              type="number"
              min="1"
              value={settings.target_height || ''}
              placeholder="Auto"
              onChange={(e) => handleInputChange('target_height', e)}
              className="w-full p-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-xs font-bold text-gray-700 dark:text-gray-300 focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Checkboxes: Maintain Aspect and Preserve Exif */}
        <div className="grid grid-cols-2 gap-3 pt-2">
          <label htmlFor="maintain-aspect-checkbox" className="flex items-center space-x-2.5 rtl:space-x-reverse cursor-pointer text-xs font-bold text-gray-600 dark:text-gray-400">
            <input
              id="maintain-aspect-checkbox"
              type="checkbox"
              checked={settings.maintain_aspect}
              onChange={(e) => handleCheckboxChange('maintain_aspect', e)}
              className="w-4.5 h-4.5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 dark:border-gray-700 dark:bg-gray-900"
            />
            <span>{t('settings.maintain_aspect')}</span>
          </label>

          <label htmlFor="preserve-exif-checkbox" className="flex items-center space-x-2.5 rtl:space-x-reverse cursor-pointer text-xs font-bold text-gray-600 dark:text-gray-400">
            <input
              id="preserve-exif-checkbox"
              type="checkbox"
              checked={settings.preserve_exif}
              onChange={(e) => handleCheckboxChange('preserve_exif', e)}
              className="w-4.5 h-4.5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 dark:border-gray-700 dark:bg-gray-900"
            />
            <span>{t('settings.preserve_exif')}</span>
          </label>
        </div>

        {/* Filters/Adjustments (Accordion or Section) */}
        <details className="group border-t border-gray-100 dark:border-gray-700/60 pt-4">
          <summary className="flex items-center justify-between cursor-pointer list-none text-xs font-extrabold text-gray-700 dark:text-gray-300 hover:text-blue-500 transition-colors">
            <span>🎨 {t('settings.custom')} (Brightness, Filters...)</span>
            <span className="transition group-open:rotate-180 text-gray-400">
              ▼
            </span>
          </summary>
          <div className="space-y-4 mt-4 pl-1">
            {/* Sharpen Slider */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-bold text-gray-600 dark:text-gray-400">
                <label htmlFor="sharpen-slider">{t('settings.sharpen')}</label>
                <span className="text-blue-500">{settings.sharpen}</span>
              </div>
              <input
                id="sharpen-slider"
                type="range"
                min="0"
                max="5"
                step="1"
                value={settings.sharpen}
                onChange={(e) => handleSettingChange('sharpen', parseInt(e.target.value))}
                className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            {/* Blur Slider */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-bold text-gray-600 dark:text-gray-400">
                <label htmlFor="blur-slider">{t('settings.blur')}</label>
                <span className="text-blue-500">{settings.blur} px</span>
              </div>
              <input
                id="blur-slider"
                type="range"
                min="0"
                max="10"
                step="0.5"
                value={settings.blur}
                onChange={(e) => handleSettingChange('blur', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            {/* Brightness Slider */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-bold text-gray-600 dark:text-gray-400">
                <label htmlFor="brightness-slider">{t('settings.brightness')}</label>
                <span className="text-blue-500">x{settings.brightness.toFixed(1)}</span>
              </div>
              <input
                id="brightness-slider"
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={settings.brightness}
                onChange={(e) => handleSettingChange('brightness', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            {/* Contrast Slider */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-bold text-gray-600 dark:text-gray-400">
                <label htmlFor="contrast-slider">{t('settings.contrast')}</label>
                <span className="text-blue-500">x{settings.contrast.toFixed(1)}</span>
              </div>
              <input
                id="contrast-slider"
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={settings.contrast}
                onChange={(e) => handleSettingChange('contrast', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
              />
            </div>
          </div>
        </details>
      </div>
    </div>
  );
}
