/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Matrix-inspired black and green palette
        primary: {
          50: '#F2F2F2',   // lightest gray
          100: '#E6E6E6',  // lighter gray
          200: '#CCCCCC',  // light gray
          300: '#B3B3B3',  // medium gray
          400: '#808080',  // gray
          500: '#1A1A1A',  // rich black (main)
          600: '#141414',  // deeper black
          700: '#0D0D0D',  // very deep black
          800: '#070707',  // almost black
          900: '#000000'   // pure black
        },
        accent: {
          neon: '#39FF14',     // electric neon green
          matrix: '#00FF41',   // matrix green
          emerald: '#50C878'   // emerald green
        },
        secondary: {
          50: '#FFFFFF',
          100: '#E6FFF2',
          200: '#B3FFD9',
          300: '#80FFC0',
          400: '#4DFFA6',
          500: '#1AFF8C',  // vibrant green
          600: '#00E673',
          700: '#00B359',
          800: '#008040',
          900: '#004D26'
        },
        highlight: {
          glow: '#7FFF00',     // bright green glow
          flash: '#32CD32',    // lime flash
          cyber: '#008F11'     // cyber green
        }
      },
    },
  },
  plugins: [],
}