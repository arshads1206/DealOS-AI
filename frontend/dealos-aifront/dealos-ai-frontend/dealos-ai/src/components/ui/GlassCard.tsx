import * as React from "react";
import { cn } from "@/lib/utils";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  raised?: boolean;
  interactive?: boolean;
}

export const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, raised = false, interactive = false, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "relative rounded-2xl overflow-hidden",
          raised ? "glass-panel-raised" : "glass-panel",
          interactive &&
            "transition-all duration-300 ease-out hover:-translate-y-0.5 hover:shadow-[0_1px_0_rgba(255,255,255,0.06)_inset,0_28px_56px_-18px_rgba(0,0,0,0.7),0_0_0_1px_rgba(201,162,39,0.22)] cursor-pointer",
          className
        )}
        {...props}
      >
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-[var(--color-gold-500)]/40 to-transparent opacity-60" />
        {children}
      </div>
    );
  }
);
GlassCard.displayName = "GlassCard";
