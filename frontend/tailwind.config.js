/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        primary: {
          DEFAULT: '#4F46E5', // Deep indigo — muted, credible take on the original purple
          50: '#EEF2FF',
          100: '#E0E7FF',
          200: '#C7D2FE',
          300: '#A5B4FC',
          400: '#818CF8',
          500: '#6366F1',
          600: '#4F46E5', // Main Brand
          700: '#4338CA',
          800: '#3730A3',
          900: '#312E81',
        },
        secondary: {
          DEFAULT: '#0D9488', // Muted teal — replaces bright pink for a calmer, professional accent
          50: '#F0FDFA',
          100: '#CCFBF1',
          200: '#99F6E4',
          400: '#2DD4BF',
          500: '#14B8A6',
          600: '#0D9488', // Main Brand
          700: '#0F766E',
        },
        accent: {
          DEFAULT: '#D97706', // Muted amber — reserved for deadlines/warnings, not brand-wide
          50: '#FFFBEB',
          100: '#FEF3C7',
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706', // Main Brand
          700: '#B45309',
        },
        slate: {
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
          600: '#475569',
          700: '#334155',
          800: '#1E293B',
          850: '#1e293b', // Custom dark for text
          900: '#0F172A',
        },
        background: {
          DEFAULT: '#F8FAFC', // Slate 50
          paper: '#FFFFFF',
        }
      },
    },
  },
  plugins: [],
}
