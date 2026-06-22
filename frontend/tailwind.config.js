/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        sand:          "#f5f0e8",
        "sand-dark":   "#ede6d6",
        charcoal:      "#1a1a2e",
        "charcoal-l":  "#2d2d4e",
        "melb-blue":   "#0057b7",
        "melb-blue-l": "#1a6fd4",
        "melb-gold":   "#d4a017",
      },
      fontFamily: {
        serif: ["Libre Baskerville", "Georgia", "serif"],
        mono:  ["Space Mono", "Courier New", "monospace"],
      },
    },
  },
  plugins: [],
};
