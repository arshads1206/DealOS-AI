import { riskByCategory } from "@/lib/mockData";
import { cn } from "@/lib/utils";

const severities = ["low", "medium", "high", "critical"] as const;

const cellTone: Record<(typeof severities)[number], (count: number) => string> = {
  low: (n) => (n === 0 ? "bg-white/[0.02]" : n < 3 ? "bg-[var(--color-ice)]/20" : "bg-[var(--color-ice)]/40"),
  medium: (n) => (n === 0 ? "bg-white/[0.02]" : n < 3 ? "bg-[var(--color-amber)]/20" : "bg-[var(--color-amber)]/40"),
  high: (n) => (n === 0 ? "bg-white/[0.02]" : n < 2 ? "bg-[var(--color-crimson)]/25" : "bg-[var(--color-crimson)]/45"),
  critical: (n) => (n === 0 ? "bg-white/[0.02]" : "bg-[var(--color-crimson)]/60"),
};

export function RiskHeatmap() {
  return (
    <div className="overflow-x-auto">
      <div className="min-w-[440px]">
        <div className="grid grid-cols-[1fr_repeat(4,64px)] items-center gap-1.5 mb-1.5">
          <span />
          {severities.map((s) => (
            <span key={s} className="text-center text-[10px] uppercase tracking-wider text-[var(--color-ink-3)]">
              {s}
            </span>
          ))}
        </div>
        {riskByCategory.map((row) => (
          <div key={row.category} className="grid grid-cols-[1fr_repeat(4,64px)] items-center gap-1.5 mb-1.5">
            <span className="text-[13px] text-[var(--color-ink-1)]">{row.category}</span>
            {severities.map((s) => {
              const count = row[s];
              return (
                <div
                  key={s}
                  className={cn(
                    "h-9 rounded-md flex items-center justify-center font-mono text-xs tabular-nums transition-transform hover:scale-105",
                    cellTone[s](count),
                    count > 0 ? "text-[var(--color-ink-0)]" : "text-[var(--color-ink-4)]"
                  )}
                >
                  {count > 0 ? count : "—"}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}
