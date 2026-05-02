import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#111827",
        muted: "#6b7280",
        line: "#e5e7eb",
        panel: "#ffffff",
      },
      boxShadow: {
        panel: "0 1px 2px rgba(17, 24, 39, 0.06)",
      },
    },
  },
  plugins: [],
};

export default config;
