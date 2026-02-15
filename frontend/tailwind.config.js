export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          200: "#bae6fd",
          400: "#38bdf8",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
          900: "#0c4a6e",
        },
      },
      boxShadow: {
        surface: "0 10px 30px rgba(2, 8, 23, 0.06)",
        float: "0 25px 60px rgba(2, 8, 23, 0.12)",
        glow: "0 0 0 1px rgba(255,255,255,.6), 0 20px 60px rgba(14,165,233,.15)",
      },
      borderRadius: {
        xl: "14px",
        "2xl": "18px",
        "3xl": "26px",
      },
    },
  },
  plugins: [],
};
