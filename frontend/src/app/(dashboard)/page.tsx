"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  BellRing,
  CalendarDays,
  Package,
  ReceiptText,
  Sparkles,
  Activity,
  Clock,
} from "lucide-react";
import api from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { useDashboardStore } from "@/stores/dashboard-store";
import { LiveMetrics } from "@/components/dashboard/live-metrics";
import { AgentActivityFeed } from "@/components/dashboard/agent-activity";
import { AlertsPanel } from "@/components/dashboard/alerts-panel";
import { AiChat } from "@/components/dashboard/ai-chat";
import { ExceptionInbox } from "@/components/dashboard/exception-inbox";
import { ExplainableAICards } from "@/components/dashboard/explainable-ai-cards";
import { AuditTimeline } from "@/components/dashboard/audit-timeline";
import { hasRoleAccess } from "@/lib/navigation";
import {
  MotionCard,
  MotionStagger,
  MotionSlideUp,
  MotionFadeIn,
  AnimatedCounter,
  StatusDot,
  staggerItem,
} from "@/components/ui/motion";
import { motion } from "framer-motion";

/* ── Types ── */
interface TodayStripData {
  reservationsToday: number | null;
  openOrders: number | null;
  lowStockItems: number | null;
  criticalAlerts: number;
}

interface FocusCard {
  title: string;
  description: string;
  href: string;
}

function formatToday() {
  return new Date().toISOString().slice(0, 10);
}

