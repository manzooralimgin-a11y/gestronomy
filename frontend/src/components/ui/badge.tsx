import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-[0.7rem] font-semibold uppercase tracking-wider backdrop-blur-[8px] transition-colors duration-200 ease-editorial focus:outline-none focus:ring-2 focus:ring-gold/30 focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "bg-[rgba(212,175,55,0.08)] border-[rgba(212,175,55,0.12)] text-gold hover:border-[rgba(212,175,55,0.2)]",
        secondary:
          "bg-[rgba(255,253,240,0.04)] border-[rgba(255,253,240,0.08)] text-foreground-muted",
        destructive:
          "bg-[rgba(230,57,70,0.08)] border-[rgba(230,57,70,0.12)] text-status-danger",
        outline:
          "bg-transparent border-[rgba(255,253,240,0.1)] text-foreground",
        success:
          "bg-[rgba(82,183,136,0.08)] border-[rgba(82,183,136,0.12)] text-status-success",
        warning:
          "bg-[rgba(232,197,71,0.08)] border-[rgba(232,197,71,0.12)] text-status-warning",
        info:
          "bg-[rgba(106,173,207,0.08)] border-[rgba(106,173,207,0.12)] text-status-info",
        glass:
          "glass-card border-[var(--glass-border)] text-foreground shadow-none",
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
