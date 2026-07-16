// Mock domain data for DealOS AI. Replace with real API/service calls when the backend is wired up.

export type RiskSeverity = "low" | "medium" | "high" | "critical";
export type CompanyStatus = "active-dd" | "portfolio" | "watchlist" | "closed";

export interface FinancialPoint {
  period: string;
  revenue: number;
  ebitda: number;
  netIncome: number;
}

export interface Company {
  id: string;
  name: string;
  ticker: string;
  sector: string;
  geography: string;
  stage: CompanyStatus;
  dealValue: number;
  ownership: number;
  riskScore: number; // 0-100, higher = riskier
  irr: number;
  moic: number;
  lastActivity: string;
  description: string;
  analyst: string;
  history: FinancialPoint[];
}

export const companies: Company[] = [
  {
    id: "meridian-health",
    name: "Meridian Health Systems",
    ticker: "MHS",
    sector: "Healthcare Services",
    geography: "North America",
    stage: "active-dd",
    dealValue: 480_000_000,
    ownership: 62,
    riskScore: 41,
    irr: 24.6,
    moic: 2.4,
    lastActivity: "2h ago",
    analyst: "R. Nair",
    description:
      "Multi-site outpatient care platform with a roll-up thesis across the Southeast. Third add-on LOI in diligence.",
    history: [
      { period: "FY22", revenue: 210, ebitda: 38, netIncome: 19 },
      { period: "FY23", revenue: 256, ebitda: 51, netIncome: 27 },
      { period: "FY24", revenue: 305, ebitda: 66, netIncome: 34 },
      { period: "FY25", revenue: 361, ebitda: 84, netIncome: 45 },
      { period: "FY26E", revenue: 418, ebitda: 101, netIncome: 57 },
    ],
  },
  {
    id: "northwind-logistics",
    name: "Northwind Logistics",
    ticker: "NWL",
    sector: "Industrials & Transport",
    geography: "North America",
    stage: "portfolio",
    dealValue: 310_000_000,
    ownership: 78,
    riskScore: 58,
    irr: 14.1,
    moic: 1.6,
    lastActivity: "1d ago",
    analyst: "S. Kapoor",
    description:
      "Regional freight and last-mile network under margin pressure from fuel costs and driver wage inflation.",
    history: [
      { period: "FY22", revenue: 402, ebitda: 61, netIncome: 22 },
      { period: "FY23", revenue: 419, ebitda: 55, netIncome: 17 },
      { period: "FY24", revenue: 431, ebitda: 49, netIncome: 12 },
      { period: "FY25", revenue: 447, ebitda: 52, netIncome: 15 },
      { period: "FY26E", revenue: 468, ebitda: 58, netIncome: 19 },
    ],
  },
  {
    id: "vertex-semiconductors",
    name: "Vertex Semiconductor Labs",
    ticker: "VSL",
    sector: "Technology & Hardware",
    geography: "APAC",
    stage: "active-dd",
    dealValue: 920_000_000,
    ownership: 35,
    riskScore: 22,
    irr: 31.8,
    moic: 3.1,
    lastActivity: "4h ago",
    analyst: "A. Chen",
    description:
      "Fabless analog chip designer serving EV power management. Clean carve-out from a larger conglomerate.",
    history: [
      { period: "FY22", revenue: 188, ebitda: 44, netIncome: 30 },
      { period: "FY23", revenue: 241, ebitda: 63, netIncome: 41 },
      { period: "FY24", revenue: 318, ebitda: 92, netIncome: 61 },
      { period: "FY25", revenue: 402, ebitda: 124, netIncome: 84 },
      { period: "FY26E", revenue: 489, ebitda: 158, netIncome: 109 },
    ],
  },
  {
    id: "harborline-insurance",
    name: "Harborline Specialty Insurance",
    ticker: "HSI",
    sector: "Financial Services",
    geography: "Europe",
    stage: "watchlist",
    dealValue: 175_000_000,
    ownership: 0,
    riskScore: 66,
    irr: 0,
    moic: 0,
    lastActivity: "3d ago",
    analyst: "R. Nair",
    description:
      "Specialty E&S underwriter flagged for reserve adequacy concerns following restated FY24 loss triangles.",
    history: [
      { period: "FY22", revenue: 96, ebitda: 21, netIncome: 14 },
      { period: "FY23", revenue: 104, ebitda: 19, netIncome: 11 },
      { period: "FY24", revenue: 101, ebitda: 9, netIncome: 3 },
      { period: "FY25", revenue: 108, ebitda: 14, netIncome: 7 },
      { period: "FY26E", revenue: 116, ebitda: 18, netIncome: 10 },
    ],
  },
  {
    id: "solace-foods",
    name: "Solace Foods Group",
    ticker: "SFG",
    sector: "Consumer & Retail",
    geography: "North America",
    stage: "portfolio",
    dealValue: 260_000_000,
    ownership: 55,
    riskScore: 33,
    irr: 19.4,
    moic: 2.0,
    lastActivity: "6h ago",
    analyst: "M. Alvarez",
    description:
      "Branded better-for-you snacking platform, three tuck-in acquisitions completed since close.",
    history: [
      { period: "FY22", revenue: 140, ebitda: 24, netIncome: 12 },
      { period: "FY23", revenue: 172, ebitda: 33, netIncome: 18 },
      { period: "FY24", revenue: 205, ebitda: 41, netIncome: 23 },
      { period: "FY25", revenue: 239, ebitda: 51, netIncome: 29 },
      { period: "FY26E", revenue: 271, ebitda: 61, netIncome: 36 },
    ],
  },
  {
    id: "clearpath-energy",
    name: "Clearpath Renewable Energy",
    ticker: "CRE",
    sector: "Energy & Infrastructure",
    geography: "Europe",
    stage: "closed",
    dealValue: 540_000_000,
    ownership: 100,
    riskScore: 28,
    irr: 27.2,
    moic: 2.7,
    lastActivity: "2w ago",
    analyst: "A. Chen",
    description:
      "Utility-scale solar and storage developer. Exited via strategic sale to a European utility in Q1.",
    history: [
      { period: "FY21", revenue: 88, ebitda: 30, netIncome: 14 },
      { period: "FY22", revenue: 121, ebitda: 46, netIncome: 22 },
      { period: "FY23", revenue: 164, ebitda: 68, netIncome: 35 },
      { period: "FY24", revenue: 219, ebitda: 95, netIncome: 52 },
      { period: "FY25", revenue: 268, ebitda: 121, netIncome: 68 },
    ],
  },
];

