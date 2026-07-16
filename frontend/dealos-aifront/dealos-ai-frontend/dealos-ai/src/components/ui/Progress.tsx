import { cn } from "@/lib/utils";

export function Progress({ value, tone = "gold", className }: { value: number; tone?: "gold" | "emerald" | "amber" | "crimson"; className?: string }) {
  const colors: Record<string, string> = {
    gold: "from-[var(--color-gold-300)] to-[var(--color-gold-600)]",
    emerald: "from-emerald-300 to-[var(--color-emerald)]",
    amber: "from-amber-200 to-[var(--color-amber)]",
    crimson: "from-red-300 to-[var(--color-crimson)]",
  };
  return (
    <div className={cn("h-1.5 w-full rounded-full bg-white/[0.06] overflow-hidden", className)}>
      <div
        className={cn("h-full rounded-full bg-gradient-to-r transition-all duration-700 ease-out", colors[tone])}
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  );
}
