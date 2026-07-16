import { useState } from "react";
import { PageHeader, PageContainer, Reveal } from "@/components/layout/PageHeader";
import { GlassCard } from "@/components/ui/GlassCard";
import { Tabs } from "@/components/ui/Tabs";
import { Button } from "@/components/ui/Button";
import { Divider } from "@/components/ui/Divider";
import { User, Bell, Shield, Palette } from "lucide-react";

const sections = [
  { id: "account", label: "Account", icon: <User size={14} /> },
  { id: "notifications", label: "Notifications", icon: <Bell size={14} /> },
  { id: "security", label: "Security", icon: <Shield size={14} /> },
  { id: "appearance", label: "Appearance", icon: <Palette size={14} /> },
];

export function SettingsPage() {
  const [active, setActive] = useState("account");

  return (
    <PageContainer>
      <PageHeader eyebrow="System" title="Settings" description="Manage your account, notification preferences, and workspace security." />

      <div className="px-8">
        <Tabs tabs={sections} active={active} onChange={setActive} />

        <div className="mt-6 max-w-2xl">
          {active === "account" && (
            <Reveal>
              <GlassCard className="p-6 space-y-5" raised>
                <Field label="Full name" defaultValue="Ananya Rao" />
                <Field label="Work email" defaultValue="ananya.rao@dealos.ai" />
                <Field label="Role" defaultValue="Vice President, Private Equity" />
                <Field label="Team" defaultValue="Healthcare & Industrials" />
                <Divider />
                <div className="flex justify-end">
                  <Button variant="primary">Save changes</Button>
                </div>
              </GlassCard>
            </Reveal>
          )}
          {active === "notifications" && (
            <Reveal>
              <GlassCard className="p-6 space-y-4" raised>
                <Toggle label="Critical risk alerts" description="Get notified immediately when the AI Analyst flags a critical risk." defaultChecked />
                <Toggle label="Document processing complete" description="Notify me when uploaded documents finish parsing." defaultChecked />
                <Toggle label="Report ready for review" description="Notify me when a due diligence report is ready to review." defaultChecked />
                <Toggle label="Weekly portfolio digest" description="A summary of activity across all workspaces, every Monday." />
              </GlassCard>
            </Reveal>
          )}
          {active === "security" && (
            <Reveal>
              <GlassCard className="p-6 space-y-5" raised>
                <Field label="Password" defaultValue="••••••••••••" type="password" />
                <Toggle label="Two-factor authentication" description="Require a verification code in addition to your password." defaultChecked />
                <Toggle label="Single sign-on (SSO)" description="Enterprise SSO managed by your organization's identity provider." defaultChecked />
                <Divider />
                <div className="flex justify-end">
                  <Button variant="primary">Update security settings</Button>
                </div>
              </GlassCard>
            </Reveal>
          )}
          {active === "appearance" && (
            <Reveal>
              <GlassCard className="p-6" raised>
                <p className="text-sm text-[var(--color-ink-2)] mb-4">DealOS AI is designed for extended focus sessions in low-light environments.</p>
                <div className="flex gap-3">
                  <div className="flex-1 rounded-xl border-2 border-[var(--color-gold-500)]/50 bg-[var(--color-bg)] p-4">
                    <div className="h-16 rounded-lg bg-gradient-to-br from-[var(--color-surface)] to-[var(--color-bg)] border border-[var(--color-border)] mb-2" />
                    <p className="text-xs text-[var(--color-ink-0)] font-medium">Matte Black (default)</p>
                  </div>
                  <div className="flex-1 rounded-xl border border-[var(--color-border-hairline)] p-4 opacity-40">
                    <div className="h-16 rounded-lg bg-gradient-to-br from-neutral-200 to-neutral-100 mb-2" />
                    <p className="text-xs text-[var(--color-ink-3)]">Light mode (coming soon)</p>
                  </div>
                </div>
              </GlassCard>
            </Reveal>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

function Field({ label, defaultValue, type = "text" }: { label: string; defaultValue: string; type?: string }) {
  return (
    <div>
      <label className="text-xs text-[var(--color-ink-3)] mb-1.5 block">{label}</label>
      <input
        type={type}
        defaultValue={defaultValue}
        className="w-full rounded-lg border border-[var(--color-border-hairline)] bg-white/[0.02] px-3 py-2.5 text-sm text-[var(--color-ink-0)] focus:border-[var(--color-border-strong)] outline-none transition-colors"
      />
    </div>
  );
}

function Toggle({ label, description, defaultChecked = false }: { label: string; description: string; defaultChecked?: boolean }) {
  const [checked, setChecked] = useState(defaultChecked);
  return (
    <div className="flex items-center justify-between gap-4">
      <div>
        <p className="text-sm text-[var(--color-ink-0)] font-medium">{label}</p>
        <p className="text-xs text-[var(--color-ink-3)] mt-0.5">{description}</p>
      </div>
      <button
        onClick={() => setChecked((c) => !c)}
        className={`relative h-6 w-11 shrink-0 rounded-full transition-colors ${checked ? "bg-[var(--color-gold-500)]/70" : "bg-white/10"}`}
      >
        <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow-md transition-transform ${checked ? "translate-x-5" : "translate-x-0.5"}`} />
      </button>
    </div>
  );
}
