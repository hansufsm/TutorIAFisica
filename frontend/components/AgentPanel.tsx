"use client";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { AgentOutput, reportBrokenLink, submitFeedback } from "@/lib/api";

// Convert TeX-style delimiters (\[...\] and \(...\)) to remark-math's $...$ syntax
function normalizeLatex(content: string): string {
  return content
    .replace(/\\\[([\s\S]*?)\\\]/g, (_, math) => `\n\n$$\n${math.trim()}\n$$\n\n`)
    .replace(/\\\(([^)]+)\\\)/g, (_, math) => `$${math.trim()}$`);
}

const AGENT_COLORS: Record<string, { icon: string; dotColor: string }> = {
  "Intérprete":   { icon: "🔵", dotColor: "bg-indigo-400" },
  "Solucionador": { icon: "🟢", dotColor: "bg-emerald-400" },
  "Visualizador": { icon: "🟠", dotColor: "bg-orange-400" },
  "Curador":      { icon: "🟣", dotColor: "bg-purple-400" },
  "Avaliador":    { icon: "🔴", dotColor: "bg-red-400" },
};

export function AgentPanel({
  agent,
  streaming,
  sessionId,
  studentEmail,
  topic,
}: {
  agent: AgentOutput;
  streaming?: boolean;
  sessionId?: string | null;
  studentEmail?: string;
  topic?: string;
}) {
  const [showReport, setShowReport] = useState(false);
  const [url, setUrl] = useState("");
  const [note, setNote] = useState("");
  const [sent, setSent] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);

  // SM-2 quiz feedback (only for Avaliador)
  const [quizAnswer, setQuizAnswer] = useState<"correct" | "incorrect" | null>(null);
  const [quizLoading, setQuizLoading] = useState(false);

  const config = AGENT_COLORS[agent.agent_name] || { icon: "⚙️", dotColor: "bg-stone-400" };

  const handleReportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setReportLoading(true);
    try {
      await reportBrokenLink({
        studentEmail: studentEmail || "aluno@ufsm.br",
        sessionId,
        agentName: agent.agent_name,
        url,
        note: note.trim() || undefined,
      });
      setSent(true);
      setUrl("");
      setNote("");
      setTimeout(() => { setSent(false); setShowReport(false); }, 2000);
    } catch (err) {
      console.error("Failed to report link:", err);
    } finally {
      setReportLoading(false);
    }
  };

  const handleQuizFeedback = async (correct: boolean) => {
    if (!studentEmail || quizAnswer || quizLoading) return;
    setQuizLoading(true);
    try {
      await submitFeedback(
        studentEmail,
        sessionId ?? `session_${Date.now()}`,
        topic ?? "física",
        correct,
        correct ? 4 : 2,
      );
      setQuizAnswer(correct ? "correct" : "incorrect");
    } catch (err) {
      console.error("Failed to submit quiz feedback:", err);
    } finally {
      setQuizLoading(false);
    }
  };

  return (
    <div className="animate-slide-in-up bg-white rounded-xl p-5 border shadow-sm transition hover:shadow-md print-content" style={{ borderColor: "var(--border)" }}>

      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <span className="text-lg">{config.icon}</span>
        <div className="flex-1">
          <h3 className="font-semibold text-stone-900 text-sm">{agent.agent_name}</h3>
          <p className="text-xs text-stone-400">{agent.dimension}</p>
        </div>
        {streaming && (
          <span className="text-xs text-stone-500 flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${config.dotColor} animate-pulse`} />
            Gerando…
          </span>
        )}
      </div>

      {/* Content */}
      <div className="prose prose-sm max-w-none
                      prose-p:my-2 prose-p:leading-relaxed prose-p:text-stone-700
                      prose-headings:font-semibold prose-headings:my-3 prose-headings:text-stone-900
                      prose-h1:text-base prose-h2:text-sm prose-h3:text-sm
                      prose-a:text-indigo-600 prose-a:underline hover:prose-a:text-indigo-800
                      prose-strong:font-semibold prose-strong:text-stone-900
                      prose-code:bg-stone-100 prose-code:text-indigo-700 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-xs prose-code:border prose-code:border-stone-200
                      prose-pre:bg-stone-50 prose-pre:border prose-pre:border-stone-200 prose-pre:rounded-lg prose-pre:p-4 prose-pre:overflow-x-auto prose-pre:text-sm
                      prose-li:my-1 prose-li:text-stone-700
                      prose-blockquote:border-l-2 prose-blockquote:border-indigo-300 prose-blockquote:pl-4 prose-blockquote:text-stone-500 prose-blockquote:italic">
        <ReactMarkdown
          remarkPlugins={[remarkMath]}
          rehypePlugins={[[rehypeKatex, { throwOnError: false, strict: false }]]}
        >
          {normalizeLatex(agent.content)}
        </ReactMarkdown>
      </div>

      {/* SM-2 Quiz Feedback — only for Avaliador */}
      {agent.agent_name === "Avaliador" && !streaming && (
        <div className="mt-4 pt-3 border-t" style={{ borderColor: "var(--border)" }}>
          {quizAnswer ? (
            <p className={`text-xs font-medium ${quizAnswer === "correct" ? "text-emerald-600" : "text-amber-600"}`}>
              {quizAnswer === "correct"
                ? "✅ Ótimo! Progresso registrado."
                : "📝 Anotado — revisaremos este conceito em breve."}
            </p>
          ) : (
            <div>
              <p className="text-xs text-stone-500 mb-2">Você conseguiu responder ao desafio?</p>
              <div className="flex gap-2">
                <button
                  onClick={() => handleQuizFeedback(true)}
                  disabled={quizLoading}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 text-emerald-700 text-xs font-medium transition disabled:opacity-40"
                >
                  ✅ Acertei
                </button>
                <button
                  onClick={() => handleQuizFeedback(false)}
                  disabled={quizLoading}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-50 hover:bg-amber-100 border border-amber-200 text-amber-700 text-xs font-medium transition disabled:opacity-40"
                >
                  ❌ Errei
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Report Broken Link */}
      <div className="mt-4 pt-3 border-t" style={{ borderColor: "var(--border)" }}>
        {!showReport ? (
          <button
            onClick={() => setShowReport(true)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs text-stone-400 hover:text-stone-600 hover:bg-stone-100 transition-all"
          >
            🔗 Reportar referência quebrada
          </button>
        ) : sent ? (
          <p className="text-xs text-emerald-600">✅ Reportado! Obrigado.</p>
        ) : (
          <form onSubmit={handleReportSubmit} className="space-y-2">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Cole o link quebrado aqui"
              className="w-full px-2.5 py-1.5 rounded-lg bg-white text-stone-800 placeholder-stone-400 text-xs border focus:outline-none focus:ring-2 focus:ring-indigo-400/30"
              style={{ borderColor: "var(--border)" }}
            />
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="O que aconteceu? (opcional)"
              maxLength={200}
              className="w-full px-2.5 py-1.5 rounded-lg bg-white text-stone-800 placeholder-stone-400 text-xs resize-none border focus:outline-none focus:ring-2 focus:ring-indigo-400/30"
              style={{ borderColor: "var(--border)" }}
              rows={2}
            />
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={reportLoading || !url.trim()}
                className="px-3 py-1 rounded-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-medium transition-all"
              >
                {reportLoading ? "Enviando…" : "Enviar"}
              </button>
              <button
                type="button"
                onClick={() => { setShowReport(false); setUrl(""); setNote(""); }}
                className="px-3 py-1 rounded-full bg-stone-100 hover:bg-stone-200 text-stone-600 text-xs font-medium transition-all border border-stone-200"
              >
                Cancelar
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
