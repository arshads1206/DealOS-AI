import type { ReactNode } from "react";
import { GlassCard } from "./GlassCard";
import { CountUp } from "./CountUp";
import { cn } from "@/lib/utils";

export function StatCard({
  label,
  value,
  delta,
  deltaTone = "emerald",
  icon,
  formatter,
  suffix,
}: {
  label: string;
  value: number;
  delta?: string;
  deltaTone?: "emerald" | "crimson";
  icon?: ReactNode;
  formatter?: (v: number) => string;
  suffix?: string;
}) {
  return (
    <GlassCard className="p-5" interactive>
      <div className="flex items-start justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-[var(--color-ink-3)]">{label}</span>
        {icon && (
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[var(--color-gold-500)]/[0.1] text-[var(--color-gold-400)] shadow-[0_0_16px_-6px_rgba(201,162,39,0.6)]">
            {icon}
          </div>
        )}
      </div>
      <div className="mt-3.5 flex items-baseline gap-1.5">
        <span className="figure-display text-[26px] font-semibold text-[var(--color-ink-0)]">
          <CountUp value={value} formatter={formatter} />
        </span>
        {suffix && <span className="text-sm text-[var(--color-ink-3)]">{suffix}</span>}
      </div>
      {delta && (
        <p className={cn("mt-2.5 pt-2.5 border-t border-[var(--color-border-hairline)] text-xs font-mono", deltaTone === "emerald" ? "text-[var(--color-emerald)]" : "text-[var(--color-crimson)]")}>
          {delta}
        </p>
      )}
    </GlassCard>
  );
}
