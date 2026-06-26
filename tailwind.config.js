/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        "surface-dim": "#121415",
        "surface-container-low": "#1a1c1d",
        "surface-container-lowest": "#0c0e0f",
        "surface-variant": "#333536",
        "on-tertiary-container": "#484a65",
        "secondary-fixed-dim": "#c6c6c7",
        "outline-variant": "#4c463b",
        "surface-tint": "#dac497",
        "error": "#ffb4ab",
        "on-secondary-fixed": "#1a1c1d",
        "on-surface-variant": "#cec5b7",
        "surface-container": "#1e2021",
        "surface-container-high": "#282a2b",
        "surface": "#121415",
        "background": "#121415",
        "on-primary-fixed-variant": "#544522",
        "on-error-container": "#ffdad6",
        "tertiary-container": "#b9bbda",
        "surface-bright": "#38393a",
        "surface-container-highest": "#333536",
        "inverse-primary": "#6d5d37",
        "on-primary-container": "#594a27",
        "tertiary-fixed": "#dfe0ff",
        "primary-fixed": "#f7e0b1",
        "primary-container": "#d0bb8e",
        "secondary-fixed": "#e2e2e3",
        "on-secondary-fixed-variant": "#454748",
        "on-primary": "#3c2f0e",
        "outline": "#979083",
        "inverse-on-surface": "#2f3132",
        "error-container": "#93000a",
        "on-surface": "#e2e2e3",
        "primary-fixed-dim": "#dac497",
        "on-primary-fixed": "#251a00",
        "on-secondary-container": "#b4b5b6",
        "on-tertiary-fixed-variant": "#42455f",
        "on-error": "#690005",
        "on-secondary": "#2f3132",
        "primary": "#edd7a8",
        "tertiary": "#d5d7f7",
        "on-tertiary": "#2c2f47",
        "secondary-container": "#454748",
        "on-background": "#e2e2e3",
        "secondary": "#c6c6c7",
        "tertiary-fixed-dim": "#c2c4e4",
        "on-tertiary-fixed": "#171a31",
        "inverse-surface": "#e2e2e3"
      },
      fontFamily: {
        "headline": ["Plus Jakarta Sans", "sans-serif"],
        "body": ["Manrope", "sans-serif"],
        "label": ["Manrope", "sans-serif"]
      },
      borderRadius: {
        "DEFAULT": "0.125rem",
        "lg": "0.25rem",
        "xl": "0.5rem",
        "full": "0.75rem"
      }
    }
  },
  plugins: [require("@tailwindcss/forms")]
};
