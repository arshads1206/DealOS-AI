import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { GlassCard } from "@/components/ui/GlassCard";
import { Avatar } from "@/components/ui/Avatar";
import { ConfidenceRing } from "@/components/ui/ConfidenceRing";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { conversationSeed, suggestedQuestions, generateResponse, type ChatMessage } from "@/lib/aiAnalyst";
import { getCompany, getDocuments } from "@/lib/mockData";
import { 
  Bot, Send, FileText, Sparkles, MessageSquarePlus, ChevronRight, ChevronDown, ChevronUp,
  History, Copy, RefreshCw, Download, FileJson, CheckCircle2, Circle, Loader2, Search, Zap, Clock, PanelLeft
} from "lucide-react";
import { cn } from "@/lib/utils";

const threadHistory = {
  today: ["This conversation", "Payor mix deep dive"],
  yesterday: ["Q1 diligence questions", "Covenant scenario modeling"],
  earlier: ["Initial screening overview", "Management team background"]
};

export function AIAnalystTab() {
  const { id } = useParams();
  const company = getCompany(id!);
  const documents = getDocuments(id!);
  
  const [messages, setMessages] = useState<ChatMessage[]>(conversationSeed[id!] ?? []);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [expandedEvidence, setExpandedEvidence] = useState<Record<string, boolean>>({});
  
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isThinking]);

  // Use the latest AI message as the context for the sidebar
  const latestAiMessage = [...messages].reverse().find(m => m.role === "assistant");
  
  const questions = suggestedQuestions[id!] ?? [
    "Summarize the key financial trends",
    "What are the top risks in this workspace?",
    "Generate an investment memo",
    "Compare competitors"
  ];

  function send(text: string) {
    if (!text.trim() || !id || isThinking) return;
    const userMsg: ChatMessage = { id: `u-${Date.now()}`, role: "user", content: text };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setIsThinking(true);
    
    // Process response asynchronously to allow UI to render Skeleton
    setTimeout(() => {
      const response = generateResponse(id, text);
      setMessages((m) => [...m, response]);
      setIsThinking(false);
    }, 1500);
  }

  const toggleEvidence = (citationId: string) => {
    setExpandedEvidence(prev => ({ ...prev, [citationId]: !prev[citationId] }));
  };

  return (
    <div className="relative h-[calc(100vh-160px)] min-h-[600px] flex overflow-hidden">
      
      {/* Collapsible History Drawer */}
      <AnimatePresence>
        {historyOpen && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 240, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: "easeInOut" }}
            className="h-full border-r border-[var(--color-border-hairline)] bg-[var(--color-surface-1)] shrink-0 overflow-y-auto"
          >
            <div className="p-4 w-[240px]">
              <Button variant="secondary" size="sm" className="w-full justify-center mb-6" onClick={() => { setMessages([]); setHistoryOpen(false); }}>
                <MessageSquarePlus size={14} /> New thread
              </Button>
              
              <div className="space-y-6">
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-[var(--color-ink-4)] font-medium px-2 mb-2">Today</p>
                  <div className="space-y-0.5">
                    {threadHistory.today.map((t, i) => (
                      <button key={t} className={cn("w-full text-left rounded-md px-2.5 py-1.5 text-xs truncate transition-colors", i === 0 ? "bg-[var(--color-gold-500)]/[0.08] text-[var(--color-gold-300)]" : "text-[var(--color-ink-2)] hover:bg-white/[0.04] hover:text-[var(--color-ink-0)]")}>{t}</button>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-[var(--color-ink-4)] font-medium px-2 mb-2">Yesterday</p>
                  <div className="space-y-0.5">
                    {threadHistory.yesterday.map(t => (
                      <button key={t} className="w-full text-left rounded-md px-2.5 py-1.5 text-xs text-[var(--color-ink-2)] hover:bg-white/[0.04] hover:text-[var(--color-ink-0)] truncate transition-colors">{t}</button>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-[var(--color-ink-4)] font-medium px-2 mb-2">Earlier</p>
                  <div className="space-y-0.5">
                    {threadHistory.earlier.map(t => (
                      <button key={t} className="w-full text-left rounded-md px-2.5 py-1.5 text-xs text-[var(--color-ink-2)] hover:bg-white/[0.04] hover:text-[var(--color-ink-0)] truncate transition-colors">{t}</button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Split Layout */}
      <div className="flex-1 grid grid-cols-1 xl:grid-cols-[1fr_360px] gap-6">
        
        {/* LEFT PANE: Conversation (70%) */}
        <div className="flex flex-col h-full overflow-hidden">
          
          <div className="flex items-center px-4 py-3 border-b border-[var(--color-border-hairline)] shrink-0">
            <button 
              onClick={() => setHistoryOpen(!historyOpen)}
              className="flex items-center gap-2 text-sm text-[var(--color-ink-3)] hover:text-[var(--color-ink-1)] transition-colors focus:outline-none"
            >
              <PanelLeft size={16} /> {historyOpen ? "Hide History" : "Show History"}
            </button>
          </div>

          <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
            
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center max-w-lg mx-auto">
                <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-[var(--color-gold-300)] to-[var(--color-gold-600)] flex items-center justify-center mb-6 shadow-[0_0_40px_rgba(201,162,39,0.15)]">
                  <Bot size={24} className="text-[#141008]" />
                </div>
                <h2 className="font-display text-2xl text-[var(--color-ink-0)] mb-3">AI Analyst for {company?.name}</h2>
                <p className="text-sm text-[var(--color-ink-3)] leading-relaxed mb-10">
                  I can analyze {documents.length} ingested documents, extract financial metrics, detect risks, and generate comprehensive investment memos. Every response is strictly grounded in the workspace evidence.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left">
                  {questions.map((q, i) => (
                    <button
                      key={q}
                      onClick={() => send(q)}
                      className="group flex flex-col gap-2 p-4 rounded-xl border border-[var(--color-border-hairline)] bg-white/[0.01] hover:bg-white/[0.03] hover:border-[var(--color-gold-500)]/40 transition-all text-left"
                    >
                      <Sparkles size={14} className="text-[var(--color-gold-500)]" />
                      <span className="text-sm font-medium text-[var(--color-ink-1)] group-hover:text-[var(--color-gold-300)]">{q}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((m, index) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={cn("flex gap-4 max-w-3xl", m.role === "user" ? "ml-auto flex-row-reverse" : "mr-auto")}
              >
                {m.role === "assistant" ? (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-[var(--color-gold-300)] to-[var(--color-gold-700)] shadow-[0_4px_12px_-4px_rgba(201,162,39,0.3)]">
                    <Bot size={16} className="text-[#141008]" />
                  </div>
                ) : (
                  <Avatar name="Ananya Rao" size={32} />
                )}
                
                <div className={cn("space-y-3 min-w-0", m.role === "user" && "flex flex-col items-end")}>
                  <div
                    className={cn(
                      "rounded-2xl px-5 py-3.5 text-[14px] leading-[1.6] text-left border shadow-sm",
                      m.role === "assistant"
                        ? "bg-white/[0.02] backdrop-blur-sm border-[var(--color-border-hairline)] text-[var(--color-ink-1)]"
                        : "bg-white/[0.05] border-[var(--color-border-hairline)] text-[var(--color-ink-0)] font-medium"
                    )}
                  >
                    {/* Render text simply. Future-ready for react-markdown. */}
                    <div className="whitespace-pre-wrap">{m.content}</div>
                  </div>
                  
                  {m.role === "assistant" && (
                    <div className="flex items-center gap-4 pl-1">
                      <div className="flex items-center gap-1 opacity-60 hover:opacity-100 transition-opacity">
                        <button className="p-1 rounded text-[var(--color-ink-4)] hover:text-[var(--color-ink-1)] hover:bg-white/5" title="Copy response">
                          <Copy size={12} />
                        </button>
                        <button className="p-1 rounded text-[var(--color-ink-4)] hover:text-[var(--color-ink-1)] hover:bg-white/5" title="Regenerate">
                          <RefreshCw size={12} />
                        </button>
                      </div>
                      
                      {m.citations && m.citations.length > 0 && (
                        <div className="flex items-center gap-2 text-[11px] text-[var(--color-ink-4)]">
                          <span>·</span>
                          <span className="flex items-center gap-1.5"><FileText size={11} className="text-[var(--color-gold-500)]" /> {m.citations.length} Sources</span>
                        </div>
                      )}
                    </div>
                  )}

                  {m.role === "assistant" && m.followUps && index === messages.length - 1 && (
                    <div className="flex flex-wrap gap-2 pt-2">
                      {m.followUps.map((f) => (
                        <button
                          key={f}
                          onClick={() => send(f)}
                          className="flex items-center gap-1.5 rounded-full border border-[var(--color-border-hairline)] px-3 py-1.5 text-xs text-[var(--color-ink-2)] bg-white/[0.01] hover:bg-white/[0.04] hover:border-[var(--color-gold-500)]/30 hover:text-[var(--color-gold-200)] transition-all"
                        >
                          {f} <ArrowRight size={10} className="opacity-50" />
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}

            {isThinking && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-4 max-w-3xl mr-auto">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-[var(--color-gold-300)] to-[var(--color-gold-700)] shadow-[0_4px_12px_-4px_rgba(201,162,39,0.3)]">
                  <Bot size={16} className="text-[#141008]" />
                </div>
                <div className="flex flex-col gap-2 w-full max-w-md">
                  <div className="flex items-center gap-2 text-xs text-[var(--color-ink-4)] mb-1">
                    <Loader2 size={12} className="animate-spin text-[var(--color-gold-500)]" />
                    <span>Analyzing documents...</span>
                  </div>
                  <Skeleton className="h-4 w-full bg-white/[0.03]" />
                  <Skeleton className="h-4 w-[85%] bg-white/[0.03]" />
                  <Skeleton className="h-4 w-[60%] bg-white/[0.03]" />
                </div>
              </motion.div>
            )}
          </div>

          <div className="p-4 border-t border-[var(--color-border-hairline)] shrink-0">
            <div className="flex items-center gap-2 rounded-xl border border-[var(--color-border-hairline)] bg-white/[0.02] px-4 py-3 focus-within:border-[var(--color-gold-500)]/50 focus-within:bg-white/[0.04] transition-all shadow-sm">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send(input)}
                placeholder="Message the AI Analyst..."
                disabled={isThinking}
                className="flex-1 bg-transparent text-[15px] text-[var(--color-ink-0)] placeholder:text-[var(--color-ink-4)] outline-none disabled:opacity-50"
              />
              <Button size="icon" variant="primary" onClick={() => send(input)} disabled={!input.trim() || isThinking} className="h-8 w-8 rounded-lg">
                <Send size={14} />
              </Button>
            </div>
          </div>
        </div>

        {/* RIGHT PANE: Persistent Analysis Sidebar (30%) */}
        <div className="border-l border-[var(--color-border-hairline)] bg-[var(--color-surface-0)] overflow-y-auto pb-8 hidden xl:block">
          
          {/* Analyst Metadata */}
          <div className="p-5 border-b border-[var(--color-border-hairline)] bg-white/[0.01]">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2.5">
                <div className="h-6 w-6 rounded bg-[var(--color-gold-500)]/20 flex items-center justify-center">
                  <Bot size={14} className="text-[var(--color-gold-400)]" />
                </div>
                <h3 className="font-display text-sm text-[var(--color-ink-0)]">AI Analyst</h3>
              </div>
              <span className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider font-medium text-[var(--color-emerald)] bg-[var(--color-emerald)]/10 px-2 py-0.5 rounded-sm">
                <span className="h-1.5 w-1.5 rounded-full bg-[var(--color-emerald)] animate-pulse" /> Ready
              </span>
            </div>
            
            <div className="grid grid-cols-2 gap-y-3 gap-x-4 text-[11px] mb-5">
              <div>
                <p className="text-[var(--color-ink-4)] mb-0.5">Model</p>
                <p className="text-[var(--color-ink-1)] font-mono">GPT-4o</p>
              </div>
              <div>
                <p className="text-[var(--color-ink-4)] mb-0.5">Workspace</p>
                <p className="text-[var(--color-ink-1)] truncate">{company?.name}</p>
              </div>
              <div>
                <p className="text-[var(--color-ink-4)] mb-0.5">Documents</p>
                <p className="text-[var(--color-ink-1)] font-mono">{documents.length}</p>
              </div>
              <div>
                <p className="text-[var(--color-ink-4)] mb-0.5">Messages</p>
                <p className="text-[var(--color-ink-1)] font-mono">{messages.length}</p>
              </div>
            </div>

            <div className="flex gap-2">
              <Button variant="secondary" size="sm" className="flex-1 text-xs h-7 bg-white/[0.03]">
                <FileJson size={12} className="mr-1" /> Export MD
              </Button>
              <Button variant="secondary" size="sm" className="flex-1 text-xs h-7 bg-white/[0.03]">
                <Download size={12} className="mr-1" /> Export Memo
              </Button>
            </div>
          </div>

          {!latestAiMessage ? (
            <div className="p-6 text-center text-sm text-[var(--color-ink-4)]">
              Waiting for analysis...
            </div>
          ) : (
            <div className="p-5 space-y-6">
              
              {/* Confidence Widget */}
              <div>
                <p className="text-[10px] uppercase tracking-wider text-[var(--color-ink-4)] font-medium mb-3">Response Confidence</p>
                <div className="flex items-center justify-between p-3 rounded-lg border border-[var(--color-border-hairline)] bg-white/[0.01]">
                  <div className="flex items-center gap-3">
                    <ConfidenceRing value={latestAiMessage.confidence ?? 92} size={32} strokeWidth={3} />
                    <div>
                      <p className="text-sm font-medium text-[var(--color-ink-1)]">{latestAiMessage.confidence ?? 92}%</p>
                      <p className="text-[10px] text-[var(--color-ink-4)]">Overall Score</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-[var(--color-ink-1)]">{latestAiMessage.citations?.length ?? 0}</p>
                    <p className="text-[10px] text-[var(--color-ink-4)]">Sources Used</p>
                  </div>
                </div>
              </div>

              {/* Reasoning Timeline */}
              {latestAiMessage.reasoning && (
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-[var(--color-ink-4)] font-medium mb-4">Analysis Pipeline</p>
                  <div className="space-y-4 relative before:absolute before:inset-0 before:ml-[11px] before:-translate-x-px before:h-full before:w-0.5 before:bg-[var(--color-border-hairline)] before:z-0">
                    
                    {latestAiMessage.reasoning.map((step, i) => {
                      const isComplete = true; // Simulating completed pipeline steps
                      return (
                        <div key={i} className="relative z-10 flex gap-3">
                          <div className={cn(
                            "h-6 w-6 rounded-full flex items-center justify-center shrink-0 border mt-0.5",
                            isComplete ? "bg-[var(--color-emerald)]/10 border-[var(--color-emerald)]/20" : "bg-white/[0.05] border-[var(--color-border-hairline)]"
                          )}>
                            {isComplete ? <CheckCircle2 size={12} className="text-[var(--color-emerald)]" /> : <Circle size={10} className="text-[var(--color-ink-4)]" />}
                          </div>
                          <div>
                            <div className="flex items-center justify-between gap-4 mb-0.5">
                              <p className="text-[12.5px] font-medium text-[var(--color-ink-1)]">{step.label}</p>
                              <span className="text-[9px] text-[var(--color-ink-4)] uppercase bg-white/[0.03] px-1.5 py-0.5 rounded font-medium">Done</span>
                            </div>
                            <p className="text-[11px] text-[var(--color-ink-3)] leading-relaxed">{step.detail}</p>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Evidence Cards */}
              {latestAiMessage.citations && latestAiMessage.citations.length > 0 && (
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-[var(--color-ink-4)] font-medium mb-3">Evidence Cited</p>
                  <div className="space-y-2.5">
                    {latestAiMessage.citations.map((c, i) => (
                      <GlassCard key={c.id} className="overflow-hidden bg-white/[0.01]" raised>
                        <button
                          onClick={() => toggleEvidence(c.id)}
                          className="w-full text-left p-3 hover:bg-white/[0.02] transition-colors focus:outline-none"
                        >
                          <div className="flex items-start gap-2.5">
                            <span className="flex items-center justify-center h-5 w-5 rounded bg-[var(--color-gold-500)]/20 text-[var(--color-gold-400)] text-[10px] font-bold shrink-0 mt-0.5">
                              [{i + 1}]
                            </span>
                            <div className="flex-1 min-w-0">
                              <p className="text-[12.5px] font-medium text-[var(--color-ink-1)] truncate leading-snug">{c.doc}</p>
                              <div className="flex items-center gap-3 mt-1.5">
                                <span className="text-[10px] font-mono text-[var(--color-ink-4)]">Page {c.page}</span>
                                <span className="flex items-center gap-1 text-[10px] font-mono text-[var(--color-ink-4)]">
                                  <ConfidenceRing value={98 - i} size={10} /> {98 - i}%
                                </span>
                              </div>
                            </div>
                            {expandedEvidence[c.id] ? (
                              <ChevronUp size={14} className="text-[var(--color-ink-4)] shrink-0" />
                            ) : (
                              <ChevronDown size={14} className="text-[var(--color-ink-4)] shrink-0" />
                            )}
                          </div>
                        </button>
                        
                        <AnimatePresence>
                          {expandedEvidence[c.id] && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: "auto", opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              transition={{ duration: 0.2 }}
                              className="border-t border-[var(--color-border-hairline)]"
                            >
                              <div className="p-3 bg-[var(--color-surface-0)]/50">
                                <p className="text-[12px] text-[var(--color-ink-2)] italic leading-relaxed text-justify border-l-2 border-[var(--color-gold-500)]/30 pl-3">
                                  "{c.snippet}"
                                </p>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </GlassCard>
                    ))}
                  </div>
                </div>
              )}

            </div>
          )}
        </div>
      </div>
    </div>
  );
}
