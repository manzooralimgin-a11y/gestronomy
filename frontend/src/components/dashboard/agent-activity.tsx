"use client";

import { useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useDashboardStore, type AgentActivity } from "@/stores/dashboard-store";
import { formatRelativeTime } from "@/lib/utils";
import { Activity } from "lucide-react";

const AGENT_COLORS: Record<string, string> = {
  InventoryAgent: "bg-blue-100 text-blue-800",
  KitchenAgent: "bg-orange-100 text-orange-800",
  FinanceAgent: "bg-green-100 text-green-800",
  WorkforceAgent: "bg-purple-100 text-purple-800",
  GuestAgent: "bg-pink-100 text-pink-800",
  MaintenanceAgent: "bg-yellow-100 text-yellow-800",
  SafetyAgent: "bg-red-100 text-red-800",
  MarketingAgent: "bg-teal-100 text-teal-800",
};

function getAgentColor(name: string): string {
  if (AGENT_COLORS[name]) return AGENT_COLORS[name];
  const hash = name.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
  const colors = Object.values(AGENT_COLORS);
  return colors[hash % colors.length];
}

function ActivityItem({ activity }: { activity: AgentActivity }) {
  return (
    <div className="flex items-start gap-3 rounded-md px-3 py-2 transition-colors hover:bg-gray-50">
      <Badge
        className={`mt-0.5 shrink-0 border-0 text-[10px] ${getAgentColor(activity.agent_name)}`}
      >
        {activity.agent_name}
      </Badge>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm text-gray-700">{activity.description}</p>
        <p className="text-xs text-gray-400">
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
              <p className="text-sm text-gray-400">No recent agent activity</p>
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
