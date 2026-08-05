/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0b0f19",
        card: "#111827",
        border: "#1f2937",
        primary: "#3b82f6",
        success: "#10b981",
        danger: "#ef4444",
      },
    },
  },
  plugins: [],
};
