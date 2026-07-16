import { Search, Bell, Command } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { Avatar } from "@/components/ui/Avatar";
import { getCompany } from "@/lib/mockData";

const labelMap: Record<string, string> = {
  companies: "Companies",
  documents: "Document Library",
  reports: "Investment Reports",
  "financial-analysis": "Financial Analysis",
  "risk-analysis": "Risk Analysis",
  "ai-analyst": "AI Analyst",
  settings: "Settings",
  admin: "Admin",
  notifications: "Notifications",
  profile: "Profile",
  search: "Search",
  overview: "Overview",
  financials: "Financials",
  risks: "Risks",
  reports_tab: "Reports",
  timeline: "Timeline",
  activity: "Activity",
};

export function Topbar() {
  const location = useLocation();
  const parts = location.pathname.split("/").filter(Boolean);

  const crumbs = parts.map((part, i) => {
    const company = getCompany(part);
    const label = company ? company.name : labelMap[part] ?? part;
    const href = "/" + parts.slice(0, i + 1).join("/");
    return { label, href, isLast: i === parts.length - 1 };
  });

  return (
    <header className="flex h-16 shrink-0 items-center gap-4 border-b border-[var(--color-border-hairline)] bg-[var(--color-bg-raised)]/60 backdrop-blur-xl px-6">
      <div className="flex min-w-0 items-center gap-1.5 text-[13px]">
        <Link to="/" className="text-[var(--color-ink-3)] hover:text-[var(--color-ink-0)] transition-colors">
          DealOS
        </Link>
        {crumbs.map((c) => (
          <span key={c.href} className="flex items-center gap-1.5 min-w-0">
            <span className="text-[var(--color-ink-4)]">/</span>
            {c.isLast ? (
              <span className="truncate text-[var(--color-ink-0)] font-medium">{c.label}</span>
            ) : (
              <Link to={c.href} className="truncate text-[var(--color-ink-3)] hover:text-[var(--color-ink-0)] transition-colors">
                {c.label}
              </Link>
            )}
          </span>
        ))}
      </div>

      <div className="flex-1" />

      <button className="group hidden md:flex items-center gap-2 rounded-lg border border-[var(--color-border-hairline)] bg-white/[0.02] px-3 py-1.5 text-[13px] text-[var(--color-ink-3)] hover:border-[var(--color-border-strong)] transition-colors w-64">
        <Search size={14} />
        <span className="flex-1 text-left">Search deals, documents, filings…</span>
        <span className="flex items-center gap-0.5 rounded border border-white/10 px-1 text-[10px] text-[var(--color-ink-4)]">
          <Command size={10} />K
        </span>
      </button>

      <button className="relative flex h-9 w-9 items-center justify-center rounded-lg text-[var(--color-ink-2)] hover:text-[var(--color-ink-0)] hover:bg-white/[0.04] transition-colors">
        <Bell size={17} strokeWidth={1.75} />
        <span className="absolute top-2 right-2 h-1.5 w-1.5 rounded-full bg-[var(--color-gold-400)]" />
      </button>

      <Link to="/profile" className="flex items-center gap-2">
        <Avatar name="Ananya Rao" size={32} />
      </Link>
    </header>
  );
}
