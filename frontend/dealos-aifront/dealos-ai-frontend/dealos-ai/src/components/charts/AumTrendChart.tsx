import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { kpiTrend } from "@/lib/mockData";

export function AumTrendChart() {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={kpiTrend} margin={{ top: 10, right: 8, left: -18, bottom: 0 }}>
        <defs>
          <linearGradient id="aum-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#C9A227" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#C9A227" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="rgba(245,243,238,0.05)" vertical={false} />
        <XAxis
          dataKey="period"
          tick={{ fill: "var(--color-ink-3)", fontSize: 11, fontFamily: "IBM Plex Mono" }}
          axisLine={{ stroke: "rgba(245,243,238,0.08)" }}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: "var(--color-ink-3)", fontSize: 11, fontFamily: "IBM Plex Mono" }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) => `$${v}B`}
          width={48}
        />
        <Tooltip
          contentStyle={{
            background: "#17181d",
            border: "1px solid rgba(201,162,39,0.24)",
            borderRadius: 10,
            fontSize: 12,
            fontFamily: "IBM Plex Mono",
          }}
          labelStyle={{ color: "#A6A6AE" }}
          formatter={(v: any) => [`$${Number(v).toFixed(2)}B`, "AUM"]}
        />
        <Area
          type="monotone"
          dataKey="value"
          stroke="#D4B34A"
          strokeWidth={2}
          fill="url(#aum-fill)"
          activeDot={{ r: 4, fill: "#E3C46B", stroke: "#0a0a0c", strokeWidth: 2 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
