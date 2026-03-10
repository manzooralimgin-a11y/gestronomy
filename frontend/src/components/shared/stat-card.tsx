import { ArrowDown, ArrowUp, type LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  target?: string;
  icon?: LucideIcon;
}

export function StatCard({ title, value, change, target, icon: Icon }: StatCardProps) {
  const isPositive = change !== undefined && change >= 0;
  const isNegative = change !== undefined && change < 0;

  return (
    <div className="glass-card p-5">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-medium text-muted-foreground">{title}</p>
          <p className="text-2xl font-bold text-foreground">{value}</p>
        </div>
        {Icon && (
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
            <Icon className="h-4 w-4 text-primary" />
          </div>
        )}
      </div>

      {(change !== undefined || target) && (
        <div className="mt-3 flex items-center gap-2">
          {change !== undefined && (
            <span
              className={cn(
                "inline-flex items-center text-xs font-medium",
                isPositive && "text-emerald-400",
                isNegative && "text-red-400"
              )}
            >
              {isPositive ? (
                <ArrowUp className="mr-0.5 h-3 w-3" />
              ) : (
                <ArrowDown className="mr-0.5 h-3 w-3" />
              )}
              {Math.abs(change).toFixed(1)}%
            </span>
          )}
          {target && (
            <span className="text-xs text-muted-foreground/60">
              Target: {target}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
