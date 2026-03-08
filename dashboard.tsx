/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#eff6ff",
          100: "#dbeafe",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          800: "#1e40af",
          900: "#1a3a5c",
        },
        brand: "#1a3a5c",
        accent: "#0ea5e9",
      },
      fontFamily: {
        sans: ["'DM Sans'", "sans-serif"],
        display: ["'Outfit'", "sans-serif"],
      },
    },
  },
  plugins: [],
};
