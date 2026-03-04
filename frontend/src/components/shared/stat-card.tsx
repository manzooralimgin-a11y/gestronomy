import { ArrowDown, ArrowUp, type LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
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
    <Card>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
          </div>
          {Icon && (
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-500/10">
              <Icon className="h-5 w-5 text-brand-500" />
            </div>
          )}
        </div>

        {(change !== undefined || target) && (
          <div className="mt-3 flex items-center gap-2">
            {change !== undefined && (
              <span
                className={cn(
                  "inline-flex items-center text-xs font-medium",
                  isPositive && "text-green-600",
                  isNegative && "text-red-600"
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
              <span className="text-xs text-gray-400">
                Target: {target}
              </span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
