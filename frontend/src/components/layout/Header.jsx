import React from 'react';
import { useTranslation } from 'react-i18next';
import { Sun, Moon, Languages, History } from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';

export default function Header({ theme, toggleTheme, showHistory, onToggleHistory }) {
  const { t } = useTranslation();
  const { currentLanguage, changeLanguage } = useLanguage();

  const handleLanguageToggle = () => {
    const nextLang = currentLanguage === 'fa' ? 'en' : 'fa';
    changeLanguage(nextLang);
  };

  return (
    <header className="w-full flex items-center justify-between py-5 border-b border-gray-100 dark:border-gray-800/80 mb-8 transition-colors duration-200">
      <div className="space-y-1">
        <h1 className="text-xl md:text-2xl font-black bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 bg-clip-text text-transparent">
          {t('app.title')}
        </h1>
        <p className="text-xs text-gray-500 dark:text-gray-400 hidden sm:block font-bold">
          {t('app.subtitle')}
        </p>
      </div>

      <div className="flex items-center space-x-2.5 rtl:space-x-reverse">
        {/* History Button */}
        <button
          onClick={onToggleHistory}
          className={`flex items-center space-x-1.5 rtl:space-x-reverse px-3 py-1.5 border rounded-xl text-xs font-bold transition-all duration-200 ${
            showHistory
              ? 'bg-blue-600 border-blue-600 text-white hover:bg-blue-700'
              : 'border-gray-200 dark:border-gray-700/80 hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-300'
          }`}
          title={showHistory ? t('history.back_to_optimizer') : t('history.view_history')}
        >
          <History className="w-4 h-4" />
          <span className="hidden sm:inline">
            {showHistory ? t('history.back_to_optimizer') : t('history.view_history')}
          </span>
        </button>

        {/* Language Switcher */}
        <button
          onClick={handleLanguageToggle}
          className="flex items-center space-x-1.5 rtl:space-x-reverse px-3 py-1.5 border border-gray-200 dark:border-gray-700/80 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 text-xs font-bold text-gray-600 dark:text-gray-300 transition-all duration-200"
          title="تغییر زبان / Switch Language"
        >
          <Languages className="w-4 h-4" />
          <span>{currentLanguage === 'fa' ? 'English' : 'فارسی'}</span>
        </button>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 border border-gray-200 dark:border-gray-700/80 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-300 transition-all duration-200"
          title={theme === 'dark' ? t('theme.light') : t('theme.dark')}
        >
          {theme === 'dark' ? (
            <Sun className="w-4.5 h-4.5 text-yellow-500" />
          ) : (
            <Moon className="w-4.5 h-4.5 text-indigo-500" />
          )}
        </button>
      </div>
    </header>
  );
}
