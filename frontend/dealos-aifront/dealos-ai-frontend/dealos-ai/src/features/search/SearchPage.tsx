import { useMemo, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { PageHeader, PageContainer, Reveal } from "@/components/layout/PageHeader";
import { GlassCard } from "@/components/ui/GlassCard";
import { Badge, SeverityBadge } from "@/components/ui/Badge";
import { companies, documents, risks, getCompany } from "@/lib/mockData";
import { Search as SearchIcon, Building2, FileText, ShieldAlert } from "lucide-react";

export function SearchPage() {
  const [query, setQuery] = useState("");

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return null;
    return {
      companies: companies.filter((c) => c.name.toLowerCase().includes(q) || c.sector.toLowerCase().includes(q)),
      documents: documents.filter((d) => d.name.toLowerCase().includes(q) || d.type.toLowerCase().includes(q)),
      risks: risks.filter((r) => r.title.toLowerCase().includes(q) || r.summary.toLowerCase().includes(q)),
    };
  }, [query]);

  const recent = ["payor concentration", "covenant headroom", "Vertex Semiconductor", "reserve restatement"];

  return (
    <PageContainer>
      <PageHeader eyebrow="Global Search" title="Search across your workspace" description="Search companies, documents, financial data, and AI-detected risks in one place." />

      <div className="px-8">
        <div className="relative max-w-2xl mb-8">
          <SearchIcon size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--color-ink-4)]" />
          <input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search deals, documents, filings, risks…"
            className="w-full rounded-xl border border-[var(--color-border-hairline)] bg-white/[0.02] py-3.5 pl-11 pr-4 text-sm text-[var(--color-ink-0)] placeholder:text-[var(--color-ink-4)] focus:border-[var(--color-border-strong)] outline-none transition-colors"
          />
        </div>

        {!results && (
          <Reveal>
            <p className="text-xs uppercase tracking-wider text-[var(--color-ink-3)] mb-3">Recent searches</p>
            <div className="flex flex-wrap gap-2">
              {recent.map((r) => (
                <button
                  key={r}
                  onClick={() => setQuery(r)}
                  className="rounded-full border border-[var(--color-border-hairline)] px-3.5 py-1.5 text-xs text-[var(--color-ink-2)] hover:border-[var(--color-border-strong)] hover:text-[var(--color-ink-0)] transition-colors"
                >
                  {r}
                </button>
              ))}
            </div>
          </Reveal>
        )}

        {results && (
          <div className="space-y-8">
            {results.companies.length > 0 && (
              <ResultSection icon={<Building2 size={14} />} title="Companies">
                {results.companies.map((c) => (
                  <Link key={c.id} to={`/companies/${c.id}`}>
                    <GlassCard interactive className="p-4 flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-[var(--color-ink-0)]">{c.name}</p>
                        <p className="text-xs text-[var(--color-ink-3)]">{c.sector}</p>
                      </div>
                      <Badge tone="gold">{c.stage.replace("-", " ")}</Badge>
                    </GlassCard>
                  </Link>
                ))}
              </ResultSection>
            )}
            {results.documents.length > 0 && (
              <ResultSection icon={<FileText size={14} />} title="Documents">
                {results.documents.map((d) => (
                  <Link key={d.id} to={`/companies/${d.companyId}/documents`}>
                    <GlassCard interactive className="p-4 flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-[var(--color-ink-0)]">{d.name}</p>
                        <p className="text-xs text-[var(--color-ink-3)]">{getCompany(d.companyId)?.name} · {d.type}</p>
                      </div>
                    </GlassCard>
                  </Link>
                ))}
              </ResultSection>
            )}
            {results.risks.length > 0 && (
              <ResultSection icon={<ShieldAlert size={14} />} title="Risks">
                {results.risks.map((r) => (
                  <Link key={r.id} to={`/companies/${r.companyId}/risks`}>
                    <GlassCard interactive className="p-4 flex items-center justify-between gap-4">
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-[var(--color-ink-0)] truncate">{r.title}</p>
                        <p className="text-xs text-[var(--color-ink-3)]">{getCompany(r.companyId)?.name}</p>
                      </div>
                      <SeverityBadge severity={r.severity} />
                    </GlassCard>
                  </Link>
                ))}
              </ResultSection>
            )}
            {results.companies.length === 0 && results.documents.length === 0 && results.risks.length === 0 && (
              <p className="text-sm text-[var(--color-ink-3)] py-12 text-center">No results for "{query}".</p>
            )}
          </div>
        )}
      </div>
    </PageContainer>
  );
}

function ResultSection({ icon, title, children }: { icon: ReactNode; title: string; children: ReactNode }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-3 text-[var(--color-ink-3)]">
        {icon}
        <p className="text-xs uppercase tracking-wider">{title}</p>
      </div>
      <div className="space-y-2">{children}</div>
    </div>
  );
}
