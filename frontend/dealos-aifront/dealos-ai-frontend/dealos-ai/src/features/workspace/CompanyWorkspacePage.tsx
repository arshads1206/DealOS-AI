import { Link, Outlet, useLocation, useNavigate, useParams } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  LayoutGrid,
  FolderOpen,
  LineChart,
  ShieldAlert,
  Bot,
  FileBarChart,
  History,
  Activity as ActivityIcon,
} from "lucide-react";
import { Tabs } from "@/components/ui/Tabs";
import { Badge } from "@/components/ui/Badge";
import { Avatar } from "@/components/ui/Avatar";
import { getCompany, getDocuments, getRisks } from "@/lib/mockData";
import { formatCurrency, cn } from "@/lib/utils";
import { EmptyState } from "@/components/ui/EmptyState";
import { Building2 } from "lucide-react";

const stageTone: Record<string, "gold" | "emerald" | "crimson" | "neutral"> = {
  "active-dd": "gold",
  portfolio: "emerald",
  watchlist: "crimson",
  closed: "neutral",
};

export function CompanyWorkspacePage() {
  const { id } = useParams();
  const company = id ? getCompany(id) : undefined;
  const navigate = useNavigate();
  const location = useLocation();

  if (!company) {
    return (
      <EmptyState
        icon={<Building2 size={32} strokeWidth={1.25} />}
        title="Company not found"
        description="This workspace doesn't exist or may have been archived."
      />
    );
  }

  const activeTab = location.pathname.split("/")[3] ?? "overview";
  const docCount = getDocuments(company.id).length;
  const riskCount = getRisks(company.id).filter((r) => r.status === "open").length;

  const tabs = [
    { id: "overview", label: "Overview", icon: <LayoutGrid size={14} /> },
    { id: "documents", label: "Documents", icon: <FolderOpen size={14} />, count: docCount },
    { id: "financials", label: "Financials", icon: <LineChart size={14} /> },
    { id: "risks", label: "Risks", icon: <ShieldAlert size={14} />, count: riskCount },
    { id: "ai-analyst", label: "AI Analyst", icon: <Bot size={14} /> },
    { id: "reports", label: "Reports", icon: <FileBarChart size={14} /> },
    { id: "timeline", label: "Timeline", icon: <History size={14} /> },
    { id: "activity", label: "Activity", icon: <ActivityIcon size={14} /> },
  ];

  return (
    <div className="pb-16">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }} className="px-8 pt-8">
        <Link to="/companies" className="inline-flex items-center gap-1.5 text-xs text-[var(--color-ink-3)] hover:text-[var(--color-ink-0)] transition-colors mb-4">
          <ArrowLeft size={12} /> Companies
        </Link>

        <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6">
          <div className="flex items-start gap-4 min-w-0">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-[var(--color-gold-500)]/25 bg-gradient-to-br from-[var(--color-gold-500)]/[0.12] to-transparent">
              <span className="font-display text-lg text-[var(--color-gold-300)]">{company.ticker.slice(0, 2)}</span>
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2.5 flex-wrap">
                <h1 className="font-display text-[26px] text-[var(--color-ink-0)]">{company.name}</h1>
                <Badge tone={stageTone[company.stage]}>{company.stage.replace("-", " ")}</Badge>
              </div>
              <p className="text-sm text-[var(--color-ink-3)] mt-1">
                {company.ticker} · {company.sector} · {company.geography}
              </p>
              <p className="text-sm text-[var(--color-ink-2)] mt-2 max-w-xl leading-relaxed">{company.description}</p>
            </div>
          </div>

          <div className="flex gap-6 shrink-0 lg:pl-6 lg:border-l lg:border-[var(--color-border-hairline)]">
            <Metric label="Deal Value" value={formatCurrency(company.dealValue)} />
            <Metric label="Ownership" value={`${company.ownership}%`} />
            <Metric label="IRR" value={company.irr > 0 ? `${company.irr}%` : "—"} tone="emerald" />
            <Metric label="MOIC" value={company.moic > 0 ? `${company.moic}x` : "—"} />
            <div className="flex flex-col items-center gap-1.5">
              <Avatar name={company.analyst} size={30} />
              <p className="text-[10px] text-[var(--color-ink-4)] whitespace-nowrap">{company.analyst}</p>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="sticky top-0 z-10 mt-6 bg-[var(--color-bg)]/85 backdrop-blur-xl px-8">
        <Tabs tabs={tabs} active={activeTab} onChange={(t) => navigate(`/companies/${company.id}/${t}`)} />
      </div>

      <div className="px-8 mt-6">
        <Outlet />
      </div>
    </div>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone?: "emerald" }) {
  return (
    <div>
      <p className={cn("font-mono text-base tabular-nums", tone === "emerald" ? "text-[var(--color-emerald)]" : "text-[var(--color-ink-0)]")}>{value}</p>
      <p className="text-[10px] uppercase tracking-wider text-[var(--color-ink-4)] mt-0.5">{label}</p>
    </div>
  );
}
