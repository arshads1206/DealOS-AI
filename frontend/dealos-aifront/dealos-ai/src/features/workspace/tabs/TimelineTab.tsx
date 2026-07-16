import { useParams } from "react-router-dom";
import { Reveal } from "@/components/layout/PageHeader";
import { getTimeline } from "@/lib/mockData";
import { Milestone, FileText, Users, ShieldAlert, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

const kindIcon = {
  milestone: Milestone,
  document: FileText,
  meeting: Users,
  risk: ShieldAlert,
  financial: TrendingUp,
};

const kindTone = {
  milestone: "text-[var(--color-gold-400)] bg-[var(--color-gold-500)]/[0.12]",
  document: "text-[var(--color-ice)] bg-[var(--color-ice)]/[0.12]",
  meeting: "text-[var(--color-ink-2)] bg-white/[0.06]",
  risk: "text-[var(--color-crimson)] bg-[var(--color-crimson)]/[0.12]",
  financial: "text-[var(--color-emerald)] bg-[var(--color-emerald)]/[0.12]",
};

export function TimelineTab() {
  const { id } = useParams();
  const events = getTimeline(id!);

  return (
    <div className="max-w-2xl">
      <div className="relative pl-8">
        <div className="absolute left-[15px] top-2 bottom-2 w-px bg-[var(--color-border-hairline)]" />
        <div className="space-y-8">
          {events.map((e, i) => {
            const Icon = kindIcon[e.kind];
            return (
              <Reveal key={e.id} delay={Math.min(i * 0.06, 0.24)}>
                <div className="relative">
                  <div className={cn("absolute -left-8 flex h-8 w-8 items-center justify-center rounded-full", kindTone[e.kind])}>
                    <Icon size={14} />
                  </div>
                  <p className="text-[11px] font-mono text-[var(--color-ink-4)] mb-1">{e.date}</p>
                  <p className="font-display text-base text-[var(--color-ink-0)]">{e.title}</p>
                  <p className="text-sm text-[var(--color-ink-2)] mt-1 leading-relaxed">{e.description}</p>
                </div>
              </Reveal>
            );
          })}
        </div>
      </div>
    </div>
  );
}
