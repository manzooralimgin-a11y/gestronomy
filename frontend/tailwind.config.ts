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
        background: "var(--background)",
        foreground: "var(--foreground)",
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
        status: {
          danger: "hsl(var(--status-danger))",
          "danger-soft": "hsl(var(--status-danger-soft))",
          warning: "hsl(var(--status-warning))",
          "warning-soft": "hsl(var(--status-warning-soft))",
          success: "hsl(var(--status-success))",
          "success-soft": "hsl(var(--status-success-soft))",
          info: "hsl(var(--status-info))",
          "info-soft": "hsl(var(--status-info-soft))",
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
          DEFAULT: "var(--sidebar)",
          foreground: "var(--sidebar-foreground)",
          primary: "var(--sidebar-primary)",
          "primary-foreground": "var(--sidebar-primary-foreground)",
          accent: "var(--sidebar-accent)",
          "accent-foreground": "var(--sidebar-accent-foreground)",
          border: "var(--sidebar-border)",
          ring: "var(--sidebar-ring)",
        },
        brand: {
          50: "#ecfdf5",
          100: "#d1fae5",
          200: "#a7f3d0",
          300: "#6ee7b7",
          400: "#34d399",
          500: "#1a9d6c",
          600: "#148a5e",
          700: "#0f6b49",
          800: "#0a4d34",
          900: "#052e1f",
        },
        glow: {
          primary: "hsl(var(--glow-primary))",
          cyan: "hsl(var(--glow-cyan))",
          purple: "hsl(var(--glow-purple))",
          amber: "hsl(var(--glow-amber))",
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
      spacing: {
        "0.5": "var(--space-0\\.5)",
        1: "var(--space-1)",
        "1.5": "var(--space-1\\.5)",
        2: "var(--space-2)",
        3: "var(--space-3)",
        4: "var(--space-4)",
        5: "var(--space-5)",
        6: "var(--space-6)",
        8: "var(--space-8)",
        10: "var(--space-10)",
        12: "var(--space-12)",
        16: "var(--space-16)",
      },
      boxShadow: {
        soft: "var(--elevation-1)",
        raised: "var(--elevation-2)",
        floating: "var(--elevation-3)",
        dramatic: "var(--elevation-4)",
        glow: "0 0 12px -2px hsl(var(--glow-primary) / 0.35)",
        "glow-sm": "0 0 8px -3px hsl(var(--glow-primary) / 0.2)",
        "glow-lg": "0 0 24px -4px hsl(var(--glow-primary) / 0.3)",
        "glow-cyan": "0 0 12px -2px hsl(var(--glow-cyan) / 0.3)",
        "glow-purple": "0 0 12px -2px hsl(var(--glow-purple) / 0.3)",
        "glow-amber": "0 0 12px -2px hsl(var(--glow-amber) / 0.3)",
        "inner-glow": "inset 0 1px 0 0 hsl(var(--glass-highlight))",
      },
      transitionDuration: {
        fast: "var(--motion-fast)",
        DEFAULT: "var(--motion-base)",
        slow: "var(--motion-slow)",
        slower: "var(--motion-slower)",
      },
      transitionTimingFunction: {
        standard: "var(--ease-standard)",
        bounce: "var(--ease-bounce)",
        spring: "var(--ease-spring)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      fontSize: {
        xs: ["var(--font-size-xs)", { lineHeight: "1.5" }],
        sm: ["var(--font-size-sm)", { lineHeight: "1.5" }],
        base: ["var(--font-size-md)", { lineHeight: "1.6" }],
        lg: ["var(--font-size-lg)", { lineHeight: "1.5" }],
        xl: ["var(--font-size-xl)", { lineHeight: "1.4" }],
        "2xl": ["var(--font-size-2xl)", { lineHeight: "1.3" }],
        "3xl": ["var(--font-size-3xl)", { lineHeight: "1.2" }],
        "4xl": ["var(--font-size-4xl)", { lineHeight: "1.1" }],
      },
      animation: {
        shimmer: "shimmer 1.8s ease-in-out infinite",
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
        "pulse-glow-primary": "pulse-glow-primary 2.5s ease-in-out infinite",
        float: "float 3s ease-in-out infinite",
        breathe: "breathe 3s ease-in-out infinite",
        "dot-pulse": "dot-pulse 1.5s ease-in-out infinite",
        "fade-in": "fade-in 0.3s ease-out forwards",
        "slide-up": "slide-up 0.4s cubic-bezier(0.2, 0.8, 0.2, 1) forwards",
        "slide-in-right": "slide-in-right 0.3s var(--ease-spring) forwards",
        "slide-in-bottom": "slide-in-bottom 0.3s var(--ease-spring) forwards",
        "scale-in": "scale-in 0.2s cubic-bezier(0.2, 0.8, 0.2, 1) forwards",
        "scale-bounce": "scale-bounce 0.35s var(--ease-bounce) forwards",
        "spin-slow": "spin-slow 8s linear infinite",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
