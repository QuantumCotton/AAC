/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          toy: '#FF6B6B',
          real: '#4ECDC4',
        },
        categories: {
          'Ultra Deep Sea': '#0F172A',
          'Deep Sea': '#1E293B',
          'Coral Reef': '#0891B2',
          'Shallow Water': '#06B6D4',
          'Farm': '#84CC16',
          'Domestic': '#EAB308',
          'Forest': '#059669',
          'Jungle': '#10B981',
          'Nocturnal': '#6B21A8',
          'Arctic': '#0EA5E9'
        }
      },
      animation: {
        'bounce-gentle': 'bounce 2s infinite',
        'pulse-slow': 'pulse 3s infinite',
      },
      fontFamily: {
        'child': ['Comic Sans MS', 'Marker Felt', 'cursive'],
      }
    },
  },
  plugins: [],
}
