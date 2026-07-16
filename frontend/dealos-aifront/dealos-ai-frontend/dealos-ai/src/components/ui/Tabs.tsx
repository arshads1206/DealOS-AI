import * as React from "react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
  count?: number;
}

export function Tabs({
  tabs,
  active,
  onChange,
}: {
  tabs: Tab[];
  active: string;
  onChange: (id: string) => void;
}) {
  return (
    <div className="flex items-center gap-1 border-b border-[var(--color-border-hairline)] overflow-x-auto no-scrollbar">
      {tabs.map((tab) => {
        const isActive = tab.id === active;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={cn(
              "relative flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors duration-200",
              isActive ? "text-[var(--color-ink-0)]" : "text-[var(--color-ink-3)] hover:text-[var(--color-ink-1)]"
            )}
          >
            {tab.icon}
            {tab.label}
            {typeof tab.count === "number" && (
              <span className="rounded-full bg-white/[0.06] px-1.5 py-0.5 text-[10px] font-mono text-[var(--color-ink-2)]">
                {tab.count}
              </span>
            )}
            {isActive && (
              <motion.div
                layoutId="tab-underline"
                className="absolute -bottom-px left-0 right-0 h-[2px] bg-gradient-to-r from-[var(--color-gold-300)] to-[var(--color-gold-600)]"
                transition={{ type: "spring", stiffness: 500, damping: 40 }}
              />
            )}
          </button>
        );
      })}
    </div>
  );
}
