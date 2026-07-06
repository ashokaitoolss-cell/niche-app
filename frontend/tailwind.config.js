/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F7F5F0",
        ink: "#1B1B18",
        research: {
          DEFAULT: "#0F6E56",
          light: "#5DCAA5",
          bg: "#E1F5EE",
        },
        market: {
          DEFAULT: "#D85A30",
          light: "#F0997B",
          bg: "#FAECE7",
        },
        synth: {
          DEFAULT: "#BA7517",
          light: "#FAC775",
          bg: "#FAEEDA",
        },
      },
      fontFamily: {
        display: ["'Archivo Black'", "Impact", "sans-serif"],
        body: ["'Inter'", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
    },
  },
  plugins: [],
};
