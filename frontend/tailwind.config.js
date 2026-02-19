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
          DEFAULT: '#7B3FFF', // Purple
          50: '#F5F3FF',
          100: '#EDE9FE',
          200: '#DDD6FE',
          300: '#C4B5FD',
          400: '#A78BFA',
          500: '#8B5CF6',
          600: '#7B3FFF', // Main Brand
          700: '#6D28D9',
          800: '#5B21B6',
          900: '#4C1D95',
        },
        secondary: {
          DEFAULT: '#FF46A4', // Pink
          50: '#FDF2F8',
          100: '#FCE7F3',
          500: '#EC4899',
          600: '#FF46A4', // Main Brand
          700: '#BE185D',
        },
        accent: {
          DEFAULT: '#FDC830', // Yellow
          50: '#FFFBEB',
          100: '#FEF3C7',
          500: '#F59E0B',
          600: '#FDC830', // Main Brand
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
      keyframes: {
        shine: {
          '0%': { backgroundPosition: '200% center' },
          '100%': { backgroundPosition: '-200% center' },
        },
      },
      animation: {
        shine: 'shine 4s linear infinite',
      },
    },
  },
  plugins: [],
}
