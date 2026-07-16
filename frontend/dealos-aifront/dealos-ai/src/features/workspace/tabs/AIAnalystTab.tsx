import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { GlassCard } from "@/components/ui/GlassCard";
import { Avatar } from "@/components/ui/Avatar";
import { ConfidenceRing } from "@/components/ui/ConfidenceRing";
import { Button } from "@/components/ui/Button";
import { StreamingText } from "@/components/ui/StreamingText";
import { conversationSeed, suggestedQuestions, generateResponse, type ChatMessage } from "@/lib/aiAnalyst";
import { getCompany } from "@/lib/mockData";
import { Bot, Send, FileText, Sparkles, MessageSquarePlus, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

const threadTitles = ["This conversation", "Payor mix deep dive", "Q1 diligence questions", "Covenant scenario modeling"];

export function AIAnalystTab() {
  const { id } = useParams();
  const company = getCompany(id!);
  const [messages, setMessages] = useState<ChatMessage[]>(conversationSeed[id!] ?? []);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const [selectedMsgId, setSelectedMsgId] = useState<string | null>(
    () => messages.filter((m) => m.role === "assistant").slice(-1)[0]?.id ?? null
  );
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, thinking]);

  const selectedMsg = messages.find((m) => m.id === selectedMsgId);
  const questions = suggestedQuestions[id!] ?? [
    "Summarize the key financial trends",
    "What are the top risks in this workspace?",
  ];

  function send(text: string) {
    if (!text.trim() || !id) return;
    const userMsg: ChatMessage = { id: `u-${Date.now()}`, role: "user", content: text };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setThinking(true);
    setTimeout(() => {
      const response = generateResponse(id, text);
      setMessages((m) => [...m, response]);
      setSelectedMsgId(response.id);
      setThinking(false);
    }, 1100);
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[220px_1fr_320px] gap-4 items-start">
      {/* Conversation rail */}
      <GlassCard className="p-3 hidden xl:block sticky top-24" raised>
        <Button variant="secondary" size="sm" className="w-full justify-center mb-3">
          <MessageSquarePlus size={14} /> New thread
        </Button>
        <div className="space-y-0.5">
          {threadTitles.map((t, i) => (
            <button
              key={t}
              className={cn(
                "w-full text-left rounded-lg px-2.5 py-2 text-[13px] truncate transition-colors",
                i === 0 ? "bg-[var(--color-gold-500)]/[0.09] text-[var(--color-gold-200)]" : "text-[var(--color-ink-3)] hover:bg-white/[0.04] hover:text-[var(--color-ink-0)]"
              )}
            >
              {t}
            </button>
          ))}
        </div>
      </GlassCard>

      {/* Chat transcript */}
      <div className="flex flex-col h-[calc(100vh-260px)] min-h-[480px]">
        <GlassCard className="flex-1 flex flex-col overflow-hidden" raised>
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-5 space-y-5">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center gap-2 px-8">
                <Bot size={28} className="text-[var(--color-gold-500)]/60" />
                <p className="font-display text-base text-[var(--color-ink-0)]">Ask the AI Analyst anything about {company?.name}</p>
                <p className="text-xs text-[var(--color-ink-3)] max-w-sm">Answers are grounded in the documents processed for this workspace, with full source citations.</p>
              </div>
            )}
            {messages.map((m) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
                className={cn("flex gap-3", m.role === "user" && "flex-row-reverse")}
              >
                {m.role === "assistant" ? (
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[var(--color-gold-300)] to-[var(--color-gold-700)]">
                    <Bot size={14} className="text-[#141008]" />
                  </div>
                ) : (
                  <Avatar name="Ananya Rao" size={28} />
                )}
                <div className={cn("max-w-[80%] space-y-2", m.role === "user" && "flex flex-col items-end")}>
                  <button
                    onClick={() => m.role === "assistant" && setSelectedMsgId(m.id)}
                    className={cn(
                      "rounded-2xl px-4 py-2.5 text-[13.5px] leading-relaxed text-left transition-all duration-200",
                      m.role === "assistant"
                        ? cn(
                            "bg-white/[0.03] backdrop-blur-sm border text-[var(--color-ink-1)] shadow-[0_1px_0_rgba(255,255,255,0.04)_inset]",
                            selectedMsgId === m.id
                              ? "border-[var(--color-gold-500)]/50 shadow-[0_1px_0_rgba(255,255,255,0.04)_inset,0_0_0_1px_rgba(201,162,39,0.12),0_12px_24px_-12px_rgba(201,162,39,0.25)]"
                              : "border-[var(--color-border-hairline)] hover:border-[var(--color-border-strong)]"
                          )
                        : "bg-gradient-to-b from-[var(--color-gold-300)] to-[var(--color-gold-500)] text-[#141008] font-medium shadow-[0_1px_0_rgba(255,255,255,0.35)_inset,0_8px_20px_-8px_rgba(201,162,39,0.4)]"
                    )}
                  >
                    {m.role === "assistant" ? <StreamingText text={m.content} /> : m.content}
                  </button>
                  {m.role === "assistant" && m.confidence !== undefined && (
                    <div className="flex items-center gap-2 pl-1">
                      <ConfidenceRing value={m.confidence} size={22} />
                      <span className="text-[11px] text-[var(--color-ink-4)]">confidence</span>
                      {m.citations && m.citations.length > 0 && (
                        <span className="text-[11px] text-[var(--color-ink-4)] flex items-center gap-1">
                          · <FileText size={11} /> {m.citations.length} source{m.citations.length > 1 ? "s" : ""}
                        </span>
                      )}
                    </div>
                  )}
                  {m.followUps && (
                    <div className="flex flex-wrap gap-1.5 pl-1">
                      {m.followUps.map((f) => (
                        <button
                          key={f}
                          onClick={() => send(f)}
                          className="rounded-full border border-[var(--color-border-hairline)] px-2.5 py-1 text-[11px] text-[var(--color-ink-3)] hover:border-[var(--color-border-strong)] hover:text-[var(--color-ink-0)] transition-colors"
                        >
                          {f}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
            <AnimatePresence>
              {thinking && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex gap-3">
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[var(--color-gold-300)] to-[var(--color-gold-700)]">
                    <Bot size={14} className="text-[#141008]" />
                  </div>
                  <div className="rounded-2xl px-4 py-3 bg-white/[0.03] border border-[var(--color-border-hairline)] flex items-center gap-1.5">
                    {[0, 1, 2].map((i) => (
                      <motion.span
                        key={i}
                        className="h-1.5 w-1.5 rounded-full bg-[var(--color-gold-400)]"
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 1.1, repeat: Infinity, delay: i * 0.15 }}
                      />
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="border-t border-[var(--color-border-hairline)] p-4">
            {messages.length === 0 && (
              <div className="flex flex-wrap gap-1.5 mb-3">
                {questions.map((q) => (
                  <button
                    key={q}
                    onClick={() => send(q)}
                    className="flex items-center gap-1 rounded-full border border-[var(--color-border-hairline)] px-3 py-1.5 text-xs text-[var(--color-ink-2)] hover:border-[var(--color-border-strong)] hover:text-[var(--color-ink-0)] transition-colors"
                  >
                    <Sparkles size={11} className="text-[var(--color-gold-500)]" /> {q}
                  </button>
                ))}
              </div>
            )}
            <div className="flex items-center gap-2 rounded-xl border border-[var(--color-border-hairline)] bg-white/[0.02] px-3 py-2 focus-within:border-[var(--color-border-strong)] transition-colors">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send(input)}
                placeholder={`Ask about ${company?.name}'s financials, risks, or documents…`}
                className="flex-1 bg-transparent text-sm text-[var(--color-ink-0)] placeholder:text-[var(--color-ink-4)] outline-none"
              />
              <Button size="icon" variant="primary" onClick={() => send(input)} disabled={!input.trim()}>
                <Send size={14} />
              </Button>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Evidence panel */}
      <GlassCard className="p-5 hidden xl:block sticky top-24 max-h-[calc(100vh-260px)] overflow-y-auto" raised>
        <p className="font-display text-base text-[var(--color-ink-0)] mb-4">Evidence &amp; Reasoning</p>
        <AnimatePresence mode="wait">
          {!selectedMsg || selectedMsg.role !== "assistant" ? (
            <motion.p key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="text-xs text-[var(--color-ink-3)]">
              Select an answer in the transcript to inspect its sources and reasoning trace.
            </motion.p>
          ) : (
            <motion.div
              key={selectedMsg.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
              className="space-y-5"
            >
              {selectedMsg.reasoning && (
                <div>
                  <p className="text-[11px] uppercase tracking-wider text-[var(--color-ink-4)] mb-2.5">Reasoning trace</p>
                  <div className="space-y-3">
                    {selectedMsg.reasoning.map((r, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -6 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3, delay: i * 0.08, ease: [0.16, 1, 0.3, 1] }}
                        className="flex gap-2.5"
                      >
                        <div className="flex flex-col items-center pt-0.5">
                          <span className="h-1.5 w-1.5 rounded-full bg-[var(--color-gold-500)] shadow-[0_0_6px_rgba(201,162,39,0.7)]" />
                          {i < selectedMsg.reasoning!.length - 1 && <span className="w-px flex-1 bg-[var(--color-border-hairline)] mt-1" />}
                        </div>
                        <div className="pb-1">
                          <p className="text-xs font-medium text-[var(--color-ink-1)]">{r.label}</p>
                          <p className="text-[11px] text-[var(--color-ink-4)] mt-0.5 leading-relaxed">{r.detail}</p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}
              {selectedMsg.citations && selectedMsg.citations.length > 0 && (
                <div>
                  <p className="text-[11px] uppercase tracking-wider text-[var(--color-ink-4)] mb-2.5">Source citations</p>
                  <div className="space-y-2.5">
                    {selectedMsg.citations.map((c, i) => (
                      <motion.button
                        key={c.id}
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: i * 0.06, ease: [0.16, 1, 0.3, 1] }}
                        whileHover={{ y: -2 }}
                        className="w-full text-left rounded-lg border border-[var(--color-border-hairline)] bg-white/[0.02] p-3 hover:border-[var(--color-gold-500)]/40 hover:shadow-[0_10px_24px_-12px_rgba(201,162,39,0.35)] transition-[border-color,box-shadow] duration-200 group"
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="flex items-center gap-1.5 text-xs font-medium text-[var(--color-ink-0)] truncate">
                            <FileText size={12} className="text-[var(--color-gold-500)] shrink-0" /> {c.doc}
                          </span>
                          <ChevronRight size={12} className="text-[var(--color-ink-4)] group-hover:text-[var(--color-gold-400)] group-hover:translate-x-0.5 transition-all shrink-0" />
                        </div>
                        <p className="text-[11px] text-[var(--color-ink-3)] italic leading-relaxed">"{c.snippet}"</p>
                        <p className="text-[10px] text-[var(--color-ink-4)] font-mono mt-1.5">Page {c.page}</p>
                      </motion.button>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </GlassCard>
    </div>
  );
}
