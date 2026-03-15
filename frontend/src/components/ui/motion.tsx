"use client";

import { motion, AnimatePresence, type Variants } from "framer-motion";
import { useEffect, useState, useRef } from "react";
import { cn } from "@/lib/utils";

/* ═══════════════════════════════════════
   EDITORIAL ANIMATION SYSTEM
   All animations are scroll-triggered
   ═══════════════════════════════════════ */

const EDITORIAL_EASE = [0.16, 1, 0.3, 1] as const;

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.5, ease: EDITORIAL_EASE } },
};

export const slideUp: Variants = {
  hidden: { opacity: 0, y: 28 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.7, ease: EDITORIAL_EASE } },
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.96 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.5, ease: EDITORIAL_EASE } },
};

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
};

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: EDITORIAL_EASE } },
};

/* ═══════════════════════════════════════
   SCROLL REVEAL — Core scroll-triggered wrapper
   ═══════════════════════════════════════ */
interface ScrollRevealProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  direction?: "up" | "down" | "left" | "right" | "none";
  distance?: number;
}

export function ScrollReveal({
  children,
  className,
  delay = 0,
  direction = "up",
  distance = 28,
}: ScrollRevealProps) {
  const initial: Record<string, number> = { opacity: 0 };
  const animate: Record<string, number> = { opacity: 1 };

  if (direction === "up") { initial.y = distance; animate.y = 0; }
  else if (direction === "down") { initial.y = -distance; animate.y = 0; }
  else if (direction === "left") { initial.x = distance; animate.x = 0; }
  else if (direction === "right") { initial.x = -distance; animate.x = 0; }

  return (
    <motion.div
      initial={initial}
      whileInView={animate}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.7, delay, ease: EDITORIAL_EASE }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ═══════════════════════════════════════
   MOTION CARD — Glass card with subtle hover
   ═══════════════════════════════════════ */
interface MotionCardProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  glowOnHover?: boolean;
}

export function MotionCard({ children, className, delay = 0 }: MotionCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.6, delay, ease: EDITORIAL_EASE }}
      whileHover={{ scale: 1.01, transition: { duration: 0.2 } }}
      className={cn("glass-card p-5", className)}
    >
      {children}
    </motion.div>
  );
}

/* ═══════════════════════════════════════
   MOTION STAGGER — Scroll-triggered stagger
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
      whileInView="visible"
      viewport={{ once: true, margin: "-60px" }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ═══════════════════════════════════════
   MOTION FADE IN — Scroll-triggered
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
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay, ease: EDITORIAL_EASE }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ═══════════════════════════════════════
   MOTION SLIDE UP — Scroll-triggered
   ═══════════════════════════════════════ */
interface MotionSlideUpProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}

export function MotionSlideUp({ children, className, delay = 0 }: MotionSlideUpProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 28 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.7, delay, ease: EDITORIAL_EASE }}
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
  duration = 1.4,
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
    success: "bg-status-success",
    warning: "bg-status-warning",
    danger: "bg-status-danger",
    info: "bg-status-info",
    neutral: "bg-foreground-dim",
  };

  const glowColors: Record<string, string> = {
    success: "shadow-[0_0_8px_var(--status-success)]",
    warning: "shadow-[0_0_8px_var(--status-warning)]",
    danger: "shadow-[0_0_8px_var(--status-danger)]",
    info: "shadow-[0_0_8px_var(--status-info)]",
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
