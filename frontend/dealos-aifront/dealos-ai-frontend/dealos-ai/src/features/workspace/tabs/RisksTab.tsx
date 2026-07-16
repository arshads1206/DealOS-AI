import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { GlassCard } from "@/components/ui/GlassCard";
import { Badge, SeverityBadge } from "@/components/ui/Badge";
import { Reveal } from "@/components/layout/PageHeader";
import { getRisks } from "@/lib/mockData";
import { cn } from "@/lib/utils";
import { FileText } from "lucide-react";

const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
const filters = ["all", "open", "monitoring", "resolved"] as const;

export function RisksTab() {
  const { id } = useParams();
  const [filter, setFilter] = useState<(typeof filters)[number]>("all");
  const allRisks = getRisks(id!);

  const filtered = useMemo(() => {
    return allRisks
      .filter((r) => filter === "all" || r.status === filter)
      .sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]);
  }, [allRisks, filter]);

  return (
    <div className="space-y-4">
      <div className="flex gap-1.5">
        {filters.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={cn(
              "rounded-full border px-3.5 py-1.5 text-xs font-medium capitalize transition-colors",
              filter === f
                ? "border-[var(--color-gold-500)]/40 bg-[var(--color-gold-500)]/[0.1] text-[var(--color-gold-300)]"
                : "border-[var(--color-border-hairline)] text-[var(--color-ink-3)] hover:text-[var(--color-ink-0)]"
            )}
          >
            {f}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {filtered.map((r, i) => (
          <Reveal key={r.id} delay={Math.min(i * 0.04, 0.2)}>
            <GlassCard className="p-5" interactive>
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-1.5">
                    <Badge tone="neutral">{r.category}</Badge>
                    <SeverityBadge severity={r.severity} />
                    <span className="text-[11px] text-[var(--color-ink-4)] font-mono">{r.status}</span>
                  </div>
                  <p className="font-display text-base text-[var(--color-ink-0)]">{r.title}</p>
                  <p className="text-sm text-[var(--color-ink-2)] mt-1.5 leading-relaxed">{r.summary}</p>
                  <div className="flex items-center gap-1.5 mt-3 text-xs text-[var(--color-ink-4)]">
                    <FileText size={12} />
                    <span>
                      {r.source} · p.{r.page}
                    </span>
                    <span>·</span>
                    <span>Detected {r.detected}</span>
                  </div>
                </div>
              </div>
            </GlassCard>
          </Reveal>
        ))}
        {filtered.length === 0 && <p className="text-sm text-[var(--color-ink-3)] py-8 text-center">No risks match this filter.</p>}
      </div>
    </div>
  );
}
