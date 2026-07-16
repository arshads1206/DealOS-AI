import { useParams } from "react-router-dom";
import { GlassCard } from "@/components/ui/GlassCard";
import { Reveal } from "@/components/layout/PageHeader";
import { getActivity } from "@/lib/mockData";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/ui/EmptyState";

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

  const isLoading = false; // Prepare for real API integration

  return (
    <GlassCard className="divide-y divide-[var(--color-border-hairline)]" raised>
      {isLoading ? (
        <div className="p-6 space-y-4">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      ) : items.length === 0 ? (
        <EmptyState
          icon={<div className="h-12 w-12 rounded-full bg-[var(--color-surface-2)] flex items-center justify-center">No Activity</div>}
          title="No recent activity"
          description="There is no recorded activity for this workspace yet."
        />
      ) : (
        items.map((a, i) => (
          <Reveal key={a.id} delay={Math.min(i * 0.04, 0.16)}>
            <div className="flex items-start gap-3 px-5 py-4 hover:bg-white/[0.02] transition-colors" tabIndex={0} role="listitem">
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
        ))
      )}
    </GlassCard>
  );
}
