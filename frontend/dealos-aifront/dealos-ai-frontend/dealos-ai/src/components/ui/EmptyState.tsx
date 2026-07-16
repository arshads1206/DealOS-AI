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
      {icon && <div className="text-[var(--color-gold-500)]/60 mb-1">{icon}</div>}
      <p className="font-display text-lg text-[var(--color-ink-0)]">{title}</p>
      {description && <p className="text-sm text-[var(--color-ink-3)] max-w-sm">{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