export interface RiskItem {
  id: string;
  companyId: string;
  title: string;
  category: "Financial" | "Legal" | "Operational" | "Market" | "ESG" | "Governance";
  severity: RiskSeverity;
  summary: string;
  source: string;
  page: number;
  detected: string;
  status: "open" | "monitoring" | "resolved";
}

export const risks: RiskItem[] = [
  {
    id: "rk-001",
    companyId: "meridian-health",
    title: "Customer concentration in top-3 payors",
    category: "Financial",
    severity: "medium",
    summary:
      "58% of net revenue derives from three managed-care payors; one contract renews within 9 months with no renegotiated rate lock disclosed.",
    source: "FY25 10-K, Note 14",
    page: 87,
    detected: "Jul 11, 2026",
    status: "open",
  },
  {
    id: "rk-002",
    companyId: "meridian-health",
    title: "Pending state licensure review — Georgia facilities",
    category: "Legal",
    severity: "low",
    summary:
      "Routine licensure renewal flagged for two facilities; no history of adverse findings in prior cycles.",
    source: "Compliance Memo, June 2026",
    page: 3,
    detected: "Jul 9, 2026",
    status: "monitoring",
  },
  {
    id: "rk-003",
    companyId: "northwind-logistics",
    title: "Covenant headroom compressed to 0.3x",
    category: "Financial",
    severity: "critical",
    summary:
      "Leverage covenant headroom fell from 1.1x to 0.3x over two quarters as EBITDA declined on fuel cost pass-through lag.",
    source: "Q2 26 Lender Compliance Cert",
    page: 2,
    detected: "Jul 12, 2026",
    status: "open",
  },
  {
    id: "rk-004",
    companyId: "northwind-logistics",
    title: "Driver attrition trending above sector benchmark",
    category: "Operational",
    severity: "medium",
    summary:
      "Annualized driver attrition of 34% vs. sector median 26%, correlated with two service-level breach notices from key accounts.",
    source: "Ops Board Deck, June 2026",
    page: 11,
    detected: "Jul 6, 2026",
    status: "open",
  },
  {
    id: "rk-005",
    companyId: "harborline-insurance",
    title: "Reserve adequacy restatement",
    category: "Financial",
    severity: "critical",
    summary:
      "FY24 loss triangles restated upward by 340bps of adverse development in commercial casualty lines; actuarial opinion qualified.",
    source: "FY24 Restated Financials",
    page: 45,
    detected: "Jul 10, 2026",
    status: "open",
  },
  {
    id: "rk-006",
    companyId: "harborline-insurance",
    title: "Key-person dependency — Chief Underwriting Officer",
    category: "Governance",
    severity: "high",
    summary:
      "No successor identified for CUO who holds sign-off authority above $2M line size; 22-year tenure, no employment agreement on file.",
    source: "Management Interview Notes",
    page: 1,
    detected: "Jul 8, 2026",
    status: "monitoring",
  },
  {
    id: "rk-007",
    companyId: "vertex-semiconductors",
    title: "Single-fab dependency — TSMC allocation",
    category: "Operational",
    severity: "medium",
    summary:
      "95% of wafer volume sourced from a single foundry partner; no dual-sourcing agreement disclosed for the next 18 months.",
    source: "Supply Chain Diligence Report",
    page: 22,
    detected: "Jul 5, 2026",
    status: "monitoring",
  },
  {
    id: "rk-008",
    companyId: "solace-foods",
    title: "Co-packer contract auto-renewal pricing gap",
    category: "Operational",
    severity: "low",
    summary:
      "Primary co-packer agreement auto-renews at index-linked pricing roughly 4% above the last negotiated benchmark rate.",
    source: "Vendor Contract Abstract",
    page: 6,
    detected: "Jul 3, 2026",
    status: "resolved",
  },
];

