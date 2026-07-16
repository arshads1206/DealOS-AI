import { PageHeader, PageContainer, Reveal } from "@/components/layout/PageHeader";
import { StatCard } from "@/components/ui/StatCard";
import { GlassCard } from "@/components/ui/GlassCard";
import { Badge, SeverityBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Divider } from "@/components/ui/Divider";
import { AumTrendChart } from "@/components/charts/AumTrendChart";
import { RiskHeatmap } from "@/components/charts/RiskHeatmap";
import {
  companies,
  portfolioSummary,
  activity,
  reports,
  risks,
} from "@/lib/mockData";
import { formatCurrency } from "@/lib/utils";
import { Link } from "react-router-dom";
import {
  Wallet,
  Building2,
  TrendingUp,
  ShieldAlert,
  ArrowUpRight,
  Sparkles,
  Upload,
  FileText,
  Plus,
  Bot,
} from "lucide-react";
import { motion } from "framer-motion";

const kindIcon: Record<string, string> = {
  upload: "▲",
  analysis: "◆",
  report: "▣",
  comment: "●",
  risk: "▲",
};

export function DashboardPage() {
  const criticalRisks = risks.filter((r) => r.severity === "critical" && r.status === "open");

  return (
    <PageContainer>
      <PageHeader
        eyebrow="Portfolio Command Center"
        title="Good morning, Ananya"
        description="Four active diligence workstreams, two critical risks surfaced overnight, and one report awaiting your sign-off."
        actions={
          <>
            <Button variant="secondary" size="md">
              <Upload size={15} /> Upload document
            </Button>
            <Button variant="primary" size="md">
              <Plus size={15} /> New workspace
            </Button>
          </>
        }
      />

      <div className="px-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Assets Under Diligence" value={portfolioSummary.totalAUM} formatter={(v) => formatCurrency(v)} icon={<Wallet size={16} />} delta="+6.2% vs last quarter" />
        <StatCard label="Active Diligence" value={portfolioSummary.activeDeals} icon={<Building2 size={16} />} delta={`${portfolioSummary.portfolioCompanies} in portfolio`} />
        <StatCard label="Average IRR" value={portfolioSummary.avgIRR} suffix="%" icon={<TrendingUp size={16} />} delta="+1.4pp vs prior period" />
        <StatCard
          label="Open Risks"
          value={portfolioSummary.openRisks}
          icon={<ShieldAlert size={16} />}
          delta={`${criticalRisks.length} critical`}
          deltaTone="crimson"
        />
      </div>

      <div className="px-8 mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Left: AUM trend + companies */}
        <div className="lg:col-span-2 space-y-4">
          <Reveal>
            <GlassCard className="p-6" raised>
              <div className="flex items-center justify-between mb-1">
                <div>
                  <p className="text-xs uppercase tracking-wider text-[var(--color-ink-3)]">Assets Under Diligence</p>
                  <p className="font-display text-2xl text-[var(--color-ink-0)] mt-0.5">$4.82B</p>
                </div>
                <Badge tone="emerald">+6.2%</Badge>
              </div>
              <AumTrendChart />
            </GlassCard>
          </Reveal>

          <Reveal delay={0.05}>
            <GlassCard className="p-0" raised>
              <div className="flex items-center justify-between px-6 pt-5 pb-4">
                <p className="font-display text-lg text-[var(--color-ink-0)]">Portfolio Companies</p>
                <Link to="/companies" className="text-xs text-[var(--color-gold-400)] hover:text-[var(--color-gold-300)] flex items-center gap-1">
                  View all <ArrowUpRight size={12} />
                </Link>
              </div>
              <Divider />
              <div>
                {companies.slice(0, 5).map((c, i) => (
                  <Link
                    to={`/companies/${c.id}`}
                    key={c.id}
                    className={`flex items-center justify-between px-6 py-3.5 hover:bg-white/[0.02] transition-colors ${i !== 0 ? "border-t border-[var(--color-border-hairline)]" : ""}`}
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-[var(--color-ink-0)] truncate">{c.name}</p>
                        <span className="font-mono text-[11px] text-[var(--color-ink-4)]">{c.ticker}</span>
                      </div>
                      <p className="text-xs text-[var(--color-ink-3)] mt-0.5">{c.sector}</p>
                    </div>
                    <div className="flex items-center gap-6 shrink-0">
                      <div className="text-right hidden sm:block">
                        <p className="font-mono text-sm text-[var(--color-ink-0)] tabular-nums">{formatCurrency(c.dealValue)}</p>
                        <p className="text-[11px] text-[var(--color-ink-3)]">deal value</p>
                      </div>
                      <div className="text-right hidden md:block">
                        <p className="font-mono text-sm text-[var(--color-emerald)] tabular-nums">{c.irr > 0 ? `${c.irr}%` : "—"}</p>
                        <p className="text-[11px] text-[var(--color-ink-3)]">IRR</p>
                      </div>
                      <Badge tone={c.stage === "active-dd" ? "gold" : c.stage === "watchlist" ? "crimson" : c.stage === "closed" ? "neutral" : "emerald"}>
                        {c.stage.replace("-", " ")}
                      </Badge>
                    </div>
                  </Link>
                ))}
              </div>
            </GlassCard>
          </Reveal>

          <Reveal delay={0.1}>
            <GlassCard className="p-6" raised>
              <p className="font-display text-lg text-[var(--color-ink-0)] mb-4">Risk Heatmap</p>
              <RiskHeatmap />
            </GlassCard>
          </Reveal>
        </div>

        {/* Right: AI Insights + Activity */}
        <div className="space-y-4">
          <Reveal delay={0.05}>
            <GlassCard className="p-5" raised>
              <div className="flex items-center gap-2 mb-4">
                <Sparkles size={15} className="text-[var(--color-gold-400)]" />
                <p className="font-display text-base text-[var(--color-ink-0)]">AI Insights</p>
              </div>
              <div className="space-y-3">
                <InsightRow
                  tone="crimson"
                  text="Northwind Logistics covenant headroom fell to 0.3x — a breach is plausible within two quarters."
                  href="/companies/northwind-logistics/risks"
                />
                <InsightRow
                  tone="amber"
                  text="Harborline reserve restatement adds 340bps of adverse development to commercial casualty lines."
                  href="/companies/harborline-insurance/risks"
                />
                <InsightRow
                  tone="emerald"
                  text="Vertex Semiconductor FY26E EBITDA margin expands to 32.3%, ahead of sector median."
                  href="/companies/vertex-semiconductors/financials"
                />
              </div>
              <Button variant="outline" size="sm" className="w-full mt-4 justify-center">
                <Bot size={14} /> Ask AI Analyst
              </Button>
            </GlassCard>
          </Reveal>

          <Reveal delay={0.1}>
            <GlassCard className="p-5" raised>
              <p className="font-display text-base text-[var(--color-ink-0)] mb-4">Recent Activity</p>
              <div className="space-y-4">
                {activity.slice(0, 6).map((a) => (
                  <div key={a.id} className="flex gap-3">
                    <span className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[var(--color-gold-500)]/[0.1] text-[10px] text-[var(--color-gold-400)]">
                      {kindIcon[a.kind]}
                    </span>
                    <div className="min-w-0">
                      <p className="text-[13px] text-[var(--color-ink-1)] leading-snug">
                        <span className="text-[var(--color-ink-0)] font-medium">{a.actor}</span> {a.action}{" "}
                        <span className="text-[var(--color-ink-0)]">{a.target}</span>
                      </p>
                      <p className="text-[11px] text-[var(--color-ink-4)] mt-0.5 font-mono">{a.timestamp}</p>
                    </div>
                  </div>
                ))}
              </div>
            </GlassCard>
          </Reveal>

          <Reveal delay={0.15}>
            <GlassCard className="p-5" raised>
              <div className="flex items-center justify-between mb-4">
                <p className="font-display text-base text-[var(--color-ink-0)]">Recent Reports</p>
                <Link to="/reports" className="text-xs text-[var(--color-gold-400)] hover:text-[var(--color-gold-300)]">
                  View all
                </Link>
              </div>
              <div className="space-y-3">
                {reports.slice(0, 3).map((r) => (
                  <div key={r.id} className="flex items-start gap-2.5">
                    <FileText size={14} className="mt-0.5 text-[var(--color-ink-4)] shrink-0" />
                    <div className="min-w-0">
                      <p className="text-[13px] text-[var(--color-ink-1)] leading-snug truncate">{r.title}</p>
                      <p className="text-[11px] text-[var(--color-ink-4)] font-mono mt-0.5">{r.date}</p>
                    </div>
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

function InsightRow({ tone, text, href }: { tone: "crimson" | "amber" | "emerald"; text: string; href: string }) {
  return (
    <Link to={href} className="group block">
      <motion.div whileHover={{ x: 2 }} className="flex items-start gap-2.5 rounded-lg p-2 -mx-2 hover:bg-white/[0.03] transition-colors">
        <SeverityBadgeDot tone={tone} />
        <p className="text-[13px] leading-snug text-[var(--color-ink-1)] group-hover:text-[var(--color-ink-0)] transition-colors">{text}</p>
      </motion.div>
    </Link>
  );
}

function SeverityBadgeDot({ tone }: { tone: "crimson" | "amber" | "emerald" }) {
  const colors = {
    crimson: "bg-[var(--color-crimson)]",
    amber: "bg-[var(--color-amber)]",
    emerald: "bg-[var(--color-emerald)]",
  };
  return <span className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${colors[tone]}`} />;
}
