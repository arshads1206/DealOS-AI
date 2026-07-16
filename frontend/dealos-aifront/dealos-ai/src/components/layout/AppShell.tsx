import { Outlet, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export function AppShell() {
  const location = useLocation();
  // Key by the top 2 path segments only (e.g. "/companies/meridian-health") so that
  // switching tabs inside a workspace (a 3rd segment) doesn't retrigger a full-page
  // transition — only real page navigations do.
  const pageKey = location.pathname.split("/").slice(0, 3).join("/");

  return (
    <div className="relative flex h-screen w-full overflow-hidden bg-[var(--color-bg)]">
      {/* Ambient background */}
      <div className="pointer-events-none fixed inset-0 brand-grid opacity-40" />
      <div className="pointer-events-none fixed -top-40 -left-40 h-[520px] w-[520px] rounded-full bg-[var(--color-gold-500)]/[0.05] blur-[140px] animate-drift" />
      <div
        className="pointer-events-none fixed top-1/3 -right-40 h-[480px] w-[480px] rounded-full bg-[var(--color-gold-700)]/[0.06] blur-[160px] animate-drift"
        style={{ animationDelay: "-11s" }}
      />

      <Sidebar />
      <div className="relative flex min-w-0 flex-1 flex-col">
        <Topbar />
        <main className="flex-1 overflow-y-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={pageKey}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
