"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, BellRing, CalendarDays, Package, ReceiptText, Sparkles } from "lucide-react";
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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { hasRoleAccess } from "@/lib/navigation";

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
  const [todayStrip, setTodayStrip] = useState<TodayStripData>({
    reservationsToday: null,
    openOrders: null,
    lowStockItems: null,
    criticalAlerts: 0,
  });

  useEffect(() => {
    api.get("/dashboard/kpis").then(({ data }) => setKPIs(data)).catch(() => {});
    api.get("/dashboard/alerts").then(({ data }) => setAlerts(data)).catch(() => {});
    api.get("/dashboard/activity").then(({ data }) => setAgentActivity(data)).catch(() => {});
    api.get("/dashboard/exceptions").then(({ data }) => setExceptions(data)).catch(() => {});
    api.get("/dashboard/recommendations").then(({ data }) => setRecommendations(data)).catch(() => {});
    api.get("/dashboard/audit-timeline").then(({ data }) => setAuditTimeline(data)).catch(() => {});
  }, [
    setKPIs,
    setAlerts,
    setAgentActivity,
    setExceptions,
    setRecommendations,
    setAuditTimeline,
  ]);

  useEffect(() => {
    setTodayStrip((prev) => ({
      ...prev,
      criticalAlerts: alerts.filter((a) => a.severity === "critical" && !a.is_read).length,
    }));
  }, [alerts]);

  useEffect(() => {
    api
      .get("/reservations", { params: { reservation_date: formatToday() } })
      .then(({ data }) =>
        setTodayStrip((prev) => ({
          ...prev,
          reservationsToday: Array.isArray(data) ? data.length : 0,
        }))
      )
      .catch(() =>
        setTodayStrip((prev) => ({
          ...prev,
          reservationsToday: null,
        }))
      );

    api
      .get("/billing/orders")
      .then(({ data }) =>
        setTodayStrip((prev) => ({
          ...prev,
          openOrders: Array.isArray(data) ? data.length : 0,
        }))
      )
      .catch(() =>
        setTodayStrip((prev) => ({
          ...prev,
          openOrders: null,
        }))
      );

    if (hasRoleAccess(role, "manager")) {
      api
        .get("/inventory/low-stock")
        .then(({ data }) =>
          setTodayStrip((prev) => ({
            ...prev,
            lowStockItems: Array.isArray(data) ? data.length : 0,
          }))
        )
        .catch(() =>
          setTodayStrip((prev) => ({
            ...prev,
            lowStockItems: null,
          }))
        );
    }
  }, [role]);

  const focusCards = useMemo<FocusCard[]>(() => {
    if (role === "admin") {
      return [
        {
          title: "Financial Control",
          description: "Track top line, margin risk, and exceptions.",
          href: "/reports",
        },
        {
          title: "Agent Oversight",
          description: "Review agent actions and approve sensitive changes.",
          href: "/agents",
        },
        {
          title: "Franchise Intelligence",
          description: "Compare locations and identify replication opportunities.",
          href: "/franchise",
        },
      ];
    }
    if (role === "manager") {
      return [
        {
          title: "Service Operations",
          description: "Seat, pace, and close service faster with fewer bottlenecks.",
          href: "/reservations",
        },
        {
          title: "Inventory Action",
          description: "Review low stock and raise purchase orders before shift.",
          href: "/inventory",
        },
        {
          title: "Guest Retention",
          description: "Find churn-risk guests and trigger recovery campaigns.",
          href: "/guests",
        },
      ];
    }
    return [
      {
        title: "Live Floor View",
        description: "See today reservations, walk-ins, and table status at a glance.",
        href: "/reservations",
      },
      {
        title: "Open Orders",
        description: "Track active bills and close checks without switching screens.",
        href: "/billing",
      },
      {
        title: "Kitchen Queue",
        description: "Watch prep status and handoff timing in real time.",
        href: "/kitchen",
      },
    ];
  }, [role]);

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold text-foreground">Command Center</h1>
        <p className="text-sm text-muted-foreground">
          Prioritized for your role so the next right action is always obvious.
        </p>
      </div>

      <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Card className="border-brand-100">
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <CalendarDays className="h-4 w-4 text-brand-500" />
              Reservations Today
            </CardDescription>
            <CardTitle className="text-2xl">{todayStrip.reservationsToday ?? "-"}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <ReceiptText className="h-4 w-4 text-brand-500" />
              Open Orders
            </CardDescription>
            <CardTitle className="text-2xl">{todayStrip.openOrders ?? "-"}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <Package className="h-4 w-4 text-brand-500" />
              Low Stock Items
            </CardDescription>
            <CardTitle className="text-2xl">{todayStrip.lowStockItems ?? "-"}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="border-status-danger/20 bg-status-danger-soft">
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <BellRing className="h-4 w-4 text-status-danger" />
              Critical Alerts
            </CardDescription>
            <CardTitle className="text-2xl text-status-danger">{todayStrip.criticalAlerts}</CardTitle>
          </CardHeader>
        </Card>
      </section>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {focusCards.map((card) => (
          <Link key={card.title} href={card.href}>
            <Card className="h-full transition hover:border-brand-300 hover:shadow-md">
              <CardHeader>
                <CardDescription className="flex items-center gap-2 text-brand-600">
                  <Sparkles className="h-4 w-4" />
                  Recommended Focus
                </CardDescription>
                <CardTitle className="text-xl">{card.title}</CardTitle>
                <CardContent className="px-0 pb-0 pt-1">
                  <p className="text-sm text-muted-foreground">{card.description}</p>
                  <div className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-brand-600">
                    Open
                    <ArrowRight className="h-4 w-4" />
                  </div>
                </CardContent>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </section>

      <LiveMetrics />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <AgentActivityFeed />
        </div>
        <div className="lg:col-span-1">
          <AlertsPanel />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="xl:col-span-1">
          <ExceptionInbox />
        </div>
        <div className="xl:col-span-1">
          <ExplainableAICards />
        </div>
        <div className="xl:col-span-1">
          <AuditTimeline />
        </div>
      </div>

      <AiChat />
    </div>
  );
}
