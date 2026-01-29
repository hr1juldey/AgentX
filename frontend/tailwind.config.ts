import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Organic UI design tokens (from C008)
        void: "#0A0A0A",        // Deep space background
        membrane: "#141414",     // Primary surface
        enzyme: "#00D9FF",       // Cyan accent
        cell: "#1E1E1E",        // Card backgrounds
        nucleus: "#FFFFFF",      // Primary text
        cytoplasm: "#A0A0A0",    // Secondary text
        vacuole: "#666666",      // Muted text
        mitochondria: "#FF6B35", // Action/warning
        ribosome: "#00D9FF",     // Enzyme (same)
        golgi: "#FFD700",        // Success
        lysosome: "#FF4757",     // Error
        endoplasmic: "#C792EA",  // Info
        microtubule: "#64FFDA",  // Success alt
        actin: "#82AAFF",        // Info alt
        myosin: "#FFCB6B",       // Warning alt
      },
      spacing: {
        // Spacing tokens (from C008)
        atom: "4px",
        molecule: "8px",
        organelle: "16px",
        cell: "24px",
        tissue: "32px",
        organ: "48px",
        system: "64px",
        organism: "96px",
        voice: "72px",       // Voice nucleus radius (mobile)
        voiceDesktop: "160px", // Voice nucleus radius (desktop)
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      keyframes: {
        "pulse-slow": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
        "drift": {
          "0%, 100%": { transform: "translateX(0)" },
          "50%": { transform: "translateX(10px)" },
        },
      },
      animation: {
        "pulse-slow": "pulse-slow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "drift": "drift 20s ease-in-out infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
