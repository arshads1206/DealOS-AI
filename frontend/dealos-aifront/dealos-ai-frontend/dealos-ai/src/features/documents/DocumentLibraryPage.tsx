import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { PageHeader, PageContainer, Reveal } from "@/components/layout/PageHeader";
import { GlassCard } from "@/components/ui/GlassCard";
import { Badge } from "@/components/ui/Badge";
import { documents, getCompany } from "@/lib/mockData";
import { FileText, UploadCloud } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

const statusTone = { processed: "emerald", processing: "amber", queued: "neutral" } as const;
const types = ["all", "10-K", "10-Q", "Earnings Transcript", "Investor Deck", "Legal", "Industry Report"] as const;

export function DocumentLibraryPage() {
  const [type, setType] = useState<(typeof types)[number]>("all");
  const filtered = useMemo(() => documents.filter((d) => type === "all" || d.type === type), [type]);

  return (
    <PageContainer>
      <PageHeader
        eyebrow="Intelligence"
        title="Document Library"
        description="Every document ingested across active workspaces, automatically parsed and indexed for retrieval."
        actions={
          <Button variant="primary" size="md">
            <UploadCloud size={15} /> Upload
          </Button>
        }
      />
      <div className="px-8">
        <div className="flex gap-1.5 mb-6 overflow-x-auto no-scrollbar">
          {types.map((t) => (
            <button
              key={t}
              onClick={() => setType(t)}
              className={cn(
                "shrink-0 rounded-full border px-3.5 py-1.5 text-xs font-medium transition-colors",
                type === t ? "border-[var(--color-gold-500)]/40 bg-[var(--color-gold-500)]/[0.1] text-[var(--color-gold-300)]" : "border-[var(--color-border-hairline)] text-[var(--color-ink-3)] hover:text-[var(--color-ink-0)]"
              )}
            >
              {t === "all" ? "All types" : t}
            </button>
          ))}
        </div>

        <Reveal>
          <GlassCard className="overflow-hidden" raised>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--color-border-hairline)] text-left text-[11px] uppercase tracking-wider text-[var(--color-ink-4)]">
                  <th className="px-5 py-3 font-medium">Document</th>
                  <th className="px-5 py-3 font-medium">Company</th>
                  <th className="px-5 py-3 font-medium">Type</th>
                  <th className="px-5 py-3 font-medium">Uploaded</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((d) => (
                  <tr key={d.id} className="border-b border-[var(--color-border-hairline)] last:border-0 hover:bg-white/[0.02] transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2.5">
                        <FileText size={15} className="text-[var(--color-ink-4)] shrink-0" />
                        <span className="text-[var(--color-ink-0)] font-medium truncate max-w-xs">{d.name}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3.5">
                      <Link to={`/companies/${d.companyId}`} className="text-[var(--color-ink-2)] hover:text-[var(--color-gold-300)] transition-colors">
                        {getCompany(d.companyId)?.name}
                      </Link>
                    </td>
                    <td className="px-5 py-3.5 text-[var(--color-ink-2)]">{d.type}</td>
                    <td className="px-5 py-3.5 font-mono text-xs text-[var(--color-ink-3)]">{d.uploaded}</td>
                    <td className="px-5 py-3.5">
                      <Badge tone={statusTone[d.status]} dot>
                        {d.status === "processed" ? `${d.confidence}% parsed` : d.status}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </GlassCard>
        </Reveal>
      </div>
    </PageContainer>
  );
}
