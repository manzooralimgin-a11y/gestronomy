"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Clock3, Filter } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatRelativeTime } from "@/lib/utils";
import { useDashboardStore, type ExceptionInboxItem } from "@/stores/dashboard-store";
import api from "@/lib/api";

const SEVERITY_ORDER: Record<string, number> = {
  critical: 0,
  warning: 1,
  info: 2,
};

const owners = ["All", "Finance", "Supply", "Service", "Kitchen", "Operations", "Growth"];

const SLA_OPTIONS = ["on_track", "at_risk", "breached", "resolved"];

function formatCountdown(totalSeconds: number): string {
  const abs = Math.abs(totalSeconds);
  const h = Math.floor(abs / 3600);
  const m = Math.floor((abs % 3600) / 60);
  const s = abs % 60;
  const base = `${h}h ${m}m ${s}s`;
  return totalSeconds < 0 ? `Overdue ${base}` : base;
}

function getSlaTone(item: ExceptionInboxItem, secondsRemaining: number | null): string {
  if (item.status === "resolved" || item.sla_status === "resolved") {
    return "text-muted-foreground";
  }
  if (item.sla_status === "breached" || (secondsRemaining != null && secondsRemaining <= 0)) {
    return "text-status-danger";
  }
  if (item.sla_status === "at_risk") {
    return "text-status-warning";
  }
  if (secondsRemaining != null && secondsRemaining <= Math.max(item.sla_minutes * 60 * 0.25, 300)) {
    return "text-status-warning";
  }
  return "text-status-success";
}