function getGreeting() {
  const h = new Date().getHours();
  if (h < 6) return "Good night";
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

function getTimeString() {
  return new Date().toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

/* ── Component ── */
export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const role = user?.role;
  const alerts = useDashboardStore((s) => s.alerts);
  const setKPIs = useDashboardStore((s) => s.setKPIs);
  const setAlerts = useDashboardStore((s) => s.setAlerts);
  const setAgentActivity = useDashboardStore((s) => s.setAgentActivity);
  const setExceptions = useDashboardStore((s) => s.setExceptions);
  const setRecommendations = useDashboardStore((s) => s.setRecommendations);
  const setAuditTimeline = useDashboardStore((s) => s.setAuditTimeline);
  const [time, setTime] = useState(getTimeString());
  const [todayStrip, setTodayStrip] = useState<TodayStripData>({
    reservationsToday: null,
    openOrders: null,
    lowStockItems: null,
    criticalAlerts: 0,
  });

  // Live clock
  useEffect(() => {
    const t = setInterval(() => setTime(getTimeString()), 30000);
    return () => clearInterval(t);
  }, []);

  // Fetch dashboard data
  useEffect(() => {
    api.get("/dashboard/kpis").then(({ data }) => setKPIs(data)).catch(() => {});
    api.get("/dashboard/alerts").then(({ data }) => setAlerts(data)).catch(() => {});
    api.get("/dashboard/activity").then(({ data }) => setAgentActivity(data)).catch(() => {});
    api.get("/dashboard/exceptions").then(({ data }) => setExceptions(data)).catch(() => {});
    api.get("/dashboard/recommendations").then(({ data }) => setRecommendations(data)).catch(() => {});
    api.get("/dashboard/audit-timeline").then(({ data }) => setAuditTimeline(data)).catch(() => {});
  }, [setKPIs, setAlerts, setAgentActivity, setExceptions, setRecommendations, setAuditTimeline]);

  useEffect(() => {
    setTodayStrip((prev) => ({
      ...prev,
      criticalAlerts: alerts.filter((a) => a.severity === "critical" && !a.is_read).length,
    }));
  }, [alerts]);

  useEffect(() => {
    api.get("/reservations", { params: { reservation_date: formatToday() } })
      .then(({ data }) => setTodayStrip((p) => ({ ...p, reservationsToday: Array.isArray(data) ? data.length : 0 })))
      .catch(() => setTodayStrip((p) => ({ ...p, reservationsToday: null })));

    api.get("/billing/orders")
      .then(({ data }) => setTodayStrip((p) => ({ ...p, openOrders: Array.isArray(data) ? data.length : 0 })))
      .catch(() => setTodayStrip((p) => ({ ...p, openOrders: null })));

    if (hasRoleAccess(role, "manager")) {
      api.get("/inventory/low-stock")
        .then(({ data }) => setTodayStrip((p) => ({ ...p, lowStockItems: Array.isArray(data) ? data.length : 0 })))
        .catch(() => setTodayStrip((p) => ({ ...p, lowStockItems: null })));
    }
  }, [role]);

  const focusCards = useMemo<FocusCard[]>(() => {
    if (role === "admin") {
      return [
        { title: "Financial Control", description: "Track top line, margin risk, and exceptions.", href: "/reports" },
        { title: "Agent Oversight", description: "Review agent actions and approve sensitive changes.", href: "/agents" },
        { title: "Franchise Intelligence", description: "Compare locations and replication opportunities.", href: "/franchise" },
      ];
    }
    if (role === "manager") {
      return [
        { title: "Service Operations", description: "Seat, pace, and close service faster.", href: "/reservations" },
        { title: "Inventory Action", description: "Review low stock and raise purchase orders.", href: "/inventory" },
        { title: "Guest Retention", description: "Find churn-risk guests and trigger recovery.", href: "/guests" },
      ];
    }
    return [
      { title: "Live Floor View", description: "Reservations, walk-ins, and table status.", href: "/reservations" },
      { title: "Open Orders", description: "Track active bills and close checks.", href: "/billing" },
      { title: "Kitchen Queue", description: "Prep status and handoff timing.", href: "/kitchen" },
    ];
  }, [role]);

  const systemHealthy = todayStrip.criticalAlerts === 0;
  const firstName = user?.full_name?.split(" ")[0] || "there";

  return (
    <div className="space-y-8">
      {/* ═══ Hero Section ═══ */}
      <MotionFadeIn>
        <div className="relative">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <h1 className="text-3xl font-bold text-foreground tracking-tight">
                {getGreeting()}, <span className="text-glow">{firstName}</span>
              </h1>
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <span className="flex items-center gap-1.5">
                  <Clock className="h-3.5 w-3.5" />
                  {time}
                </span>
                <span className="text-white/10">|</span>
                <span className="flex items-center gap-1.5">
                  <StatusDot status={systemHealthy ? "success" : "warning"} pulse={!systemHealthy} />
                  {systemHealthy ? "All systems nominal" : `${todayStrip.criticalAlerts} alert${todayStrip.criticalAlerts > 1 ? "s" : ""} need attention`}
                </span>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-2 text-xs text-muted-foreground/50">
              <Activity className="h-3 w-3" />
              <span>Command Center</span>
            </div>
          </div>
        </div>
      </MotionFadeIn>

      {/* ═══ Metric Strip — Glass cards with animated counters ═══ */}
      <MotionStagger className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {/* Reservations */}
        <motion.div variants={staggerItem}>
          <div className="glass-card p-4 group">
            <div className="flex items-center gap-2 mb-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10">
                <CalendarDays className="h-4 w-4 text-blue-400" />
              </div>
              <span className="text-xs font-medium text-muted-foreground">Reservations Today</span>
            </div>
            <AnimatedCounter
              value={todayStrip.reservationsToday}
              className="text-2xl font-bold text-foreground"
            />
          </div>
        </motion.div>

        {/* Open Orders */}
        <motion.div variants={staggerItem}>
          <div className="glass-card p-4 group">
            <div className="flex items-center gap-2 mb-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10">
                <ReceiptText className="h-4 w-4 text-emerald-400" />
              </div>
              <span className="text-xs font-medium text-muted-foreground">Open Orders</span>
            </div>
            <AnimatedCounter
              value={todayStrip.openOrders}
              className="text-2xl font-bold text-foreground"
            />
          </div>
        </motion.div>

        {/* Low Stock */}
        <motion.div variants={staggerItem}>
          <div className="glass-card p-4 group">
            <div className="flex items-center gap-2 mb-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-500/10">
                <Package className="h-4 w-4 text-purple-400" />
              </div>
              <span className="text-xs font-medium text-muted-foreground">Low Stock Items</span>
            </div>
            <AnimatedCounter
              value={todayStrip.lowStockItems}
              className="text-2xl font-bold text-foreground"
            />
          </div>
        </motion.div>

        {/* Critical Alerts */}
        <motion.div variants={staggerItem}>
          <div className={`glass-card p-4 group ${todayStrip.criticalAlerts > 0 ? "pulse-danger border-red-500/30" : ""}`}>
            <div className="flex items-center gap-2 mb-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-500/10">
                <BellRing className="h-4 w-4 text-red-400" />
              </div>
              <span className="text-xs font-medium text-muted-foreground">Critical Alerts</span>
            </div>
            <AnimatedCounter
              value={todayStrip.criticalAlerts}
              className={`text-2xl font-bold ${todayStrip.criticalAlerts > 0 ? "text-red-400" : "text-foreground"}`}
            />
          </div>
        </motion.div>
      </MotionStagger>

      {/* ═══ AI Focus Cards — Staggered entrance ═══ */}
      <MotionStagger className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {focusCards.map((card) => (
          <motion.div key={card.title} variants={staggerItem}>
            <Link href={card.href} className="block group">
              <div className="glass-card p-5 h-full transition-all duration-300 hover:glow-border">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="h-4 w-4 text-emerald-400/60" />
                  <span className="text-[10px] font-semibold uppercase tracking-[0.15em] text-emerald-400/60">
                    AI Recommended
                  </span>
                </div>
                <h3 className="text-lg font-bold text-foreground mb-1">{card.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{card.description}</p>
                <div className="mt-4 flex items-center gap-1.5 text-sm font-medium text-primary">
                  <span>Open</span>
                  <ArrowRight className="h-3.5 w-3.5 transition-transform duration-200 group-hover:translate-x-1" />
                </div>
              </div>
            </Link>
          </motion.div>
        ))}
      </MotionStagger>

      {/* ═══ Live Metrics ═══ */}
      <MotionSlideUp delay={0.2}>
        <LiveMetrics />
      </MotionSlideUp>

      {/* ═══ Activity + Alerts ═══ */}
      <MotionSlideUp delay={0.3} className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <AgentActivityFeed />
        </div>
        <div className="lg:col-span-1">
          <AlertsPanel />
        </div>
      </MotionSlideUp>

      {/* ═══ Exceptions + AI + Audit ═══ */}
      <MotionSlideUp delay={0.4} className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="xl:col-span-1">
          <ExceptionInbox />
        </div>
        <div className="xl:col-span-1">
          <ExplainableAICards />
        </div>
        <div className="xl:col-span-1">
          <AuditTimeline />
        </div>
      </MotionSlideUp>

      {/* ═══ AI Chat ═══ */}
      <MotionSlideUp delay={0.5}>
        <AiChat />
      </MotionSlideUp>
    </div>
  );
}
