import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { PageHeader, PageContainer, Reveal } from "@/components/layout/PageHeader";
import { GlassCard } from "@/components/ui/GlassCard";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { companies, type CompanyStatus } from "@/lib/mockData";
import { formatCurrency, cn } from "@/lib/utils";
import { Plus, Search, ArrowUpRight, TrendingUp, TrendingDown } from "lucide-react";

const stageLabel: Record<CompanyStatus, string> = {
  "active-dd": "Active Diligence",
  portfolio: "Portfolio",
  watchlist: "Watchlist",
  closed: "Closed",
};

const stageTone: Record<CompanyStatus, "gold" | "emerald" | "crimson" | "neutral"> = {
  "active-dd": "gold",
  portfolio: "emerald",
  watchlist: "crimson",
  closed: "neutral",
};

const filters: (CompanyStatus | "all")[] = ["all", "active-dd", "portfolio", "watchlist", "closed"];

export function CompaniesPage() {
  const [filter, setFilter] = useState<CompanyStatus | "all">("all");
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    return companies.filter((c) => {
      const matchesFilter = filter === "all" || c.stage === filter;
      const matchesQuery =
        query.trim() === "" ||
        c.name.toLowerCase().includes(query.toLowerCase()) ||
        c.sector.toLowerCase().includes(query.toLowerCase());
      return matchesFilter && matchesQuery;
    });
  }, [filter, query]);

  return (
    <PageContainer>
      <PageHeader
        eyebrow="Workspace"
        title="Companies"
        description="Every company workspace across active diligence, portfolio, and watchlist."
        actions={
          <Button variant="primary" size="md">
            <Plus size={15} /> New workspace
          </Button>
        }
      />

      <div className="px-8 flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1 max-w-sm">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-ink-4)]" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by name or sector…"
            className="w-full rounded-lg border border-[var(--color-border-hairline)] bg-white/[0.02] py-2 pl-9 pr-3 text-sm text-[var(--color-ink-0)] placeholder:text-[var(--color-ink-4)] focus:border-[var(--color-border-strong)] outline-none transition-colors"
          />
        </div>
        <div className="flex gap-1.5 overflow-x-auto no-scrollbar">
          {filters.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                "shrink-0 rounded-full border px-3.5 py-1.5 text-xs font-medium capitalize transition-colors",
                filter === f
                  ? "border-[var(--color-gold-500)]/40 bg-[var(--color-gold-500)]/[0.1] text-[var(--color-gold-300)]"
                  : "border-[var(--color-border-hairline)] text-[var(--color-ink-3)] hover:text-[var(--color-ink-0)]"
              )}
            >
              {f === "all" ? "All" : stageLabel[f]}
            </button>
          ))}
        </div>
      </div>

      <div className="px-8 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        {filtered.map((c, i) => (
          <Reveal key={c.id} delay={Math.min(i * 0.04, 0.2)}>
            <Link to={`/companies/${c.id}`}>
              <GlassCard interactive className="p-5 h-full flex flex-col">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-display text-[17px] text-[var(--color-ink-0)]">{c.name}</p>
                    <p className="text-xs text-[var(--color-ink-3)] mt-0.5">
                      {c.sector} · {c.geography}
                    </p>
                  </div>
                  <Badge tone={stageTone[c.stage]}>{stageLabel[c.stage]}</Badge>
                </div>
                <p className="text-[13px] text-[var(--color-ink-2)] leading-relaxed line-clamp-2 flex-1">{c.description}</p>
                <div className="ledger-rule my-4" />
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-mono text-sm text-[var(--color-ink-0)] tabular-nums">{formatCurrency(c.dealValue)}</p>
                    <p className="text-[11px] text-[var(--color-ink-4)]">deal value</p>
                  </div>
                  <div className="text-right">
                    <p className={cn("font-mono text-sm tabular-nums flex items-center gap-1 justify-end", c.riskScore > 55 ? "text-[var(--color-crimson)]" : c.riskScore > 35 ? "text-[var(--color-amber)]" : "text-[var(--color-emerald)]")}>
                      {c.riskScore > 55 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                      {c.riskScore}
                    </p>
                    <p className="text-[11px] text-[var(--color-ink-4)]">risk score</p>
                  </div>
                </div>
                <div className="mt-4 flex items-center justify-between text-xs">
                  <span className="text-[var(--color-ink-4)]">Analyst: {c.analyst}</span>
                  <span className="flex items-center gap-1 text-[var(--color-gold-400)]">
                    Open <ArrowUpRight size={12} />
                  </span>
                </div>
              </GlassCard>
            </Link>
          </Reveal>
        ))}
      </div>
    </PageContainer>
  );
}
