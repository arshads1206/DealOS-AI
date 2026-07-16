import { initials } from "@/lib/utils";
import { cn } from "@/lib/utils";

export function Avatar({ name, size = 32, className }: { name: string; size?: number; className?: string }) {
  return (
    <div
      className={cn(
        "flex items-center justify-center rounded-full bg-gradient-to-br from-[var(--color-gold-300)] to-[var(--color-gold-700)] text-[#141008] font-mono font-semibold shrink-0",
        className
      )}
      style={{ width: size, height: size, fontSize: size * 0.36 }}
    >
      {initials(name)}
    </div>
  );
}
