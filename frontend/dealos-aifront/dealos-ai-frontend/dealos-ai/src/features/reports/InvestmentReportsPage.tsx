import { Link } from "react-router-dom";
import { PageHeader, PageContainer, Reveal } from "@/components/layout/PageHeader";
import { GlassCard } from "@/components/ui/GlassCard";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { reports, getCompany } from "@/lib/mockData";
import { FileBarChart, Download, Plus } from "lucide-react";

const statusTone = { draft: "neutral", "in-review": "amber", final: "emerald" } as const;

export function InvestmentReportsPage() {
  return (
    <PageContainer>
      <PageHeader
        eyebrow="Intelligence"
        title="Investment Reports"
        description="AI-assisted due diligence reports, investment memos, and quarterly reviews across the portfolio."
        actions={
          <Button variant="primary" size="md">
            <Plus size={15} /> Generate report
          </Button>
        }
      />
      <div className="px-8 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {reports.map((r, i) => (
          <Reveal key={r.id} delay={Math.min(i * 0.05, 0.2)}>
            <GlassCard className="p-5 h-full flex flex-col" interactive>
              <div className="flex items-start justify-between mb-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--color-gold-500)]/[0.1]">
                  <FileBarChart size={16} className="text-[var(--color-gold-400)]" />
                </div>
                <Badge tone={statusTone[r.status]}>{r.status.replace("-", " ")}</Badge>
              </div>
              <p className="font-display text-base text-[var(--color-ink-0)] leading-snug flex-1">{r.title}</p>
              <Link to={`/companies/${r.companyId}`} className="text-xs text-[var(--color-gold-400)] hover:text-[var(--color-gold-300)] mt-2 inline-block w-fit">
                {getCompany(r.companyId)?.name}
              </Link>
              <p className="text-xs text-[var(--color-ink-3)] mt-1.5">
                {r.type} · {r.pages} pages · {r.author}
              </p>
              <div className="flex items-center justify-between mt-4 pt-3 border-t border-[var(--color-border-hairline)]">
                <span className="text-[11px] font-mono text-[var(--color-ink-4)]">{r.date}</span>
                <button className="flex items-center gap-1 text-xs text-[var(--color-gold-400)] hover:text-[var(--color-gold-300)]">
                  <Download size={12} /> Export
                </button>
              </div>
            </GlassCard>
          </Reveal>
        ))}
      </div>
    </PageContainer>
  );
}