export interface DocumentItem {
  id: string;
  companyId: string;
  name: string;
  type: "10-K" | "10-Q" | "Earnings Transcript" | "Investor Deck" | "Legal" | "News" | "Industry Report";
  uploaded: string;
  pages: number;
  size: string;
  status: "processed" | "processing" | "queued";
  confidence: number;
}

export const documents: DocumentItem[] = [
  { id: "doc-1", companyId: "meridian-health", name: "Meridian Health — FY25 10-K", type: "10-K", uploaded: "Jul 11, 2026", pages: 214, size: "8.4 MB", status: "processed", confidence: 98 },
  { id: "doc-2", companyId: "meridian-health", name: "Q2 FY26 Earnings Call Transcript", type: "Earnings Transcript", uploaded: "Jul 12, 2026", pages: 31, size: "410 KB", status: "processed", confidence: 96 },
  { id: "doc-3", companyId: "meridian-health", name: "Management Investor Presentation — June", type: "Investor Deck", uploaded: "Jul 9, 2026", pages: 48, size: "12.1 MB", status: "processed", confidence: 94 },
  { id: "doc-4", companyId: "meridian-health", name: "Georgia Licensure Compliance Memo", type: "Legal", uploaded: "Jul 9, 2026", pages: 6, size: "220 KB", status: "processing", confidence: 0 },
  { id: "doc-5", companyId: "northwind-logistics", name: "Q2 26 Lender Compliance Certificate", type: "Legal", uploaded: "Jul 12, 2026", pages: 9, size: "1.1 MB", status: "processed", confidence: 99 },
  { id: "doc-6", companyId: "northwind-logistics", name: "Northwind Logistics — 10-Q", type: "10-Q", uploaded: "Jul 8, 2026", pages: 82, size: "5.6 MB", status: "processed", confidence: 95 },
  { id: "doc-7", companyId: "northwind-logistics", name: "Operations Board Deck — June", type: "Investor Deck", uploaded: "Jul 6, 2026", pages: 27, size: "6.8 MB", status: "processed", confidence: 91 },
  { id: "doc-8", companyId: "vertex-semiconductors", name: "Supply Chain Diligence Report", type: "Industry Report", uploaded: "Jul 5, 2026", pages: 64, size: "9.9 MB", status: "processed", confidence: 93 },
  { id: "doc-9", companyId: "vertex-semiconductors", name: "Carve-out Separation Agreement (Draft)", type: "Legal", uploaded: "Jul 4, 2026", pages: 118, size: "3.2 MB", status: "queued", confidence: 0 },
  { id: "doc-10", companyId: "harborline-insurance", name: "FY24 Restated Financial Statements", type: "10-K", uploaded: "Jul 10, 2026", pages: 176, size: "7.1 MB", status: "processed", confidence: 97 },
];

