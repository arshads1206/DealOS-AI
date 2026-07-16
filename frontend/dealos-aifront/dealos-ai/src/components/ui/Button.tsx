import * as React from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "secondary" | "ghost" | "outline" | "danger";
type Size = "sm" | "md" | "lg" | "icon";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

const variants: Record<Variant, string> = {
  primary:
    "bg-gradient-to-b from-[var(--color-gold-300)] to-[var(--color-gold-500)] text-[#141008] font-medium shadow-[0_1px_0_rgba(255,255,255,0.35)_inset,0_8px_20px_-8px_rgba(201,162,39,0.55)] hover:shadow-[0_1px_0_rgba(255,255,255,0.4)_inset,0_10px_28px_-8px_rgba(201,162,39,0.7)] hover:brightness-[1.06] active:brightness-95",
  secondary:
    "bg-[var(--color-surface-2)] text-[var(--color-ink-0)] border border-[var(--color-border-hairline)] hover:border-[var(--color-border-strong)] hover:bg-white/[0.04]",
  ghost: "bg-transparent text-[var(--color-ink-1)] hover:text-[var(--color-ink-0)] hover:bg-white/[0.04]",
  outline:
    "bg-transparent border border-[var(--color-border-strong)] text-[var(--color-gold-300)] hover:bg-[var(--color-gold-500)]/[0.08] hover:border-[var(--color-gold-500)]/60",
  danger:
    "bg-[var(--color-crimson-dim)]/20 text-[var(--color-crimson)] border border-[var(--color-crimson)]/30 hover:bg-[var(--color-crimson-dim)]/30",
};

const sizes: Record<Size, string> = {
  sm: "h-8 px-3 text-xs gap-1.5 rounded-lg",
  md: "h-9 px-4 text-sm gap-2 rounded-lg",
  lg: "h-11 px-6 text-sm gap-2 rounded-xl",
  icon: "h-9 w-9 rounded-lg justify-center",
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", loading = false, disabled, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={cn(
          "relative inline-flex items-center font-sans transition-all duration-200 ease-out disabled:opacity-40 disabled:pointer-events-none whitespace-nowrap select-none",
          "hover:-translate-y-[1px] active:translate-y-0 active:scale-[0.98]",
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {loading && <Loader2 size={14} className="animate-spin" />}
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";
