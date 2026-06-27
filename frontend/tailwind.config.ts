import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        mist: "#f4f7f6",
        moss: "#597568",
        brass: "#b58b35",
        coral: "#c85f4a",
        ocean: "#1f6f8b"
      }
    }
  },
  plugins: []
};

export default config;

