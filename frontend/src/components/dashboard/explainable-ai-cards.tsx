"use client";

import { RotateCcw, ShieldCheck, Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useDashboardStore } from "@/stores/dashboard-store";
import { formatRelativeTime } from "@/lib/utils";

export function ExplainableAICards() {
  const recommendations = useDashboardStore((s) => s.recommendations);

  return (
    <Card className="flex h-[460px] flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Sparkles className="h-5 w-5 text-brand-500" />
          Explainable AI Recommendations
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden">
        <div className="h-full space-y-3 overflow-y-auto pr-1">
          {recommendations.length === 0 ? (
            <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
              No recommendations available.
            </div>
          ) : (
            recommendations.map((rec) => (
              <div key={rec.id} className="rounded-lg border border-border bg-card p-3 shadow-soft">
                <div className="mb-1 flex items-center gap-2">
                  <Badge variant="secondary">{rec.agent_name}</Badge>
                  <Badge variant={rec.requires_approval ? "warning" : "success"}>
                    {rec.requires_approval ? "Needs approval" : "Auto-safe"}
                  </Badge>
                  <span className="ml-auto text-xs text-muted-foreground">{formatRelativeTime(rec.created_at)}</span>
                </div>
                <p className="text-sm font-semibold text-foreground">{rec.title}</p>
                <p className="mt-1 text-sm text-foreground">{rec.recommendation}</p>
                <div className="mt-2 rounded bg-muted p-2 text-xs text-muted-foreground">
                  <p className="font-medium text-foreground">Why:</p>
                  <p>{rec.rationale}</p>
                </div>
                <div className="mt-2 grid grid-cols-1 gap-2 text-xs sm:grid-cols-2">
                  <div className="flex items-center gap-1 text-muted-foreground">
                    <ShieldCheck className="h-3.5 w-3.5" />
                    Confidence: {rec.confidence == null ? "-" : `${Math.round(rec.confidence * 100)}%`}
                  </div>
                  <div className="text-muted-foreground">Impact: {rec.estimated_impact || "Operational efficiency"}</div>
                </div>
                {rec.rollback_strategy && (
                  <div className="mt-2 flex items-center gap-1 rounded bg-status-info-soft px-2 py-1 text-xs text-status-info">
                    <RotateCcw className="h-3.5 w-3.5" />
                    Rollback: {rec.rollback_strategy}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
