import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import faTranslation from './fa.json';
import enTranslation from './en.json';

const resources = {
  fa: {
    translation: faTranslation,
  },
  en: {
    translation: enTranslation,
  },
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'fa', // Default language is Persian
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
