import path from "path";
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    path.join(__dirname, "src/**/*.{ts,tsx}"),
  ],
  theme: {
    extend: {
      colors: {
        border: "var(--border)",
        background: {
          DEFAULT: "var(--background)",
          subtle: "var(--background-subtle)",
          muted: "var(--background-muted)",
        },
        foreground: {
          DEFAULT: "var(--foreground)",
          muted: "var(--foreground-muted)",
          dim: "var(--foreground-dim)",
        },
        primary: {
          DEFAULT: "var(--primary)",
          foreground: "var(--primary-foreground)",
        },
        secondary: {
          DEFAULT: "var(--secondary)",
          foreground: "var(--secondary-foreground)",
        },
        muted: {
          DEFAULT: "var(--muted)",
          foreground: "var(--muted-foreground)",
        },
        accent: {
          DEFAULT: "var(--accent)",
          foreground: "var(--accent-foreground)",
        },
        destructive: {
          DEFAULT: "var(--destructive)",
        },
        gold: {
          DEFAULT: "var(--gold)",
          hover: "var(--gold-hover)",
          dim: "var(--gold-dim)",
          bg: "var(--gold-bg)",
          border: "var(--gold-border)",
        },
        forest: {
          DEFAULT: "var(--forest)",
          hover: "var(--forest-hover)",
        },
        emerald: "var(--emerald)",
        status: {
          success: "var(--status-success)",
          "success-soft": "var(--status-success-soft)",
          warning: "var(--status-warning)",
          "warning-soft": "var(--status-warning-soft)",
          danger: "var(--status-danger)",
          "danger-soft": "var(--status-danger-soft)",
          info: "var(--status-info)",
          "info-soft": "var(--status-info-soft)",
        },
        card: {
          DEFAULT: "var(--card)",
          foreground: "var(--card-foreground)",
        },
        popover: {
          DEFAULT: "var(--popover)",
          foreground: "var(--popover-foreground)",
        },
        sidebar: {
          DEFAULT: "var(--sidebar-bg)",
          border: "var(--sidebar-border)",
        },
      },
      borderColor: {
        DEFAULT: "var(--border)",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
        xl: "calc(var(--radius) + 4px)",
        "2xl": "calc(var(--radius) + 8px)",
        "3xl": "calc(var(--radius) + 14px)",
      },
      boxShadow: {
        glass: "var(--glass-shadow)",
        "glass-hover": "var(--glass-shadow-hover)",
        elevated: "var(--glass-elevated-shadow)",
        soft: "0 1px 3px rgba(0,0,0,0.08)",
        raised: "0 4px 12px rgba(0,0,0,0.12)",
        floating: "0 12px 32px rgba(0,0,0,0.16)",
        dramatic: "0 24px 48px rgba(0,0,0,0.24)",
      },
      transitionDuration: {
        fast: "var(--motion-fast)",
        DEFAULT: "var(--motion-base)",
        slow: "var(--motion-slow)",
        slower: "var(--motion-slower)",
      },
      transitionTimingFunction: {
        editorial: "var(--ease-editorial)",
        standard: "var(--ease-standard)",
      },
      fontFamily: {
        editorial: ["var(--font-editorial)", "Georgia", "serif"],
        body: ["var(--font-body)", "system-ui", "sans-serif"],
        sans: ["var(--font-body)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains)", "Fira Code", "monospace"],
      },
      fontSize: {
        xs: ["0.75rem", { lineHeight: "1.5" }],
        sm: ["0.8125rem", { lineHeight: "1.5" }],
        base: ["0.9375rem", { lineHeight: "1.6" }],
        lg: ["1.0625rem", { lineHeight: "1.5" }],
        xl: ["1.25rem", { lineHeight: "1.4" }],
        "2xl": ["1.5rem", { lineHeight: "1.3" }],
        "3xl": ["1.875rem", { lineHeight: "1.2" }],
        "4xl": ["2.25rem", { lineHeight: "1.1" }],
        "5xl": ["3rem", { lineHeight: "1.05" }],
        "6xl": ["3.75rem", { lineHeight: "1" }],
        "7xl": ["4.5rem", { lineHeight: "0.95" }],
      },
      animation: {
        shimmer: "shimmer 2s ease-in-out infinite",
        "gold-shimmer": "gold-shimmer 4s ease-in-out infinite",
        "pulse-subtle": "pulse-subtle 2.5s ease-in-out infinite",
        float: "float 4s ease-in-out infinite",
        breathe: "breathe 3s ease-in-out infinite",
        "fade-in": "fade-in 0.3s var(--ease-editorial) forwards",
        "slide-up": "slide-up 0.5s var(--ease-editorial) forwards",
        "scale-in": "scale-in 0.25s var(--ease-editorial) forwards",
        "scale-bounce": "scale-bounce 0.35s var(--ease-editorial) forwards",
        "orb-drift": "orb-drift 20s ease-in-out infinite",
        "spin-slow": "spin-slow 8s linear infinite",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-up": {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.96)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
