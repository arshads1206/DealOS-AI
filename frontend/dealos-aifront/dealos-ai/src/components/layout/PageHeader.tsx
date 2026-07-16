import type { ReactNode } from "react";
import { motion } from "framer-motion";

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="flex flex-col gap-4 px-8 pt-8 pb-6 md:flex-row md:items-end md:justify-between"
    >
      <div>
        {eyebrow && (
          <p className="mb-1.5 text-[11px] font-medium uppercase tracking-[0.16em] text-[var(--color-gold-500)]">
            {eyebrow}
          </p>
        )}
        <h1 className="font-display text-[28px] leading-tight text-[var(--color-ink-0)]">{title}</h1>
        {description && <p className="mt-1.5 max-w-2xl text-sm text-[var(--color-ink-3)]">{description}</p>}
      </div>
      {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
    </motion.div>
  );
}

export function PageContainer({ children }: { children: ReactNode }) {
  return <div className="mx-auto max-w-[1400px] pb-16">{children}</div>;
}

export function Reveal({ children, delay = 0 }: { children: ReactNode; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8, scale: 0.99 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ once: true, margin: "-20px" }}
      transition={{ duration: 0.4, delay, ease: [0.25, 0.1, 0.25, 1] }}
    >
      {children}
    </motion.div>
  );
}
