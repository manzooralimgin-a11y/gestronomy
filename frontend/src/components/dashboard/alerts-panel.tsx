"use client";

import { AlertTriangle, Info, X, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useDashboardStore, type AlertItem } from "@/stores/dashboard-store";
import { formatRelativeTime, cn } from "@/lib/utils";

const SEVERITY_CONFIG: Record<
  string,
  { color: string; badgeVariant: "destructive" | "warning" | "default"; icon: typeof AlertTriangle }
> = {
  critical: {
    color: "border-l-red-500",
    badgeVariant: "destructive",
    icon: AlertCircle,
  },
  warning: {
    color: "border-l-yellow-500",
    badgeVariant: "warning",
    icon: AlertTriangle,
  },
  info: {
    color: "border-l-blue-500",
    badgeVariant: "default",
    icon: Info,
  },
};

const SEVERITY_ORDER: Record<string, number> = {
  critical: 0,
  warning: 1,
  info: 2,
};

function AlertRow({
  alert,
  onDismiss,
}: {
  alert: AlertItem;
  onDismiss: (id: number) => void;
}) {
  const config = SEVERITY_CONFIG[alert.severity] || SEVERITY_CONFIG.info;
  const Icon = config.icon;

  return (
    <div
      className={cn(
        "flex items-start gap-3 border-l-4 rounded-r-md bg-[hsl(var(--glass-highlight))] p-3 transition-colors hover:bg-[hsl(var(--glass-border))]",
        config.color,
        alert.is_read && "opacity-60"
      )}
    >
      <Icon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <Badge variant={config.badgeVariant} className="text-[10px]">
            {alert.severity}
          </Badge>
          <span className="truncate text-sm font-medium text-foreground">
            {alert.title}
          </span>
        </div>
        <p className="mt-1 text-xs text-muted-foreground">{alert.message}</p>
        <p className="mt-1 text-xs text-muted-foreground/60">
          {formatRelativeTime(alert.created_at)}
        </p>
      </div>
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6 shrink-0"
        onClick={() => onDismiss(alert.id)}
      >
        <X className="h-3 w-3" />
      </Button>
    </div>
  );
}

export function AlertsPanel() {
  const alerts = useDashboardStore((s) => s.alerts);
  const markAlertRead = useDashboardStore((s) => s.markAlertRead);

  const sortedAlerts = [...alerts]
    .filter((a) => !a.is_read)
    .sort(
      (a, b) =>
        (SEVERITY_ORDER[a.severity] ?? 3) - (SEVERITY_ORDER[b.severity] ?? 3)
    );

  return (
    <Card className="flex h-[400px] flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <AlertTriangle className="h-5 w-5 text-brand-500" />
            Active Alerts
          </CardTitle>
          {sortedAlerts.length > 0 && (
            <Badge variant="secondary" className="text-xs">
              {sortedAlerts.length}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden p-0">
        <div className="h-full overflow-y-auto px-6 pb-4">
          {sortedAlerts.length === 0 ? (
            <div className="flex h-full items-center justify-center">
              <p className="text-sm text-muted-foreground/60">No active alerts</p>
            </div>
          ) : (
            <div className="space-y-2">
              {sortedAlerts.map((alert) => (
                <AlertRow
                  key={alert.id}
                  alert={alert}
                  onDismiss={markAlertRead}
                />
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
