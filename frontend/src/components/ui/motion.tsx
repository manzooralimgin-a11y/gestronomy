"use client";

import { motion, AnimatePresence, type Variants } from "framer-motion";
import { useEffect, useState, useRef } from "react";
import { cn } from "@/lib/utils";

/* ═══════════════════════════════════════
   ANIMATION VARIANTS
   ═══════════════════════════════════════ */
export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.3, ease: [0.2, 0.8, 0.2, 1] } },
};

export const slideUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.2, 0.8, 0.2, 1] } },
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.25, ease: [0.2, 0.8, 0.2, 1] } },
};

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.06, delayChildren: 0.1 },
  },
};

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.2, 0.8, 0.2, 1] } },
};

/* ═══════════════════════════════════════
   MOTION CARD — Glass card with hover lift
   ═══════════════════════════════════════ */
interface MotionCardProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  glowOnHover?: boolean;
}

export function MotionCard({ children, className, delay = 0, glowOnHover = false }: MotionCardProps) {
  return (
    <motion.div
      variants={staggerItem}
      initial="hidden"
      animate="visible"
      transition={{ delay }}
      whileHover={{ y: -3, transition: { duration: 0.2 } }}
      className={cn(
        "glass-card p-5",
        glowOnHover && "hover:glow-border",
        className
      )}
    >
      {children}
    </motion.div>
  );
}

/* ═══════════════════════════════════════
   MOTION STAGGER — Staggered children
   ═══════════════════════════════════════ */
interface MotionStaggerProps {
  children: React.ReactNode;
  className?: string;
}

export function MotionStagger({ children, className }: MotionStaggerProps) {
  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ═══════════════════════════════════════
   MOTION FADE IN
   ═══════════════════════════════════════ */
interface MotionFadeInProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}

export function MotionFadeIn({ children, className, delay = 0 }: MotionFadeInProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3, delay, ease: [0.2, 0.8, 0.2, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ═══════════════════════════════════════
   MOTION SLIDE UP
   ═══════════════════════════════════════ */
interface MotionSlideUpProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}

export function MotionSlideUp({ children, className, delay = 0 }: MotionSlideUpProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: [0.2, 0.8, 0.2, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ═══════════════════════════════════════
   ANIMATED COUNTER — Number count-up
   ═══════════════════════════════════════ */
interface AnimatedCounterProps {
  value: number | null | undefined;
  duration?: number;
  prefix?: string;
  suffix?: string;
  className?: string;
  decimals?: number;
}

export function AnimatedCounter({
  value,
  duration = 1.2,
  prefix = "",
  suffix = "",
  className,
  decimals = 0,
}: AnimatedCounterProps) {
  const [display, setDisplay] = useState(0);
  const animFrame = useRef<number>(0);
  const startTime = useRef<number>(0);

  useEffect(() => {
    if (value === null || value === undefined) return;
    const target = value;
    const start = display;

    startTime.current = Date.now();
    const animate = () => {
      const elapsed = (Date.now() - startTime.current) / 1000;
      const progress = Math.min(elapsed / duration, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = start + (target - start) * eased;
      setDisplay(current);

      if (progress < 1) {
        animFrame.current = requestAnimationFrame(animate);
      }
    };

    animFrame.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animFrame.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value, duration]);

  if (value === null || value === undefined) {
    return <span className={className}>—</span>;
  }

  return (
    <span className={cn("tabular-nums font-mono", className)}>
      {prefix}{decimals > 0 ? display.toFixed(decimals) : Math.round(display)}{suffix}
    </span>
  );
}

/* ═══════════════════════════════════════
   STATUS DOT — Animated status indicator
   ═══════════════════════════════════════ */
interface StatusDotProps {
  status: "success" | "warning" | "danger" | "info" | "neutral";
  pulse?: boolean;
  size?: "sm" | "md";
}

export function StatusDot({ status, pulse = false, size = "sm" }: StatusDotProps) {
  const colors: Record<string, string> = {
    success: "bg-emerald-400",
    warning: "bg-amber-400",
    danger: "bg-red-400",
    info: "bg-blue-400",
    neutral: "bg-gray-400",
  };

  const glowColors: Record<string, string> = {
    success: "shadow-[0_0_8px_rgba(52,211,153,0.6)]",
    warning: "shadow-[0_0_8px_rgba(251,191,36,0.6)]",
    danger: "shadow-[0_0_8px_rgba(248,113,113,0.6)]",
    info: "shadow-[0_0_8px_rgba(96,165,250,0.6)]",
    neutral: "",
  };

  const sizeClass = size === "sm" ? "h-2 w-2" : "h-2.5 w-2.5";

  return (
    <span className="relative flex items-center">
      <span
        className={cn(
          "rounded-full",
          sizeClass,
          colors[status],
          glowColors[status],
          pulse && "animate-pulse"
        )}
      />
    </span>
  );
}

export { motion, AnimatePresence };
