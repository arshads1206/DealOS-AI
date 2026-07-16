import { PageHeader, PageContainer, Reveal } from "@/components/layout/PageHeader";
import { GlassCard } from "@/components/ui/GlassCard";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Divider } from "@/components/ui/Divider";
import { activity } from "@/lib/mockData";
import { Mail, Building2, Calendar } from "lucide-react";
import type { ReactNode } from "react";

export function ProfilePage() {
  const recentActivity = activity.filter((a) => a.actor === "R. Nair").slice(0, 5);

  return (
    <PageContainer>
      <PageHeader eyebrow="System" title="Profile" description="Your role, coverage, and recent activity across DealOS AI." />

      <div className="px-8 grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Reveal>
          <GlassCard className="p-6 text-center" raised>
            <Avatar name="Ananya Rao" size={64} className="mx-auto text-lg" />
            <p className="font-display text-lg text-[var(--color-ink-0)] mt-4">Ananya Rao</p>
            <p className="text-sm text-[var(--color-ink-3)]">Vice President, Private Equity</p>
            <Badge tone="gold" className="mt-3">
              Healthcare &amp; Industrials
            </Badge>
            <Divider className="my-5" />
            <div className="space-y-3 text-left">
              <InfoRow icon={<Mail size={13} />} text="ananya.rao@dealos.ai" />
              <InfoRow icon={<Building2 size={13} />} text="Meridian Capital Partners" />
              <InfoRow icon={<Calendar size={13} />} text="Joined March 2023" />
            </div>
          </GlassCard>
        </Reveal>

        <div className="lg:col-span-2 space-y-4">
          <Reveal delay={0.05}>
            <GlassCard className="p-6" raised>
              <p className="font-display text-lg text-[var(--color-ink-0)] mb-4">Coverage</p>
              <div className="grid grid-cols-3 gap-4 text-center">
                <Stat label="Active workspaces" value="4" />
                <Stat label="Reports authored" value="12" />
                <Stat label="Risks reviewed" value="38" />
              </div>
            </GlassCard>
          </Reveal>

          <Reveal delay={0.1}>
            <GlassCard className="p-6" raised>
              <p className="font-display text-lg text-[var(--color-ink-0)] mb-4">Recent Activity</p>
              <div className="space-y-4">
                {recentActivity.map((a) => (
                  <div key={a.id}>
                    <p className="text-[13px] text-[var(--color-ink-1)] leading-snug">
                      {a.action} <span className="text-[var(--color-ink-0)]">{a.target}</span>
                    </p>
                    <p className="text-[11px] text-[var(--color-ink-4)] font-mono mt-0.5">{a.timestamp}</p>
                  </div>
                ))}
              </div>
            </GlassCard>
          </Reveal>
        </div>
      </div>
    </PageContainer>
  );
}

function InfoRow({ icon, text }: { icon: ReactNode; text: string }) {
  return (
    <div className="flex items-center gap-2.5 text-sm text-[var(--color-ink-2)]">
      <span className="text-[var(--color-ink-4)]">{icon}</span>
      {text}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="font-mono text-2xl font-semibold text-[var(--color-gold-300)]">{value}</p>
      <p className="text-[11px] text-[var(--color-ink-3)] mt-1 uppercase tracking-wider">{label}</p>
    </div>
  );
}
