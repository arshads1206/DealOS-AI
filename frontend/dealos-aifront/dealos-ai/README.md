# DealOS AI — Investment Intelligence Operating System

A frontend build for an enterprise investment due-diligence platform. Matte black, glass, and champagne gold — built for analysts who live in this tool 8–12 hours a day.

## Honest scope note

The brief called for 20 pages built to executive-demo quality plus a full motion/branding system. That's a multi-week build for a real team. Rather than spread the effort thin across everything, this build goes deep on the surfaces that matter most and are representative of the whole system, and keeps the rest functional but lighter. Specifically:

**Built to full depth** (design system, motion, branding, real interaction):
- Dashboard (portfolio KPIs, AUM trend, risk heatmap, AI insights, activity)
- Companies list (filterable, searchable)
- Company Workspace — all 8 tabs: Overview, Documents, Financials, Risks, **AI Analyst**, Reports, Timeline, Activity
- AI Analyst chat — the flagship surface: streaming responses, confidence rings, source citations, reasoning trace, evidence panel, suggested/follow-up questions
- Authentication

**Built functional, lighter polish** (same design system, less bespoke interaction):
- Global Search, standalone Document Library, standalone Investment Reports, standalone Financial Analysis, standalone Risk Analysis, Settings, Profile, Notifications, Admin

Everything routes, renders, and uses the same design tokens — nothing is a dead link — but if you tell me which of the lighter pages matter most for your next demo (e.g. for BNY, or for HackMIT judges), I'll bring that one up to flagship quality next.

## Design system, briefly

- **Palette**: matte black/graphite base, champagne gold accent (`#C9A227` family), emerald/amber/crimson/ice-blue for success/warning/risk/info.
- **Type**: Fraunces (display, luxury/editorial gravitas) + IBM Plex Sans (UI, engineered precision) + IBM Plex Mono (all numbers/data — tabular-nums throughout). This pairing was chosen specifically to avoid the generic "Inter everywhere" AI-dashboard look while staying legible for dense financial data.
- **Signature motif**: a thin gold "ledger rule" divider and a recurring confidence-ring component (used for AI answer confidence, risk scores) — both tie back to the idea of an audited, evidenced platform rather than decoration for its own sake.
- **Glass**: every panel uses backdrop-blur with a gold-tinted border and top-edge highlight; interactive cards lift slightly on hover.
- **Motion**: Framer Motion for page/section reveals, staggered card entrances, animated tab underline, count-up numbers, and a typing-dots state in the AI Analyst — restrained on purpose, nothing spins or bounces gratuitously.

## Tech stack

React 19 · TypeScript · Vite · Tailwind CSS v4 · Framer Motion · React Router · TanStack Query (wired, ready for real data fetching) · Zustand · Recharts · Lucide Icons · React Hook Form + Zod (installed, ready for form validation as real forms are added)

All data is mocked in `src/lib/mockData.ts` and `src/lib/aiAnalyst.ts` — no backend calls are made. Replace these with real API/service calls when the backend is ready; the shapes are already typed.

## Running it

```bash
npm install
npm run dev
```

Then open the printed local URL (usually `http://localhost:5173`).

To type-check and build for production:

```bash
npm run build
```

## Project structure

```
src/
  components/
    ui/        — design system primitives (Button, GlassCard, Badge, Tabs, ConfidenceRing, ...)
    layout/    — AppShell, Sidebar, Topbar, PageHeader
    charts/    — Recharts wrappers styled to the brand
  features/
    dashboard/, companies/, workspace/ (+ tabs/), search/, documents/,
    reports/, financial-analysis/, risk-analysis/, settings/, profile/,
    notifications/, admin/, auth/
  lib/         — mock data, formatting helpers, cn() utility
  store/       — Zustand app-level UI state
```

## Notes on what's mocked vs. real

- AI Analyst answers are generated from a small template engine over the mock data (`generateResponse` in `src/lib/aiAnalyst.ts`) — it's convincing for a demo but isn't calling a real model. When you wire up a real backend, this is the one function to replace.
- Document "processing" status and confidence scores are static, not live.
- Auth is a UI shell with no real session handling.
