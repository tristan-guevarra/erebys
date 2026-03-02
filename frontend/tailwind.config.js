/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        erebys: {
          50:  "#f5f3ff",
          100: "#ede9fe",
          200: "#ddd6fe",
          300: "#c4b5fd",
          400: "#a78bfa",
          500: "#8b5cf6",
          600: "#7c3aed",
          700: "#6d28d9",
          800: "#5b21b6",
          900: "#4c1d95",
          950: "#2e1065",
        },
        accent: {
          emerald: "#10b981",
          amber:   "#f59e0b",
          rose:    "#f43f5e",
          cyan:    "#06b6d4",
        },
      },
      fontFamily: {
        display: ['"Outfit"', "system-ui", "sans-serif"],
        body:    ['"DM Sans"', "system-ui", "sans-serif"],
        mono:    ['"JetBrains Mono"', "monospace"],
      },
      animation: {
        "fade-in":       "fadeIn 0.4s ease-out",
        "slide-up":      "slideUp 0.35s ease-out",
        "slide-in-left": "slideInLeft 0.25s ease-out",
        "pulse-subtle":  "pulseSubtle 2s infinite",
      },
      keyframes: {
        fadeIn:      { "0%": { opacity: "0" },                               "100%": { opacity: "1" } },
        slideUp:     { "0%": { opacity: "0", transform: "translateY(10px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        slideInLeft: { "0%": { opacity: "0", transform: "translateX(-10px)" }, "100%": { opacity: "1", transform: "translateX(0)" } },
        pulseSubtle: { "0%, 100%": { opacity: "1" }, "50%": { opacity: "0.65" } },
      },
    },
  },
  plugins: [],
};
