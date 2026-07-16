import { Link } from "react-router-dom";
import { PageHeader, PageContainer, Reveal } from "@/components/layout/PageHeader";
import { GlassCard } from "@/components/ui/GlassCard";
import { Badge } from "@/components/ui/Badge";
import { activity, risks, getCompany } from "@/lib/mockData";
import { ShieldAlert, Upload, FileBarChart, MessageSquare, Sparkles } from "lucide-react";

const kindIcon = {
  upload: Upload,
  analysis: Sparkles,
  report: FileBarChart,
  comment: MessageSquare,
  risk: ShieldAlert,
};

export function NotificationsPage() {
  const criticalRisks = risks.filter((r) => r.severity === "critical" && r.status === "open");

  return (
    <PageContainer>
      <PageHeader eyebrow="System" title="Notifications" description="Everything that needs your attention, in one stream." />

      <div className="px-8 max-w-2xl space-y-6">
        {criticalRisks.length > 0 && (
          <Reveal>
            <div>
              <p className="text-xs uppercase tracking-wider text-[var(--color-crimson)] mb-3">Needs attention</p>
              <div className="space-y-2">
                {criticalRisks.map((r) => (
                  <Link key={r.id} to={`/companies/${r.companyId}/risks`}>
                    <GlassCard interactive className="p-4 flex items-start gap-3 border-[var(--color-crimson)]/25">
                      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--color-crimson)]/[0.12] text-[var(--color-crimson)]">
                        <ShieldAlert size={15} />
                      </span>
                      <div className="min-w-0">
                        <p className="text-sm text-[var(--color-ink-0)] font-medium">{r.title}</p>
                        <p className="text-xs text-[var(--color-ink-3)] mt-0.5">
                          {getCompany(r.companyId)?.name} · {r.detected}
                        </p>
                      </div>
                      <Badge tone="crimson" className="ml-auto shrink-0">
                        critical
                      </Badge>
                    </GlassCard>
                  </Link>
                ))}
              </div>
            </div>
          </Reveal>
        )}

        <Reveal delay={0.05}>
          <div>
            <p className="text-xs uppercase tracking-wider text-[var(--color-ink-3)] mb-3">Recent</p>
            <div className="space-y-2">
              {activity.map((a) => {
                const Icon = kindIcon[a.kind];
                return (
                  <GlassCard key={a.id} className="p-4 flex items-start gap-3">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--color-gold-500)]/[0.1] text-[var(--color-gold-400)]">
                      <Icon size={14} />
                    </span>
                    <div className="min-w-0">
                      <p className="text-[13px] text-[var(--color-ink-1)] leading-snug">
                        <span className="text-[var(--color-ink-0)] font-medium">{a.actor}</span> {a.action}{" "}
                        <span className="text-[var(--color-ink-0)]">{a.target}</span>
                      </p>
                      <p className="text-[11px] text-[var(--color-ink-4)] mt-0.5 font-mono">{a.timestamp}</p>
                    </div>
                  </GlassCard>
                );
              })}
            </div>
          </div>
        </Reveal>
      </div>
    </PageContainer>
  );
}
