import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

type Tone = "gold" | "emerald" | "amber" | "crimson" | "ice" | "neutral";

const tones: Record<Tone, string> = {
  gold: "bg-[var(--color-gold-500)]/[0.12] text-[var(--color-gold-300)] border-[var(--color-gold-500)]/30 shadow-[0_0_12px_-4px_rgba(201,162,39,0.5)]",
  emerald: "bg-[var(--color-emerald)]/[0.12] text-[var(--color-emerald)] border-[var(--color-emerald)]/30 shadow-[0_0_12px_-4px_rgba(52,178,127,0.4)]",
  amber: "bg-[var(--color-amber)]/[0.12] text-[var(--color-amber)] border-[var(--color-amber)]/30 shadow-[0_0_12px_-4px_rgba(220,157,63,0.4)]",
  crimson: "bg-[var(--color-crimson)]/[0.12] text-[var(--color-crimson)] border-[var(--color-crimson)]/30 shadow-[0_0_12px_-4px_rgba(207,87,81,0.4)]",
  ice: "bg-[var(--color-ice)]/[0.12] text-[var(--color-ice)] border-[var(--color-ice)]/30 shadow-[0_0_12px_-4px_rgba(91,155,213,0.4)]",
  neutral: "bg-white/[0.05] text-[var(--color-ink-2)] border-white/10",
};

const dotTones: Record<Tone, string> = {
  gold: "bg-[var(--color-gold-300)]",
  emerald: "bg-[var(--color-emerald)]",
  amber: "bg-[var(--color-amber)]",
  crimson: "bg-[var(--color-crimson)]",
  ice: "bg-[var(--color-ice)]",
  neutral: "bg-[var(--color-ink-2)]",
};

export function Badge({
  children,
  tone = "neutral",
  dot = false,
  className,
}: {
  children: ReactNode;
  tone?: Tone;
  dot?: boolean;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-medium tracking-wide uppercase",
        tones[tone],
        className
      )}
    >
      {dot && <span className={cn("h-1.5 w-1.5 rounded-full", dotTones[tone])} />}
      {children}
    </span>
  );
}

export function StatusDot({ tone }: { tone: Tone }) {
  return <span className={cn("mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full", dotTones[tone])} />;
}

const severityTone: Record<string, Tone> = {
  low: "ice",
  medium: "amber",
  high: "crimson",
  critical: "crimson",
};

export function SeverityBadge({ severity }: { severity: "low" | "medium" | "high" | "critical" }) {
  return (
    <Badge tone={severityTone[severity]} dot>
      {severity}
    </Badge>
  );
}
