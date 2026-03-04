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
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
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
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#0f3460",
          600: "#0c2a4e",
          700: "#16213e",
          800: "#1a1a2e",
          900: "#0f0f1a",
        },
        accent: {
          DEFAULT: "#e94560",
          light: "#ff6b81",
          dark: "#c73e54",
        },
      },
      borderColor: {
        DEFAULT: "hsl(var(--border))",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      spacing: {
        1: "var(--space-1)",
        2: "var(--space-2)",
        3: "var(--space-3)",
        4: "var(--space-4)",
        5: "var(--space-5)",
        6: "var(--space-6)",
        8: "var(--space-8)",
        10: "var(--space-10)",
        12: "var(--space-12)",
      },
      boxShadow: {
        soft: "var(--elevation-1)",
        raised: "var(--elevation-2)",
        floating: "var(--elevation-3)",
      },
      transitionDuration: {
        fast: "var(--motion-fast)",
        DEFAULT: "var(--motion-base)",
        slow: "var(--motion-slow)",
      },
      transitionTimingFunction: {
        standard: "var(--ease-standard)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      fontSize: {
        xs: "var(--font-size-xs)",
        sm: "var(--font-size-sm)",
        base: "var(--font-size-md)",
        lg: "var(--font-size-lg)",
        xl: "var(--font-size-xl)",
        "2xl": "var(--font-size-2xl)",
        "3xl": "var(--font-size-3xl)",
      },
    },
  },
  plugins: [],
};

export default config;
