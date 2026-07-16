import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { PageHeader, PageContainer, Reveal } from "@/components/layout/PageHeader";
import { GlassCard } from "@/components/ui/GlassCard";
import { SeverityBadge, Badge } from "@/components/ui/Badge";
import { RiskHeatmap } from "@/components/charts/RiskHeatmap";
import { risks, getCompany } from "@/lib/mockData";
import { cn } from "@/lib/utils";
import { FileText } from "lucide-react";

const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
const filters = ["all", "open", "monitoring", "resolved"] as const;

export function RiskAnalysisPage() {
  const [filter, setFilter] = useState<(typeof filters)[number]>("all");

  const filtered = useMemo(
    () => risks.filter((r) => filter === "all" || r.status === filter).sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]),
    [filter]
  );

  return (
    <PageContainer>
      <PageHeader
        eyebrow="Intelligence"
        title="Risk Analysis"
        description="Every risk detected by the AI Analyst across the portfolio, ranked by severity and traced to its source document."
      />

      <div className="px-8 space-y-4">
        <Reveal>
          <GlassCard className="p-6" raised>
            <p className="font-display text-lg text-[var(--color-ink-0)] mb-4">Risk Distribution by Category</p>
            <RiskHeatmap />
          </GlassCard>
        </Reveal>

        <div className="flex gap-1.5">
          {filters.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                "rounded-full border px-3.5 py-1.5 text-xs font-medium capitalize transition-colors",
                filter === f ? "border-[var(--color-gold-500)]/40 bg-[var(--color-gold-500)]/[0.1] text-[var(--color-gold-300)]" : "border-[var(--color-border-hairline)] text-[var(--color-ink-3)] hover:text-[var(--color-ink-0)]"
              )}
            >
              {f}
            </button>
          ))}
        </div>

        <div className="space-y-3">
          {filtered.map((r, i) => (
            <Reveal key={r.id} delay={Math.min(i * 0.03, 0.2)}>
              <GlassCard className="p-5" interactive>
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1.5">
                      <Link to={`/companies/${r.companyId}`} className="text-xs text-[var(--color-gold-400)] hover:text-[var(--color-gold-300)] font-medium">
                        {getCompany(r.companyId)?.name}
                      </Link>
                      <Badge tone="neutral">{r.category}</Badge>
                      <SeverityBadge severity={r.severity} />
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
        </div>
      </div>
    </PageContainer>
  );
}