export interface ActivityItem {
  id: string;
  companyId: string;
  actor: string;
  action: string;
  target: string;
  timestamp: string;
  kind: "upload" | "analysis" | "report" | "comment" | "risk";
}

export const activity: ActivityItem[] = [
  { id: "a1", companyId: "meridian-health", actor: "AI Analyst", action: "flagged a new risk in", target: "Payor concentration, Note 14", timestamp: "12 min ago", kind: "risk" },
  { id: "a2", companyId: "northwind-logistics", actor: "S. Kapoor", action: "generated a due diligence report for", target: "Northwind Logistics Q2 Review", timestamp: "48 min ago", kind: "report" },
  { id: "a3", companyId: "vertex-semiconductors", actor: "AI Analyst", action: "finished processing", target: "Supply Chain Diligence Report", timestamp: "2h ago", kind: "analysis" },
  { id: "a4", companyId: "meridian-health", actor: "R. Nair", action: "uploaded", target: "Q2 FY26 Earnings Call Transcript", timestamp: "3h ago", kind: "upload" },
  { id: "a5", companyId: "harborline-insurance", actor: "R. Nair", action: "commented on", target: "Reserve adequacy restatement", timestamp: "5h ago", kind: "comment" },
  { id: "a6", companyId: "solace-foods", actor: "M. Alvarez", action: "resolved risk", target: "Co-packer contract pricing gap", timestamp: "1d ago", kind: "risk" },
  { id: "a7", companyId: "northwind-logistics", actor: "AI Analyst", action: "flagged a critical risk in", target: "Covenant headroom compression", timestamp: "1d ago", kind: "risk" },
];

export interface ReportItem {
  id: string;
  companyId: string;
  title: string;
  type: "Due Diligence" | "Investment Memo" | "Quarterly Review" | "Risk Assessment";
  author: string;
  date: string;
  status: "draft" | "in-review" | "final";
  pages: number;
}

