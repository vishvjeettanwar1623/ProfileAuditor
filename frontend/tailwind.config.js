/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        dark: {
          base: '#090A0C',
          surface: '#111418',
          elevated: '#161A20',
          border: '#1F242D',
          borderLight: '#2A313C',
          textMuted: '#64748B',
          textBody: '#94A3B8',
          textHead: '#F8FAFC',
        }
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.4)',
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.5), 0 1px 2px -1px rgba(0, 0, 0, 0.5)',
        'glow': '0 0 20px -5px rgba(255, 255, 255, 0.05)',
      }
    },
  },
  plugins: [],
}