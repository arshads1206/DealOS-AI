import { Link } from "react-router-dom";
import { PageHeader, PageContainer, Reveal } from "@/components/layout/PageHeader";
import { GlassCard } from "@/components/ui/GlassCard";
import { companies } from "@/lib/mockData";
import { formatCurrency, cn } from "@/lib/utils";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";
import { TrendingUp, TrendingDown } from "lucide-react";

const comparisonData = companies.map((c) => {
  const latest = c.history[c.history.length - 1];
  return {
    name: c.ticker,
    revenue: latest.revenue,
    ebitda: latest.ebitda,
    margin: Number(((latest.ebitda / latest.revenue) * 100).toFixed(1)),
  };
});

export function FinancialAnalysisPage() {
  return (
    <PageContainer>
      <PageHeader
        eyebrow="Intelligence"
        title="Financial Analysis"
        description="Extracted KPIs compared across every active workspace, refreshed automatically as new filings are processed."
      />

      <div className="px-8 space-y-4">
        <Reveal>
          <GlassCard className="p-6" raised>
            <p className="font-display text-lg text-[var(--color-ink-0)] mb-4">Latest Period Revenue &amp; EBITDA by Company</p>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={comparisonData} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
                <CartesianGrid stroke="rgba(245,243,238,0.05)" vertical={false} />
                <XAxis dataKey="name" tick={{ fill: "var(--color-ink-3)", fontSize: 11, fontFamily: "IBM Plex Mono" }} axisLine={{ stroke: "rgba(245,243,238,0.08)" }} tickLine={false} />
                <YAxis tick={{ fill: "var(--color-ink-3)", fontSize: 11, fontFamily: "IBM Plex Mono" }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${v}M`} width={52} />
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
                  cursor={{ fill: "rgba(227,196,107,0.04)" }}
                />
                <Legend wrapperStyle={{ fontSize: 12, fontFamily: "IBM Plex Sans", color: "var(--color-ink-3)" }} />
                <Bar dataKey="revenue" name="Revenue" fill="#C9A227" radius={[4, 4, 0, 0]} animationDuration={900} animationEasing="ease-out" />
                <Bar dataKey="ebitda" name="EBITDA" fill="#5B9BD5" radius={[4, 4, 0, 0]} animationDuration={900} animationEasing="ease-out" animationBegin={80} />
              </BarChart>
            </ResponsiveContainer>
          </GlassCard>
        </Reveal>

        <Reveal delay={0.05}>
          <GlassCard className="overflow-hidden" raised>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--color-border-hairline)] text-left text-[11px] uppercase tracking-wider text-[var(--color-ink-4)]">
                  <th className="px-5 py-3 font-medium">Company</th>
                  <th className="px-5 py-3 font-medium text-right">Deal Value</th>
                  <th className="px-5 py-3 font-medium text-right">Revenue</th>
                  <th className="px-5 py-3 font-medium text-right">EBITDA Margin</th>
                  <th className="px-5 py-3 font-medium text-right">IRR</th>
                  <th className="px-5 py-3 font-medium text-right">MOIC</th>
                </tr>
              </thead>
              <tbody>
                {companies.map((c) => {
                  const latest = c.history[c.history.length - 1];
                  const margin = ((latest.ebitda / latest.revenue) * 100).toFixed(1);
                  return (
                    <tr key={c.id} className="border-b border-[var(--color-border-hairline)] last:border-0 hover:bg-white/[0.02] transition-colors">
                      <td className="px-5 py-3.5">
                        <Link to={`/companies/${c.id}`} className="text-[var(--color-ink-0)] font-medium hover:text-[var(--color-gold-300)] transition-colors">
                          {c.name}
                        </Link>
                      </td>
                      <td className="px-5 py-3.5 text-right font-mono text-[var(--color-ink-1)] tabular-nums">{formatCurrency(c.dealValue)}</td>
                      <td className="px-5 py-3.5 text-right font-mono text-[var(--color-ink-1)] tabular-nums">${latest.revenue}M</td>
                      <td className="px-5 py-3.5 text-right font-mono text-[var(--color-ink-1)] tabular-nums">{margin}%</td>
                      <td className={cn("px-5 py-3.5 text-right font-mono tabular-nums flex items-center justify-end gap-1", c.irr > 20 ? "text-[var(--color-emerald)]" : "text-[var(--color-ink-1)]")}>
                        {c.irr > 0 ? (c.irr > 20 ? <TrendingUp size={12} /> : <TrendingDown size={12} />) : null}
                        {c.irr > 0 ? `${c.irr}%` : "—"}
                      </td>
                      <td className="px-5 py-3.5 text-right font-mono text-[var(--color-ink-1)] tabular-nums">{c.moic > 0 ? `${c.moic}x` : "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </GlassCard>
        </Reveal>
      </div>
    </PageContainer>
  );
}
