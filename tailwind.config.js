/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        sps: {
          navy: 'var(--sps-deep-navy)',
          blue: 'var(--sps-blue)',
          bright: 'var(--sps-bright-blue)',
          light: 'var(--sps-light-blue)',
          border: 'var(--sps-border-blue)',
        },
      },
      boxShadow: {
        card: '0 10px 30px rgba(11, 31, 77, 0.08)',
      },
      fontFamily: {
        sans: ['Inter', 'Segoe UI', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
