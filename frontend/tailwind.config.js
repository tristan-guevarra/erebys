/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        erebys: {
          50:  "#f6f3ff",
          100: "#eee8ff",
          200: "#dfd3ff",
          300: "#c8b2fd",
          400: "#b196f0",
          500: "#9a7de0",
          600: "#8462c2",
          700: "#6f4aab",
          800: "#5c3994",
          900: "#4b2d7d",
          950: "#2d1660",
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
        "fade-in":       "fadeIn 0.4s ease-out forwards",
        "slide-up":      "slideUp 0.35s ease-out forwards",
        "slide-in-left": "slideInLeft 0.25s ease-out forwards",
        "pulse-subtle":  "pulseSubtle 2s infinite",
        "shimmer":       "shimmer 2.5s infinite",
      },
      keyframes: {
        fadeIn:      { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        slideUp:     { "0%": { opacity: "0", transform: "translateY(10px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        slideInLeft: { "0%": { opacity: "0", transform: "translateX(-10px)" }, "100%": { opacity: "1", transform: "translateX(0)" } },
        pulseSubtle: { "0%, 100%": { opacity: "1" }, "50%": { opacity: "0.65" } },
        shimmer:     { "0%": { backgroundPosition: "-200% 0" }, "100%": { backgroundPosition: "200% 0" } },
      },
    },
  },
  plugins: [],
};
