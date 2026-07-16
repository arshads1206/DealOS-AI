import { useParams } from "react-router-dom";
import { GlassCard } from "@/components/ui/GlassCard";
import { Reveal } from "@/components/layout/PageHeader";
import { getActivity } from "@/lib/mockData";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";

const kindTone = {
  upload: "ice",
  analysis: "gold",
  report: "emerald",
  comment: "neutral",
  risk: "crimson",
} as const;

export function ActivityTab() {
  const { id } = useParams();
  const items = getActivity(id!);

  return (
    <GlassCard className="divide-y divide-[var(--color-border-hairline)]" raised>
      {items.map((a, i) => (
        <Reveal key={a.id} delay={Math.min(i * 0.04, 0.16)}>
          <div className="flex items-start gap-3 px-5 py-4">
            <Avatar name={a.actor === "AI Analyst" ? "AI Analyst" : a.actor} size={30} />
            <div className="min-w-0 flex-1">
              <p className="text-sm text-[var(--color-ink-1)]">
                <span className="text-[var(--color-ink-0)] font-medium">{a.actor}</span> {a.action}{" "}
                <span className="text-[var(--color-ink-0)]">{a.target}</span>
              </p>
              <p className="text-[11px] text-[var(--color-ink-4)] font-mono mt-1">{a.timestamp}</p>
            </div>
            <Badge tone={kindTone[a.kind]}>{a.kind}</Badge>
          </div>
        </Reveal>
      ))}
    </GlassCard>
  );
}
