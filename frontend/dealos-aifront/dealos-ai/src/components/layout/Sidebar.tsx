import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Building2,
  Search,
  LineChart,
  ShieldAlert,
  Bot,
  FolderOpen,
  FileBarChart,
  Settings,
  ShieldCheck,
  ChevronsLeft,
} from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import { cn } from "@/lib/utils";

const nav = [
  {
    section: "Workspace",
    items: [
      { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
      { to: "/companies", label: "Companies", icon: Building2 },
      { to: "/search", label: "Search", icon: Search },
    ],
  },
  {
    section: "Intelligence",
    items: [
      { to: "/financial-analysis", label: "Financial Analysis", icon: LineChart },
      { to: "/risk-analysis", label: "Risk Analysis", icon: ShieldAlert },
      { to: "/ai-analyst", label: "AI Analyst", icon: Bot },
      { to: "/documents", label: "Document Library", icon: FolderOpen },
      { to: "/reports", label: "Investment Reports", icon: FileBarChart },
    ],
  },
  {
    section: "System",
    items: [
      { to: "/admin", label: "Admin", icon: ShieldCheck },
      { to: "/settings", label: "Settings", icon: Settings },
    ],
  },
];

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useAppStore();

  return (
    <aside
      className={cn(
        "relative hidden md:flex flex-col shrink-0 border-r border-[var(--color-border-hairline)] bg-[var(--color-bg-raised)]/80 backdrop-blur-xl transition-all duration-300 ease-out",
        sidebarCollapsed ? "w-[76px]" : "w-[248px]"
      )}
    >
      {/* Brand mark */}
      <div className="flex items-center gap-3 px-5 h-16 shrink-0">
        <div className="relative flex h-8 w-8 shrink-0 items-center justify-center">
          <div className="pointer-events-none absolute inset-0 rounded-full bg-[var(--color-gold-500)]/20 blur-md animate-pulse-glow" />
          <svg viewBox="0 0 32 32" className="relative h-8 w-8">
            <circle cx="16" cy="16" r="14.5" fill="none" stroke="url(#brand-ring)" strokeWidth="1.4" opacity="0.7" />
            <text x="16" y="21" textAnchor="middle" fontFamily="Fraunces, serif" fontSize="15" fill="var(--color-gold-200)">
              D
            </text>
            <defs>
              <linearGradient id="brand-ring" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#E3C46B" />
                <stop offset="100%" stopColor="#8B6B2E" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        {!sidebarCollapsed && (
          <div className="leading-tight overflow-hidden">
            <p className="font-display text-[15px] text-[var(--color-ink-0)] whitespace-nowrap">DealOS AI</p>
            <p className="text-[10px] uppercase tracking-[0.14em] text-[var(--color-ink-3)] whitespace-nowrap">
              Investment Intelligence
            </p>
          </div>
        )}
      </div>

      <div className="ledger-rule mx-5" />

      <nav className="flex-1 overflow-y-auto no-scrollbar px-3 py-4 space-y-6">
        {nav.map((group) => (
          <div key={group.section}>
            {!sidebarCollapsed && (
              <p className="px-2 mb-2 text-[10px] font-medium uppercase tracking-[0.14em] text-[var(--color-ink-4)]">
                {group.section}
              </p>
            )}
            <div className="space-y-0.5">
              {group.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) =>
                    cn(
                      "group relative flex items-center gap-3 rounded-lg px-2.5 py-2 text-[13px] font-medium transition-colors duration-200",
                      isActive
                        ? "text-[var(--color-gold-200)] bg-[var(--color-gold-500)]/[0.09]"
                        : "text-[var(--color-ink-2)] hover:text-[var(--color-ink-0)] hover:bg-white/[0.04]"
                    )
                  }
                >
                  {({ isActive }) => (
                    <>
                      {isActive && (
                        <motion.span
                          layoutId="sidebar-active-bar"
                          transition={{ type: "spring", stiffness: 500, damping: 40 }}
                          className="absolute left-0 top-1/2 h-4 w-[2px] -translate-y-1/2 rounded-full bg-gradient-to-b from-[var(--color-gold-300)] to-[var(--color-gold-600)] shadow-[0_0_8px_rgba(201,162,39,0.6)]"
                        />
                      )}
                      <item.icon
                        size={17}
                        strokeWidth={1.75}
                        className="shrink-0 transition-transform duration-200 group-hover:scale-110 group-hover:-translate-y-px"
                      />
                      {!sidebarCollapsed && <span className="truncate">{item.label}</span>}
                    </>
                  )}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      <div className="p-3">
        <button
          onClick={toggleSidebar}
          className="flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-[13px] text-[var(--color-ink-3)] hover:text-[var(--color-ink-0)] hover:bg-white/[0.04] transition-colors"
        >
          <ChevronsLeft size={16} className={cn("transition-transform duration-300", sidebarCollapsed && "rotate-180")} />
          {!sidebarCollapsed && "Collapse"}
        </button>
      </div>
    </aside>
  );
}
