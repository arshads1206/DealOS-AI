import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";

export interface ListRowProps {
  icon: ReactNode;
  title: ReactNode;
  subtitle?: ReactNode;
  href?: string;
  onClick?: () => void;
}

export function ListRow({ icon, title, subtitle, href, onClick }: ListRowProps) {
  const content = (
    <>
      <div className="mt-0.5 shrink-0 flex items-center justify-center">{icon}</div>
      <div className="min-w-0 flex-1">
        <div className="text-[13px] text-[var(--color-ink-1)] leading-snug truncate">{title}</div>
        {subtitle && (
          <div className="text-[11px] text-[var(--color-ink-4)] font-mono mt-0.5 truncate">{subtitle}</div>
        )}
      </div>
    </>
  );

  const containerClasses =
    "flex items-start gap-3 rounded-lg p-2 -mx-2 hover:bg-white/[0.03] transition-colors outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-gold-500)]";

  if (href) {
    return (
      <Link to={href} className="group block focus:outline-none">
        <motion.div
          whileHover={{ x: 2 }}
          transition={{ duration: 0.2 }}
          className={containerClasses}
        >
          {content}
        </motion.div>
      </Link>
    );
  }

  return (
    <motion.div
      whileHover={{ x: onClick ? 2 : 0 }}
      transition={{ duration: 0.2 }}
      className={containerClasses}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
    >
      {content}
    </motion.div>
  );
}
