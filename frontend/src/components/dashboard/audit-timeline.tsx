"use client";

import { useEffect, useState } from "react";
import { ActivitySquare, Bot, ShieldAlert } from "lucide-react";
import api from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatRelativeTime } from "@/lib/utils";
import type { AuditTimelineEvent } from "@/stores/dashboard-store";

interface AuditTimelineProps {
  title?: string;
  entityType?: string;
  entityId?: number | null;
  limit?: number;
  compact?: boolean;
}

export function AuditTimeline({
  title = "Action Audit Timeline",
  entityType,
  entityId,
  limit = 20,
  compact = false,
}: AuditTimelineProps) {
  const [items, setItems] = useState<AuditTimelineEvent[]>([]);

  useEffect(() => {
    api
      .get("/dashboard/audit-timeline", {
        params: {
          entity_type: entityType || undefined,
          entity_id: entityId ?? undefined,
          limit,
        },
      })
      .then(({ data }) => setItems(data))
      .catch(() => setItems([]));
  }, [entityType, entityId, limit]);

  return (
    <Card className={compact ? "" : "flex h-[420px] flex-col"}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <ActivitySquare className="h-5 w-5 text-brand-500" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className={compact ? "" : "flex-1 overflow-hidden"}>
        <div className={`${compact ? "max-h-[260px]" : "h-full"} space-y-2 overflow-y-auto pr-1`}>
          {items.length === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">No audit events yet.</div>
          ) : (
            items.map((event) => (
              <div key={event.id} className="rounded-lg border border-border bg-card p-3 shadow-soft">
                <div className="mb-1 flex items-center gap-2">
                  <Badge variant={event.event_type === "alert" ? "warning" : "secondary"}>
                    {event.event_type}
                  </Badge>
                  <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                    {event.actor_type === "agent" ? <Bot className="h-3.5 w-3.5" /> : <ShieldAlert className="h-3.5 w-3.5" />}
                    {event.actor_name}
                  </span>
                  <span className="ml-auto text-xs text-muted-foreground">{formatRelativeTime(event.created_at)}</span>
                </div>
                <p className="text-sm font-medium text-foreground">{event.action}</p>
                <p className="text-xs text-muted-foreground">{event.detail}</p>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
