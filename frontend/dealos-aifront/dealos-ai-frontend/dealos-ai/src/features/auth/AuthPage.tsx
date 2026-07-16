import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/Button";
import { GlassCard } from "@/components/ui/GlassCard";
import { Lock, Mail, ArrowRight } from "lucide-react";

export function AuthPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => navigate("/"), 700);
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[var(--color-bg)] px-4">
      <div className="pointer-events-none fixed inset-0 brand-grid opacity-40" />
      <div className="pointer-events-none fixed top-1/4 left-1/4 h-[560px] w-[560px] -translate-x-1/2 rounded-full bg-[var(--color-gold-500)]/[0.07] blur-[160px]" />
      <div className="pointer-events-none fixed bottom-0 right-1/4 h-[420px] w-[420px] rounded-full bg-[var(--color-gold-700)]/[0.08] blur-[140px]" />

      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }} className="relative w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <svg viewBox="0 0 32 32" className="h-11 w-11 mb-4">
            <circle cx="16" cy="16" r="14.5" fill="none" stroke="url(#auth-ring)" strokeWidth="1.4" />
            <text x="16" y="21" textAnchor="middle" fontFamily="Fraunces, serif" fontSize="15" fill="var(--color-gold-200)">
              D
            </text>
            <defs>
              <linearGradient id="auth-ring" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#E3C46B" />
                <stop offset="100%" stopColor="#8B6B2E" />
              </linearGradient>
            </defs>
          </svg>
          <p className="font-display text-2xl text-[var(--color-ink-0)]">DealOS AI</p>
          <p className="text-xs uppercase tracking-[0.16em] text-[var(--color-ink-3)] mt-1">Investment Intelligence Operating System</p>
        </div>

        <GlassCard className="p-8" raised>
          <p className="font-display text-lg text-[var(--color-ink-0)] mb-1">Sign in to your workspace</p>
          <p className="text-sm text-[var(--color-ink-3)] mb-6">Enterprise SSO available — contact your administrator.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-xs text-[var(--color-ink-3)] mb-1.5 block">Work email</label>
              <div className="flex items-center gap-2 rounded-lg border border-[var(--color-border-hairline)] bg-white/[0.02] px-3 py-2.5 focus-within:border-[var(--color-border-strong)] transition-colors">
                <Mail size={14} className="text-[var(--color-ink-4)]" />
                <input
                  type="email"
                  required
                  defaultValue="ananya.rao@dealos.ai"
                  className="flex-1 bg-transparent text-sm text-[var(--color-ink-0)] outline-none"
                />
              </div>
            </div>
            <div>
              <label className="text-xs text-[var(--color-ink-3)] mb-1.5 block">Password</label>
              <div className="flex items-center gap-2 rounded-lg border border-[var(--color-border-hairline)] bg-white/[0.02] px-3 py-2.5 focus-within:border-[var(--color-border-strong)] transition-colors">
                <Lock size={14} className="text-[var(--color-ink-4)]" />
                <input type="password" required defaultValue="••••••••••••" className="flex-1 bg-transparent text-sm text-[var(--color-ink-0)] outline-none" />
              </div>
            </div>
            <Button type="submit" variant="primary" size="lg" className="w-full justify-center" disabled={loading}>
              {loading ? "Verifying…" : "Continue"} {!loading && <ArrowRight size={15} />}
            </Button>
          </form>
        </GlassCard>
        <p className="text-center text-[11px] text-[var(--color-ink-4)] mt-6">
          Protected by enterprise-grade encryption · SOC 2 Type II compliant
        </p>
      </motion.div>
    </div>
  );
}
