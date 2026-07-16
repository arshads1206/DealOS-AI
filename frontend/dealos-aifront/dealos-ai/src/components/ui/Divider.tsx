import { cn } from "@/lib/utils";

export function Divider({ className }: { className?: string }) {
  return <div className={cn("ledger-rule w-full", className)} />;
}
