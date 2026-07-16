import { useParams } from "react-router-dom";
import { GlassCard } from "@/components/ui/GlassCard";
import { Reveal } from "@/components/layout/PageHeader";
import { getCompany } from "@/lib/mockData";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";

export function FinancialsTab() {
  const { id } = useParams();
  const company = getCompany(id!);
  if (!company) return null;

  const latest = company.history[company.history.length - 1];
  const prior = company.history[company.history.length - 2];
  const revenueGrowth = (((latest.revenue - prior.revenue) / prior.revenue) * 100).toFixed(1);
  const ebitdaMargin = ((latest.ebitda / latest.revenue) * 100).toFixed(1);
  const netMargin = ((latest.netIncome / latest.revenue) * 100).toFixed(1);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiTile label="Revenue (FY26E)" value={`$${latest.revenue}M`} sub={`+${revenueGrowth}% YoY`} tone="emerald" />
        <KpiTile label="EBITDA Margin" value={`${ebitdaMargin}%`} sub={`$${latest.ebitda}M EBITDA`} />
        <KpiTile label="Net Margin" value={`${netMargin}%`} sub={`$${latest.netIncome}M net income`} />
        <KpiTile label="Risk Score" value={`${company.riskScore}/100`} sub={company.riskScore > 50 ? "Elevated" : "Within tolerance"} tone={company.riskScore > 50 ? "crimson" : "emerald"} />
      </div>

      <Reveal>
        <GlassCard className="p-6" raised>
          <p className="font-display text-lg text-[var(--color-ink-0)] mb-1">Revenue, EBITDA &amp; Net Income</p>
          <p className="text-xs text-[var(--color-ink-3)] mb-4">Extracted from filed financial statements and management presentations, in USD millions.</p>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={company.history} margin={{ top: 8, right: 8, left: -12, bottom: 0 }} barGap={4}>
              <CartesianGrid stroke="rgba(245,243,238,0.05)" vertical={false} />
              <XAxis dataKey="period" tick={{ fill: "var(--color-ink-3)", fontSize: 11, fontFamily: "IBM Plex Mono" }} axisLine={{ stroke: "rgba(245,243,238,0.08)" }} tickLine={false} />
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
              <Bar dataKey="netIncome" name="Net Income" fill="#34B27F" radius={[4, 4, 0, 0]} animationDuration={900} animationEasing="ease-out" animationBegin={160} />
            </BarChart>
          </ResponsiveContainer>
        </GlassCard>
      </Reveal>

      <Reveal delay={0.05}>
        <GlassCard className="overflow-hidden" raised>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--color-border-hairline)] text-left text-[11px] uppercase tracking-wider text-[var(--color-ink-4)]">
                <th className="px-5 py-3 font-medium">Period</th>
                <th className="px-5 py-3 font-medium text-right">Revenue</th>
                <th className="px-5 py-3 font-medium text-right">EBITDA</th>
                <th className="px-5 py-3 font-medium text-right">EBITDA Margin</th>
                <th className="px-5 py-3 font-medium text-right">Net Income</th>
              </tr>
            </thead>
            <tbody>
              {company.history.map((h) => (
                <tr key={h.period} className="border-b border-[var(--color-border-hairline)] last:border-0 hover:bg-white/[0.02] transition-colors font-mono">
                  <td className="px-5 py-3 text-[var(--color-ink-0)]">{h.period}</td>
                  <td className="px-5 py-3 text-right text-[var(--color-ink-1)] tabular-nums">${h.revenue}M</td>
                  <td className="px-5 py-3 text-right text-[var(--color-ink-1)] tabular-nums">${h.ebitda}M</td>
                  <td className="px-5 py-3 text-right text-[var(--color-ink-1)] tabular-nums">{((h.ebitda / h.revenue) * 100).toFixed(1)}%</td>
                  <td className="px-5 py-3 text-right text-[var(--color-ink-1)] tabular-nums">${h.netIncome}M</td>
                </tr>
              ))}
            </tbody>
          </table>
        </GlassCard>
      </Reveal>
    </div>
  );
}

function KpiTile({ label, value, sub, tone }: { label: string; value: string; sub: string; tone?: "emerald" | "crimson" }) {
  return (
    <GlassCard className="p-4" interactive>
      <p className="text-[11px] uppercase tracking-wider text-[var(--color-ink-3)]">{label}</p>
      <p className="figure-display text-xl font-semibold text-[var(--color-ink-0)] mt-2">{value}</p>
      <p className={`text-xs mt-1 font-mono ${tone === "emerald" ? "text-[var(--color-emerald)]" : tone === "crimson" ? "text-[var(--color-crimson)]" : "text-[var(--color-ink-3)]"}`}>{sub}</p>
    </GlassCard>
  );
}
