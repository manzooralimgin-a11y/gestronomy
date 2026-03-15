import { ArrowDown, ArrowUp, type LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  target?: string;
  icon?: LucideIcon;
  className?: string;
}

export function StatCard({ title, value, change, target, icon: Icon, className }: StatCardProps) {
  const isPositive = change !== undefined && change >= 0;
  const isNegative = change !== undefined && change < 0;

  return (
    <div className={cn("glass-card p-5 group", className)}>
      <div className="flex items-start justify-between">
        <div className="space-y-1.5">
          <p className="text-xs font-medium text-muted-foreground tracking-wide uppercase">
            {title}
          </p>
          <p className="text-2xl font-bold text-foreground tracking-tight">
            {value}
          </p>
        </div>
        {Icon && (
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 transition-all duration-base group-hover:bg-primary/15 group-hover:shadow-glow-sm">
            <Icon className="h-[18px] w-[18px] text-primary" />
          </div>
        )}
      </div>

      {(change !== undefined || target) && (
        <div className="mt-3 flex items-center gap-2.5">
          {change !== undefined && (
            <span
              className={cn(
                "inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-xs font-semibold",
                isPositive && "bg-status-success/10 text-status-success",
                isNegative && "bg-status-danger/10 text-status-danger"
              )}
            >
              {isPositive ? (
                <ArrowUp className="h-3 w-3" />
              ) : (
                <ArrowDown className="h-3 w-3" />
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
