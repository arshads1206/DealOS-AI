export interface Citation {
  id: string;
  doc: string;
  page: number;
  snippet: string;
}

export interface ReasoningStep {
  label: string;
  detail: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  confidence?: number;
  citations?: Citation[];
  reasoning?: ReasoningStep[];
  followUps?: string[];
}

export const suggestedQuestions: Record<string, string[]> = {
  "meridian-health": [
    "What is the payor concentration risk exposure?",
    "Summarize EBITDA margin trend over the last 3 years",
    "Are there any related-party transactions disclosed?",
    "Compare growth vs. sector benchmarks",
  ],
  "northwind-logistics": [
    "How much covenant headroom remains?",
    "What's driving the EBITDA decline this year?",
    "Summarize driver attrition trends",
    "What are the refinancing options if the covenant is breached?",
  ],
};

import { getCompany, getDocuments, getRisks } from "./mockData";

let counter = 1000;
function nextId() {
  counter += 1;
  return `gen-${counter}`;
}

export function generateResponse(companyId: string, question: string): ChatMessage {
  const company = getCompany(companyId);
  const docs = getDocuments(companyId);
  const companyRisks = getRisks(companyId);
  const lower = question.toLowerCase();

  const doc = docs[0];
  const risk = companyRisks.find((r) => lower.includes(r.category.toLowerCase())) ?? companyRisks[0];
  const latest = company?.history[company.history.length - 1];
  const prior = company?.history[company.history.length - 2];

  let content = "";
  const citations: Citation[] = [];
  const reasoning: ReasoningStep[] = [
    { label: "Parsed question", detail: "Identified key entities and intent from the query." },
    { label: "Searched workspace", detail: `Scanned ${docs.length} processed documents for relevant passages.` },
  ];

  if ((lower.includes("revenue") || lower.includes("financ") || lower.includes("ebitda") || lower.includes("margin")) && latest && prior) {
    const growth = (((latest.revenue - prior.revenue) / prior.revenue) * 100).toFixed(1);
    content = `${company?.name} reported ${latest.period} revenue of $${latest.revenue}M, up ${growth}% year over year, with EBITDA of $${latest.ebitda}M implying a ${((latest.ebitda / latest.revenue) * 100).toFixed(1)}% margin. Net income landed at $${latest.netIncome}M.`;
    citations.push({ id: nextId(), doc: doc?.name ?? "Financial Statements", page: 42, snippet: "Consolidated financial results for the period reflect continued top-line growth..." });
    reasoning.push({ label: "Extracted financial tables", detail: "Pulled structured revenue, EBITDA, and net income figures from filed statements." });
  } else if (lower.includes("risk") || lower.includes("concern") || lower.includes("exposure")) {
    content = risk
      ? `The most material open item is "${risk.title}" (${risk.severity} severity). ${risk.summary}`
      : `No material open risks are currently flagged for ${company?.name}.`;
    if (risk) citations.push({ id: nextId(), doc: risk.source, page: risk.page, snippet: risk.summary });
    reasoning.push({ label: "Ranked by severity", detail: "Sorted open risk register by severity and recency of detection." });
  } else {
    content = `Based on the ${docs.length} documents processed for ${company?.name}, I don't have a high-confidence answer to that yet — but I can pull the relevant section if you point me to a specific filing, or I can run a broader search across the data room.`;
    if (doc) citations.push({ id: nextId(), doc: doc.name, page: 1, snippet: "Document processed and indexed for retrieval." });
  }

  return {
    id: nextId(),
    role: "assistant",
    content,
    confidence: citations.length > 0 ? 78 + Math.floor(Math.random() * 15) : 52,
    citations,
    reasoning,
    followUps: [
      "Show me the source document",
      "How does this compare to sector peers?",
    ],
  };
}

export const conversationSeed: Record<string, ChatMessage[]> = {
  "meridian-health": [
    {
      id: "m1",
      role: "user",
      content: "What is our exposure to payor concentration, and how urgent is it?",
    },
    {
      id: "m2",
      role: "assistant",
      content:
        "Meridian derives 58% of net revenue from three managed-care payors. The largest single payor contract (≈24% of revenue) renews in April 2027 — inside the typical 18-month diligence-to-close window for a platform of this size. No rate lock or minimum-volume guarantee is disclosed in the current agreement, which is the main source of downside risk rather than the concentration itself.",
      confidence: 87,
      citations: [
        { id: "c1", doc: "Meridian Health — FY25 10-K", page: 87, snippet: "Three payors accounted for approximately 58% of net patient service revenue in fiscal 2025..." },
        { id: "c2", doc: "Q2 FY26 Earnings Call Transcript", page: 12, snippet: "...renewal discussions with our largest partner are underway and we expect to have clarity by year end..." },
      ],
      reasoning: [
        { label: "Scanned revenue disclosures", detail: "Cross-referenced Note 14 payor mix against segment revenue tables." },
        { label: "Checked contract terms", detail: "Searched legal data room for rate-lock or MFN clauses — none found." },
        { label: "Checked management commentary", detail: "Matched against Q2 earnings call transcript for forward guidance." },
      ],
      followUps: [
        "What would a 200bps rate cut from this payor do to EBITDA?",
        "Has management discussed diversification plans?",
      ],
    },
  ],
  "northwind-logistics": [
    {
      id: "n1",
      role: "user",
      content: "How much covenant headroom is left, and what happens if we breach?",
    },
    {
      id: "n2",
      role: "assistant",
      content:
        "Headroom on the senior leverage covenant compressed from 1.1x to 0.3x over the last two quarters, driven by an EBITDA decline tied to a fuel cost pass-through lag. At the current trajectory, a breach is plausible within one to two quarters absent intervention. The credit agreement includes a standard 30-day cure period and an equity cure right, capped at two uses over the facility term.",
      confidence: 82,
      citations: [
        { id: "c3", doc: "Q2 26 Lender Compliance Certificate", page: 2, snippet: "Leverage ratio calculated at 4.7x against a maximum permitted ratio of 5.0x..." },
        { id: "c4", doc: "Northwind Logistics — 10-Q", page: 34, snippet: "Fuel surcharge recovery lags actual cost increases by approximately one billing cycle..." },
      ],
      reasoning: [
        { label: "Pulled compliance certificates", detail: "Compared last two quarters of leverage ratio calculations." },
        { label: "Traced EBITDA decline", detail: "Attributed margin compression to fuel surcharge timing mismatch." },
        { label: "Reviewed credit agreement", detail: "Located cure provisions in Section 8.3 of the facility agreement." },
      ],
      followUps: [
        "What's the equity cure amount required to restore compliance?",
        "Model EBITDA sensitivity to a 5% fuel cost increase",
      ],
    },
  ],
};
