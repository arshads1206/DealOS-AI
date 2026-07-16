import type { ReactNode } from "react";

export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 px-6 text-center">
      {icon && (
        <div className="mb-1 flex h-16 w-16 items-center justify-center rounded-2xl glass-panel text-[var(--color-gold-400)] shadow-[0_0_24px_-8px_rgba(201,162,39,0.4)]">
          {icon}
        </div>
      )}
      <p className="font-display text-lg text-[var(--color-ink-0)]">{title}</p>
      {description && <p className="text-sm text-[var(--color-ink-3)] max-w-sm">{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
