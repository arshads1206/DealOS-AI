import { useState } from "react";
import { useParams } from "react-router-dom";
import { GlassCard } from "@/components/ui/GlassCard";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Reveal } from "@/components/layout/PageHeader";
import { getReports } from "@/lib/mockData";
import { FileBarChart, Download, Plus } from "lucide-react";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import { InvestmentMemoView } from "../../reports/InvestmentMemoView";

const statusTone = { draft: "neutral", "in-review": "amber", final: "emerald" } as const;

export function ReportsTab() {
  const { id } = useParams();
  const items = getReports(id!);
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);

  const isLoading = false; // Prepare for API

  if (selectedReportId) {
    const report = items.find(r => r.id === selectedReportId);
    if (report) {
      return <InvestmentMemoView report={report} onBack={() => setSelectedReportId(null)} />;
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button variant="primary" size="sm">
          <Plus size={14} /> Generate report
        </Button>
      </div>
      
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Skeleton className="h-32 w-full rounded-xl" />
          <Skeleton className="h-32 w-full rounded-xl" />
        </div>
      ) : items.length === 0 ? (
        <EmptyState
          icon={<div className="h-12 w-12 rounded-full bg-[var(--color-surface-2)] flex items-center justify-center"><FileBarChart size={20} className="text-[var(--color-ink-3)]" /></div>}
          title="No reports generated"
          description="Generate investment reports, credit memos, or risk summaries."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {items.map((r, i) => (
            <Reveal key={r.id} delay={Math.min(i * 0.05, 0.2)}>
              <div onClick={() => setSelectedReportId(r.id)} className="h-full cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-gold-500)] rounded-xl text-left">
                <GlassCard className="p-5" interactive>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--color-gold-500)]/[0.1]">
                      <FileBarChart size={16} className="text-[var(--color-gold-400)]" />
                    </div>
                    <Badge tone={statusTone[r.status]}>{r.status.replace("-", " ")}</Badge>
                  </div>
                  <p className="font-display text-base text-[var(--color-ink-0)] leading-snug">{r.title}</p>
                  <p className="text-xs text-[var(--color-ink-3)] mt-1.5">
                    {r.type} · {r.pages} pages · {r.author}
                  </p>
                  <div className="flex items-center justify-between mt-4 pt-3 border-t border-[var(--color-border-hairline)]">
                    <span className="text-[11px] font-mono text-[var(--color-ink-4)]">{r.date}</span>
                    <button onClick={(e) => e.stopPropagation()} aria-label={`Export ${r.title}`} className="flex items-center gap-1 text-xs text-[var(--color-gold-400)] hover:text-[var(--color-gold-300)]">
                      <Download size={12} /> Export
                    </button>
                  </div>
                </GlassCard>
              </div>
            </Reveal>
          ))}
        </div>
      )}
    </div>
  );
}
