import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-semibold ring-offset-background transition-all duration-fast ease-standard focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground shadow-soft hover:shadow-glow-sm hover:brightness-110 active:scale-[0.98]",
        destructive:
          "bg-status-danger text-white shadow-soft hover:bg-status-danger/90 active:scale-[0.98]",
        outline:
          "glass-input text-foreground hover:bg-[hsl(var(--glass-highlight))] hover:border-[hsl(var(--glass-elevated-border))] active:scale-[0.98]",
        secondary:
          "bg-secondary text-secondary-foreground shadow-soft hover:bg-secondary/80 active:scale-[0.98]",
        ghost:
          "text-foreground hover:bg-[hsl(var(--glass-highlight))] active:scale-[0.98]",
        link: "text-primary underline-offset-4 hover:underline",
        glass:
          "glass-card text-foreground hover:shadow-raised active:scale-[0.98]",
        glow:
          "bg-primary text-primary-foreground shadow-glow hover:shadow-glow-lg hover:brightness-110 active:scale-[0.98]",
      },
      size: {
        default: "h-10 px-5 py-2",
        sm: "h-9 px-3.5 text-xs",
        lg: "h-12 px-8 text-base",
        xl: "h-14 px-10 text-base font-bold",
        icon: "h-10 w-10",
        "icon-sm": "h-8 w-8",
        "icon-lg": "h-12 w-12",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
