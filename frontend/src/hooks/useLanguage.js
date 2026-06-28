import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

export function useLanguage() {
  const { i18n } = useTranslation();
  const currentLanguage = i18n.language || 'fa';
  const isRTL = currentLanguage === 'fa';

  useEffect(() => {
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = currentLanguage;
  }, [currentLanguage, isRTL]);

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return { currentLanguage, isRTL, changeLanguage };
}
