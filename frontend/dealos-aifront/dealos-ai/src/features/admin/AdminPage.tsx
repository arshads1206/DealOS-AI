import { PageHeader, PageContainer, Reveal } from "@/components/layout/PageHeader";
import { GlassCard } from "@/components/ui/GlassCard";
import { Badge } from "@/components/ui/Badge";
import { Avatar } from "@/components/ui/Avatar";
import { Button } from "@/components/ui/Button";
import { StatCard } from "@/components/ui/StatCard";
import { UserPlus, Users, Building2, FileStack } from "lucide-react";

const teamMembers = [
  { name: "Ananya Rao", role: "Vice President", team: "Healthcare & Industrials", status: "active" },
  { name: "Rohan Nair", role: "Senior Analyst", team: "Healthcare & Industrials", status: "active" },
  { name: "Sanya Kapoor", role: "Associate", team: "Industrials & Transport", status: "active" },
  { name: "Alex Chen", role: "Senior Analyst", team: "Technology & Energy", status: "active" },
  { name: "Maria Alvarez", role: "Associate", team: "Consumer & Retail", status: "invited" },
];

export function AdminPage() {
  return (
    <PageContainer>
      <PageHeader
        eyebrow="System"
        title="Admin"
        description="Manage team access, organization-wide settings, and platform usage."
        actions={
          <Button variant="primary" size="md">
            <UserPlus size={15} /> Invite member
          </Button>
        }
      />

      <div className="px-8 grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <StatCard label="Active Users" value={12} icon={<Users size={16} />} delta="+2 this month" />
        <StatCard label="Workspaces" value={6} icon={<Building2 size={16} />} />
        <StatCard label="Documents Processed" value={1842} icon={<FileStack size={16} />} delta="+184 this week" />
      </div>

      <div className="px-8">
        <Reveal>
          <GlassCard className="overflow-hidden" raised>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--color-border-hairline)] text-left text-[11px] uppercase tracking-wider text-[var(--color-ink-4)]">
                  <th className="px-5 py-3 font-medium">Member</th>
                  <th className="px-5 py-3 font-medium">Role</th>
                  <th className="px-5 py-3 font-medium">Team</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                  <th className="px-5 py-3 font-medium" />
                </tr>
              </thead>
              <tbody>
                {teamMembers.map((m) => (
                  <tr key={m.name} className="border-b border-[var(--color-border-hairline)] last:border-0 hover:bg-white/[0.02] transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2.5">
                        <Avatar name={m.name} size={28} />
                        <span className="text-[var(--color-ink-0)] font-medium">{m.name}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-[var(--color-ink-2)]">{m.role}</td>
                    <td className="px-5 py-3.5 text-[var(--color-ink-2)]">{m.team}</td>
                    <td className="px-5 py-3.5">
                      <Badge tone={m.status === "active" ? "emerald" : "amber"} dot>
                        {m.status}
                      </Badge>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Button variant="ghost" size="sm">
                        Manage
                      </Button>
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
