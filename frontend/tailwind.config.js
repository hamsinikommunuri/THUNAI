/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        nature: {
          50: '#F4F9F4',
          100: '#E8F5E9',
          200: '#C8E6C9',
          300: '#A5D6A7',
          400: '#81C784',
          500: '#4CAF50',
          600: '#388E3C',
          700: '#2E7D32',
          800: '#1B5E20',
          900: '#0E3E14',
          950: '#07240B',
        },
        forest: {
          DEFAULT: '#143122',
          deep: '#0E2419',
          dark: '#08170F',
          surface: '#11291C',
        },
        earth: {
          50: '#FDFBF7',
          100: '#F7F2E7',
          200: '#EAE1CE',
          300: '#D5C4A5',
          400: '#BAA079',
          500: '#9E7F54',
          600: '#7F623C',
          700: '#5D4428',
          800: '#402D18',
        },
        cream: {
          50: '#FCFBF9',
          100: '#F8F6F0',
          200: '#F2EFE6',
          300: '#E8E3D5',
        },
        emerald: {
          bright: '#7CE8A1',
          DEFAULT: '#5FCB87',
          glow: 'rgba(95, 203, 135, 0.2)',
        },
        sunlight: {
          DEFAULT: '#E7C66B',
          warm: '#F59E0B',
          glow: 'rgba(231, 198, 107, 0.25)',
        },
        obsidian: '#080B0A',
        charcoal: '#0F1411',
        carbon: '#161D19',
        mineral: '#F4F1E8',
        'mineral-muted': '#9CA39E',
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        serif: ['"Newsreader"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'natural': '0 4px 20px -2px rgba(14, 36, 25, 0.08), 0 2px 6px -1px rgba(14, 36, 25, 0.04)',
        'natural-lg': '0 12px 36px -4px rgba(14, 36, 25, 0.12), 0 4px 12px -2px rgba(14, 36, 25, 0.06)',
        'natural-dark': '0 12px 40px -10px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 255, 255, 0.07)',
        'glow-emerald': '0 0 25px -4px rgba(95, 203, 135, 0.35)',
      },
      borderRadius: {
        'natural': '24px',
        'natural-lg': '32px',
      }
    },
  },
  plugins: [],
}
