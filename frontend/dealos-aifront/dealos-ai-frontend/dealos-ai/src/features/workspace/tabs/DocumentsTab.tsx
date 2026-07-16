import { useParams } from "react-router-dom";
import { GlassCard } from "@/components/ui/GlassCard";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Reveal } from "@/components/layout/PageHeader";
import { getDocuments } from "@/lib/mockData";
import { UploadCloud, FileText, MoreHorizontal } from "lucide-react";

const statusTone = {
  processed: "emerald",
  processing: "amber",
  queued: "neutral",
} as const;

export function DocumentsTab() {
  const { id } = useParams();
  const docs = getDocuments(id!);

  return (
    <div className="space-y-4">
      <Reveal>
        <label className="group flex flex-col items-center justify-center gap-2 rounded-2xl border border-dashed border-[var(--color-border-strong)] bg-[var(--color-gold-500)]/[0.03] px-6 py-10 text-center cursor-pointer transition-colors hover:bg-[var(--color-gold-500)]/[0.06]">
          <UploadCloud size={26} className="text-[var(--color-gold-500)]/70 group-hover:text-[var(--color-gold-400)] transition-colors" />
          <p className="text-sm text-[var(--color-ink-1)]">
            <span className="text-[var(--color-gold-300)] font-medium">Click to upload</span> or drag and drop
          </p>
          <p className="text-xs text-[var(--color-ink-4)]">10-Ks, 10-Qs, earnings transcripts, investor decks, legal documents — PDF up to 100MB</p>
          <input type="file" multiple className="hidden" />
        </label>
      </Reveal>

      <Reveal delay={0.05}>
        <GlassCard className="overflow-hidden" raised>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--color-border-hairline)] text-left text-[11px] uppercase tracking-wider text-[var(--color-ink-4)]">
                <th className="px-5 py-3 font-medium">Document</th>
                <th className="px-5 py-3 font-medium">Type</th>
                <th className="px-5 py-3 font-medium">Uploaded</th>
                <th className="px-5 py-3 font-medium">Size</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium" />
              </tr>
            </thead>
            <tbody>
              {docs.map((d) => (
                <tr key={d.id} className="border-b border-[var(--color-border-hairline)] last:border-0 hover:bg-white/[0.02] transition-colors">
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-2.5">
                      <FileText size={15} className="text-[var(--color-ink-4)] shrink-0" />
                      <span className="text-[var(--color-ink-0)] font-medium truncate max-w-xs">{d.name}</span>
                    </div>
                  </td>
                  <td className="px-5 py-3.5 text-[var(--color-ink-2)]">{d.type}</td>
                  <td className="px-5 py-3.5 font-mono text-xs text-[var(--color-ink-3)]">{d.uploaded}</td>
                  <td className="px-5 py-3.5 font-mono text-xs text-[var(--color-ink-3)]">{d.size}</td>
                  <td className="px-5 py-3.5">
                    <Badge tone={statusTone[d.status]} dot>
                      {d.status === "processed" ? `${d.confidence}% parsed` : d.status}
                    </Badge>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <Button variant="ghost" size="icon">
                      <MoreHorizontal size={15} />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </GlassCard>
      </Reveal>
    </div>
  );
}
