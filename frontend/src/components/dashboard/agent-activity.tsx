"use client";

import { useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useDashboardStore, type AgentActivity } from "@/stores/dashboard-store";
import { formatRelativeTime } from "@/lib/utils";
import { Activity } from "lucide-react";

const AGENT_COLORS: Record<string, string> = {
  InventoryAgent: "bg-blue-500/15 text-blue-400",
  KitchenAgent: "bg-amber-500/15 text-amber-400",
  FinanceAgent: "bg-emerald-500/15 text-emerald-400",
  WorkforceAgent: "bg-purple-500/15 text-purple-400",
  GuestAgent: "bg-pink-500/15 text-pink-400",
  MaintenanceAgent: "bg-amber-500/15 text-amber-400",
  SafetyAgent: "bg-red-500/15 text-red-400",
  MarketingAgent: "bg-teal-500/15 text-teal-400",
};

function getAgentColor(name: string): string {
  if (AGENT_COLORS[name]) return AGENT_COLORS[name];
  const hash = name.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
  const colors = Object.values(AGENT_COLORS);
  return colors[hash % colors.length];
}

function ActivityItem({ activity }: { activity: AgentActivity }) {
  return (
    <div className="flex items-start gap-3 rounded-md px-3 py-2 transition-colors hover:bg-[hsl(var(--glass-highlight))]">
      <Badge
        className={`mt-0.5 shrink-0 border-0 text-[10px] ${getAgentColor(activity.agent_name)}`}
      >
        {activity.agent_name}
      </Badge>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm text-foreground/80">{activity.description}</p>
        <p className="text-xs text-muted-foreground/60">
          {formatRelativeTime(activity.created_at)}
        </p>
      </div>
    </div>
  );
}

export function AgentActivityFeed() {
  const agentActivity = useDashboardStore((s) => s.agentActivity);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [agentActivity.length]);

  return (
    <Card className="flex h-[400px] flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Activity className="h-5 w-5 text-brand-500" />
          Agent Activity
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden p-0">
        <div ref={scrollRef} className="h-full overflow-y-auto px-3 pb-4">
          {agentActivity.length === 0 ? (
            <div className="flex h-full items-center justify-center">
              <p className="text-sm text-muted-foreground/60">No recent agent activity</p>
            </div>
          ) : (
            <div className="space-y-1">
              {agentActivity.map((activity) => (
                <ActivityItem key={activity.id} activity={activity} />
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
