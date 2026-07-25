import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        clay: {
          bg: "#f5f5f4",
          card: "#ffffff",
          primary: "#78350f",
          accent: "#b45309",
          text: "#1c1917",
          muted: "#78716c",
          border: "#d6d3d1",
        },
      },
      borderRadius: {
        clay: "28px",
        "clay-sm": "18px",
      },
    },
  },
  plugins: [],
};
export default config;