export const reports: ReportItem[] = [
  { id: "rp-1", companyId: "meridian-health", title: "Meridian Health — Initial Due Diligence Report", type: "Due Diligence", author: "AI Analyst + R. Nair", date: "Jul 12, 2026", status: "in-review", pages: 38 },
  { id: "rp-2", companyId: "northwind-logistics", title: "Northwind Logistics — Q2 2026 Portfolio Review", type: "Quarterly Review", author: "S. Kapoor", date: "Jul 12, 2026", status: "final", pages: 22 },
  { id: "rp-3", companyId: "vertex-semiconductors", title: "Vertex Semiconductor — Investment Committee Memo", type: "Investment Memo", author: "A. Chen", date: "Jul 10, 2026", status: "draft", pages: 44 },
  { id: "rp-4", companyId: "harborline-insurance", title: "Harborline — Reserve Risk Assessment", type: "Risk Assessment", author: "AI Analyst + R. Nair", date: "Jul 11, 2026", status: "final", pages: 16 },
  { id: "rp-5", companyId: "solace-foods", title: "Solace Foods — Q2 2026 Portfolio Review", type: "Quarterly Review", author: "M. Alvarez", date: "Jul 9, 2026", status: "final", pages: 19 },
];

export interface TimelineEvent {
  id: string;
  companyId: string;
  title: string;
  description: string;
  date: string;
  kind: "milestone" | "document" | "meeting" | "risk" | "financial";
}

export const timeline: TimelineEvent[] = [
  { id: "t1", companyId: "meridian-health", title: "Initial IC screen approved", description: "Investment committee approved advancing to confirmatory diligence.", date: "May 2, 2026", kind: "milestone" },
  { id: "t2", companyId: "meridian-health", title: "Management presentation", description: "First management meeting; CEO and CFO walked through FY25 performance.", date: "May 18, 2026", kind: "meeting" },
  { id: "t3", companyId: "meridian-health", title: "Data room opened", description: "Full data room access granted; 40+ documents ingested since.", date: "Jun 2, 2026", kind: "document" },
  { id: "t4", companyId: "meridian-health", title: "Q2 earnings call", description: "Beat on revenue, in-line on EBITDA margin; guidance reiterated.", date: "Jul 12, 2026", kind: "financial" },
  { id: "t5", companyId: "meridian-health", title: "Payor concentration risk flagged", description: "AI Analyst surfaced concentration risk from Note 14 of the 10-K.", date: "Jul 12, 2026", kind: "risk" },
];

export const portfolioSummary = {
  totalAUM: 4_820_000_000,
  activeDeals: companies.filter((c) => c.stage === "active-dd").length,
  portfolioCompanies: companies.filter((c) => c.stage === "portfolio").length,
  avgIRR: 21.3,
  avgMOIC: 2.2,
  documentsProcessed: 1842,
  openRisks: risks.filter((r) => r.status === "open").length,
};

export const riskByCategory = [
  { category: "Financial", low: 2, medium: 3, high: 1, critical: 2 },
  { category: "Legal", low: 3, medium: 1, high: 0, critical: 0 },
  { category: "Operational", low: 1, medium: 2, high: 0, critical: 0 },
  { category: "Governance", low: 0, medium: 1, high: 1, critical: 0 },
  { category: "Market", low: 2, medium: 1, high: 0, critical: 0 },
  { category: "ESG", low: 1, medium: 0, high: 0, critical: 0 },
];

export const kpiTrend = [
  { period: "Feb", value: 3.9 },
  { period: "Mar", value: 4.1 },
  { period: "Apr", value: 4.2 },
  { period: "May", value: 4.4 },
  { period: "Jun", value: 4.6 },
  { period: "Jul", value: 4.82 },
];

export function getCompany(id: string) {
  return companies.find((c) => c.id === id);
}
export function getDocuments(companyId: string) {
  return documents.filter((d) => d.companyId === companyId);
}
export function getRisks(companyId: string) {
  return risks.filter((r) => r.companyId === companyId);
}
export function getActivity(companyId: string) {
  return activity.filter((a) => a.companyId === companyId);
}
export function getReports(companyId: string) {
  return reports.filter((r) => r.companyId === companyId);
}
export function getTimeline(companyId: string) {
  return timeline.filter((t) => t.companyId === companyId);
}