function ExceptionRow({
  item,
  onPersist,
}: {
  item: ExceptionInboxItem;
  onPersist: (id: number, patch: Partial<ExceptionInboxItem>) => void;
}) {
  const [saving, setSaving] = useState(false);
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const interval = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(interval);
  }, []);

  const patchException = async (payload: Record<string, unknown>) => {
    setSaving(true);
    try {
      const { data } = await api.patch(`/dashboard/exceptions/${item.id}`, payload);
      onPersist(item.id, data);
    } catch {
      // keep local state unchanged on failure
    } finally {
      setSaving(false);
    }
  };

  const setStatus = (nextStatus: "open" | "in_progress" | "resolved") => {
    patchException({
      status: nextStatus,
      action_taken:
        nextStatus === "in_progress"
          ? "Exception moved to in_progress from inbox"
          : nextStatus === "resolved"
          ? "Exception resolved from inbox"
          : "Exception reopened from inbox",
    });
  };

  const dueAtMs = item.due_at ? Date.parse(item.due_at) : null;
  const secondsRemaining = dueAtMs ? Math.floor((dueAtMs - now) / 1000) : null;
  const slaTone = getSlaTone(item, secondsRemaining);

  return (
    <div className="rounded-lg border border-border bg-card p-3 shadow-soft">
      <div className="mb-1 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Badge variant={item.severity === "critical" ? "destructive" : item.severity === "warning" ? "warning" : "default"}>
            {item.severity}
          </Badge>
          <span className="text-xs text-muted-foreground">{item.owner}</span>
        </div>
        <div className="text-xs text-muted-foreground">Impact {item.impact_score}</div>
      </div>
      <p className="text-sm font-semibold text-foreground">{item.title}</p>
      <p className="mt-1 text-xs text-muted-foreground">{item.message}</p>
      <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          <Clock3 className="h-3.5 w-3.5" />
          SLA {item.sla_minutes}m
        </div>
        <span className={slaTone}>
          {secondsRemaining == null ? formatRelativeTime(item.created_at) : formatCountdown(secondsRemaining)}
        </span>
      </div>
      <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-3">
        <select
          aria-label={`Assign owner for exception ${item.id}`}
          value={item.owner}
          disabled={saving}
          onChange={(event) => patchException({ owner: event.target.value })}
          className="rounded border border-border bg-card px-2 py-1 text-xs text-foreground focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-1"
        >
          {owners.slice(1).map((owner) => (
            <option key={owner} value={owner}>
              {owner}
            </option>
          ))}
        </select>
        <select
          aria-label={`Set SLA status for exception ${item.id}`}
          value={item.sla_status}
          disabled={saving}
          onChange={(event) => patchException({ sla_status: event.target.value })}
          className="rounded border border-border bg-card px-2 py-1 text-xs text-foreground focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-1"
        >
          {SLA_OPTIONS.map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>
        <div className="flex items-center gap-1">
          {item.status !== "in_progress" && item.status !== "resolved" && (
            <button
              type="button"
              aria-label={`Mark exception ${item.id} as in progress`}
              onClick={() => setStatus("in_progress")}
              disabled={saving}
              className="rounded bg-status-info-soft px-2 py-1 text-xs font-medium text-status-info transition-colors duration-fast ease-standard hover:bg-status-info-soft/70 focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-1"
            >
              In Progress
            </button>
          )}
          {item.status !== "resolved" && (
            <button
              type="button"
              aria-label={`Resolve exception ${item.id}`}
              onClick={() => setStatus("resolved")}
              disabled={saving}
              className="rounded bg-status-success-soft px-2 py-1 text-xs font-medium text-status-success transition-colors duration-fast ease-standard hover:bg-status-success-soft/70 focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-1"
            >
              Resolve
            </button>
          )}
          {item.status === "resolved" && (
            <button
              type="button"
              aria-label={`Reopen exception ${item.id}`}
              onClick={() => setStatus("open")}
              disabled={saving}
              className="rounded bg-muted px-2 py-1 text-xs font-medium text-muted-foreground transition-colors duration-fast ease-standard hover:bg-secondary focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-1"
            >
              Undo
            </button>
          )}
        </div>
      </div>
      {item.recommended_actions.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {item.recommended_actions.slice(0, 2).map((action) => (
            <span key={action} className="rounded bg-muted px-2 py-0.5 text-[11px] text-muted-foreground">
              {action}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export function ExceptionInbox() {
  const exceptions = useDashboardStore((s) => s.exceptions);
  const setExceptions = useDashboardStore((s) => s.setExceptions);
  const [severityFilter, setSeverityFilter] = useState<"all" | "critical" | "warning" | "info">("all");
  const [ownerFilter, setOwnerFilter] = useState("All");

  const applyPersistedChange = (id: number, patch: Partial<ExceptionInboxItem>) => {
    setExceptions(
      exceptions.map((item) =>
        item.id === id
          ? {
              ...item,
              ...patch,
            }
          : item
      )
    );
  };

  const filtered = useMemo(() => {
    return [...exceptions]
      .filter((item) => severityFilter === "all" || item.severity === severityFilter)
      .filter((item) => ownerFilter === "All" || item.owner === ownerFilter)
      .sort((a, b) => (SEVERITY_ORDER[a.severity] ?? 9) - (SEVERITY_ORDER[b.severity] ?? 9));
  }, [exceptions, severityFilter, ownerFilter]);

  return (
    <Card className="flex h-[460px] flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <AlertTriangle className="h-5 w-5 text-brand-500" />
            Exception Inbox
          </CardTitle>
          <Badge variant="secondary">{filtered.length}</Badge>
        </div>
        <div className="flex items-center gap-2 pt-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <div className="flex gap-1">
            {(["all", "critical", "warning", "info"] as const).map((level) => (
              <button
                key={level}
                type="button"
                aria-label={`Filter exceptions by ${level}`}
                onClick={() => setSeverityFilter(level)}
                className={`rounded px-2 py-1 text-xs transition-colors duration-fast ease-standard focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-1 ${severityFilter === level ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:bg-secondary"}`}
              >
                {level}
              </button>
            ))}
          </div>
          <select
            aria-label="Filter exceptions by owner"
            value={ownerFilter}
            onChange={(event) => setOwnerFilter(event.target.value)}
            className="ml-auto rounded border border-border bg-card px-2 py-1 text-xs text-muted-foreground focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-1"
          >
            {owners.map((owner) => (
              <option key={owner} value={owner}>
                {owner}
              </option>
            ))}
          </select>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden">
        <div className="h-full space-y-2 overflow-y-auto pr-1">
          {filtered.length === 0 ? (
            <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
              No matching exceptions.
            </div>
          ) : (
            filtered.map((item) => (
              <ExceptionRow
                key={`${item.source_type}-${item.id}`}
                item={item}
                onPersist={applyPersistedChange}
              />
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
