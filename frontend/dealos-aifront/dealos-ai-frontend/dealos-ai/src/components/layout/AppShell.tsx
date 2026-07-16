import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export function AppShell() {
  return (
    <div className="relative flex h-screen w-full overflow-hidden bg-[var(--color-bg)]">
      {/* Ambient background */}
      <div className="pointer-events-none fixed inset-0 brand-grid opacity-40" />
      <div className="pointer-events-none fixed -top-40 -left-40 h-[520px] w-[520px] rounded-full bg-[var(--color-gold-500)]/[0.05] blur-[140px]" />
      <div className="pointer-events-none fixed top-1/3 -right-40 h-[480px] w-[480px] rounded-full bg-[var(--color-gold-700)]/[0.06] blur-[160px]" />

      <Sidebar />
      <div className="relative flex min-w-0 flex-1 flex-col">
        <Topbar />
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
