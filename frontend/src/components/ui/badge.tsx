import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors duration-fast ease-standard focus:outline-none focus:ring-2 focus:ring-ring/50 focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary/15 text-primary",
        secondary: "border-transparent bg-secondary text-secondary-foreground",
        destructive: "border-transparent bg-status-danger/15 text-status-danger",
        outline: "border-border bg-transparent text-foreground",
        success: "border-transparent bg-status-success/15 text-status-success",
        warning: "border-transparent bg-status-warning/15 text-status-warning",
        info: "border-transparent bg-status-info/15 text-status-info",
        glass: "glass-card border-[hsl(var(--glass-border))] text-foreground shadow-none",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
