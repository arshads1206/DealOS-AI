import { useNavigate, useParams } from "react-router-dom";
import { GlassCard } from "@/components/ui/GlassCard";
import { SeverityBadge } from "@/components/ui/Badge";
import { Reveal } from "@/components/layout/PageHeader";
import { ResponsiveContainer, AreaChart, Area, XAxis, Tooltip } from "recharts";
import { getCompany, getRisks, getActivity, getDocuments } from "@/lib/mockData";
import { formatCurrency } from "@/lib/utils";
import { FileText, ShieldAlert, ArrowUpRight } from "lucide-react";

export function OverviewTab() {
  const { id } = useParams();
  const navigate = useNavigate();
  const company = getCompany(id!);
  if (!company) return null;

  const openRisks = getRisks(company.id).filter((r) => r.status === "open").slice(0, 3);
  const recentActivity = getActivity(company.id).slice(0, 4);
  const recentDocs = getDocuments(company.id).slice(0, 3);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className="lg:col-span-2 space-y-4">
        <Reveal>
          <GlassCard className="p-6" raised>
            <div className="flex items-center justify-between mb-4">
              <p className="font-display text-lg text-[var(--color-ink-0)]">Revenue &amp; EBITDA</p>
              <button onClick={() => navigate(`/companies/${company.id}/financials`)} className="text-xs text-[var(--color-gold-400)] hover:text-[var(--color-gold-300)] flex items-center gap-1">
                Full breakdown <ArrowUpRight size={12} />
              </button>
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={company.history} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
                <defs>
                  <linearGradient id="rev-fill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#C9A227" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#C9A227" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="ebitda-fill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#5B9BD5" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="#5B9BD5" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="period" tick={{ fill: "var(--color-ink-3)", fontSize: 11, fontFamily: "IBM Plex Mono" }} axisLine={{ stroke: "rgba(245,243,238,0.08)" }} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    background: "#17181d",
                    border: "1px solid rgba(201,162,39,0.28)",
                    borderRadius: 12,
                    fontSize: 12,
                    fontFamily: "IBM Plex Mono",
                    boxShadow: "0 20px 40px -12px rgba(0,0,0,0.7), 0 0 0 1px rgba(201,162,39,0.1)",
                    padding: "8px 12px",
                  }}
                  labelStyle={{ color: "#A6A6AE", marginBottom: 2 }}
                  cursor={{ stroke: "rgba(227,196,107,0.35)", strokeWidth: 1, strokeDasharray: "3 3" }}
                  formatter={(v: any, name: any) => [`$${v}M`, name === "revenue" ? "Revenue" : "EBITDA"]}
                />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke="#D4B34A"
                  strokeWidth={2}
                  fill="url(#rev-fill)"
                  animationDuration={1100}
                  animationEasing="ease-out"
                  activeDot={{ r: 4, fill: "#E3C46B", stroke: "#0a0a0c", strokeWidth: 2 }}
                />
                <Area
                  type="monotone"
                  dataKey="ebitda"
                  stroke="#5B9BD5"
                  strokeWidth={2}
                  fill="url(#ebitda-fill)"
                  animationDuration={1100}
                  animationEasing="ease-out"
                  animationBegin={100}
                  activeDot={{ r: 4, fill: "#7EB3E0", stroke: "#0a0a0c", strokeWidth: 2 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </GlassCard>
        </Reveal>

        <Reveal delay={0.05}>
          <GlassCard className="p-6" raised>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <ShieldAlert size={15} className="text-[var(--color-crimson)]" />
                <p className="font-display text-lg text-[var(--color-ink-0)]">Top Risks</p>
              </div>
              <button onClick={() => navigate(`/companies/${company.id}/risks`)} className="text-xs text-[var(--color-gold-400)] hover:text-[var(--color-gold-300)] flex items-center gap-1">
                View all <ArrowUpRight size={12} />
              </button>
            </div>
            <div className="space-y-3">
              {openRisks.map((r) => (
                <div key={r.id} className="flex items-start justify-between gap-3 p-3 rounded-lg bg-white/[0.02] border border-[var(--color-border-hairline)]">
                  <div className="min-w-0">
                    <p className="text-sm text-[var(--color-ink-0)] font-medium">{r.title}</p>
                    <p className="text-xs text-[var(--color-ink-3)] mt-1 line-clamp-2">{r.summary}</p>
                  </div>
                  <SeverityBadge severity={r.severity} />
                </div>
              ))}
              {openRisks.length === 0 && <p className="text-sm text-[var(--color-ink-3)]">No open risks flagged.</p>}
            </div>
          </GlassCard>
        </Reveal>
      </div>

      <div className="space-y-4">
        <Reveal delay={0.05}>
          <GlassCard className="p-5" raised>
            <p className="font-display text-base text-[var(--color-ink-0)] mb-4">Recent Documents</p>
            <div className="space-y-3">
              {recentDocs.map((d) => (
                <div key={d.id} className="flex items-start gap-2.5">
                  <FileText size={14} className="mt-0.5 text-[var(--color-ink-4)] shrink-0" />
                  <div className="min-w-0">
                    <p className="text-[13px] text-[var(--color-ink-1)] leading-snug truncate">{d.name}</p>
                    <p className="text-[11px] text-[var(--color-ink-4)] font-mono mt-0.5">
                      {d.type} · {d.uploaded}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </Reveal>

        <Reveal delay={0.1}>
          <GlassCard className="p-5" raised>
            <p className="font-display text-base text-[var(--color-ink-0)] mb-4">Recent Activity</p>
            <div className="space-y-4">
              {recentActivity.map((a) => (
                <div key={a.id}>
                  <p className="text-[13px] text-[var(--color-ink-1)] leading-snug">
                    <span className="text-[var(--color-ink-0)] font-medium">{a.actor}</span> {a.action} {a.target}
                  </p>
                  <p className="text-[11px] text-[var(--color-ink-4)] mt-0.5 font-mono">{a.timestamp}</p>
                </div>
              ))}
            </div>
          </GlassCard>
        </Reveal>

        <Reveal delay={0.15}>
          <GlassCard className="p-5" raised>
            <p className="text-xs uppercase tracking-wider text-[var(--color-ink-3)] mb-2">Deal Snapshot</p>
            <dl className="space-y-2.5">
              <Row label="Deal value" value={formatCurrency(company.dealValue)} />
              <Row label="Ownership" value={`${company.ownership}%`} />
              <Row label="Risk score" value={`${company.riskScore} / 100`} />
              <Row label="Lead analyst" value={company.analyst} />
              <Row label="Last activity" value={company.lastActivity} />
            </dl>
          </GlassCard>
        </Reveal>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between text-[13px]">
      <dt className="text-[var(--color-ink-3)]">{label}</dt>
      <dd className="font-mono text-[var(--color-ink-0)]">{value}</dd>
    </div>
  );
}
