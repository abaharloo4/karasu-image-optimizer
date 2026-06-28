/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        fa: ['YekanBakh', 'sans-serif'],
        en: ['Inter', 'sans-serif'],
        sans: ['YekanBakh', 'Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
