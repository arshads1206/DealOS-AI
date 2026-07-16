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
        {icon && <div className="text-[var(--color-gold-500)]/70">{icon}</div>}
      </div>
      <div className="mt-3 flex items-baseline gap-1">
        <span className="font-mono text-2xl font-semibold tabular-nums text-[var(--color-ink-0)]">
          <CountUp value={value} formatter={formatter} />
        </span>
        {suffix && <span className="text-sm text-[var(--color-ink-3)]">{suffix}</span>}
      </div>
      {delta && (
        <p className={cn("mt-2 text-xs font-mono", deltaTone === "emerald" ? "text-[var(--color-emerald)]" : "text-[var(--color-crimson)]")}>
          {delta}
        </p>
      )}
    </GlassCard>
  );
}
