"use client";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { AgentOutput, reportBrokenLink } from "@/lib/api";

const AGENT_COLORS: Record<string, { icon: string; dotColor: string }> = {
  "Intérprete": { icon: "🔵", dotColor: "bg-indigo-500" },
  "Solucionador": { icon: "🟢", dotColor: "bg-emerald-500" },
  "Visualizador": { icon: "🟠", dotColor: "bg-orange-500" },
  "Curador": { icon: "🟣", dotColor: "bg-purple-500" },
  "Avaliador": { icon: "🔴", dotColor: "bg-red-500" },
};

export function AgentPanel({
  agent,
  streaming,
  sessionId,
  studentEmail,
}: {
  agent: AgentOutput;
  streaming?: boolean;
  sessionId?: string | null;
  studentEmail?: string;
}) {
  const [showReport, setShowReport] = useState(false);
  const [url, setUrl] = useState("");
  const [note, setNote] = useState("");
  const [sent, setSent] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);

  const config = AGENT_COLORS[agent.agent_name] || {
    icon: "⚙️",
    dotColor: "bg-slate-500",
  };

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
      setTimeout(() => {
        setSent(false);
        setShowReport(false);
      }, 2000);
    } catch (err) {
      console.error("Failed to report link:", err);
    } finally {
      setReportLoading(false);
    }
  };

  return (
    <div className="animate-slide-in-up glass rounded-lg p-5 border border-slate-700/50 dark:border-slate-700/50 hover:border-slate-600/50 dark:hover:border-slate-600/50 transition">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <span className="text-lg">{config.icon}</span>
        <div className="flex-1">
          <h3 className="font-semibold text-slate-50 dark:text-slate-50 text-sm">{agent.agent_name}</h3>
          <p className="text-xs text-slate-500 dark:text-slate-500">{agent.dimension}</p>
        </div>
        {streaming && (
          <span className="text-xs text-slate-400 dark:text-slate-400 flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${config.dotColor} animate-pulse`}></span>
            <span>Gerando...</span>
          </span>
        )}
      </div>

      {/* Content */}
      <div className="prose prose-sm prose-invert dark:prose-invert max-w-none
                     prose-p:my-2 prose-p:leading-relaxed prose-p:text-slate-300 dark:prose-p:text-slate-300
                     prose-headings:font-semibold prose-headings:my-3 prose-headings:text-slate-50 dark:prose-headings:text-slate-50
                     prose-h1:text-lg prose-h2:text-base prose-h3:text-sm
                     prose-a:text-cyan-400 dark:prose-a:text-cyan-400 prose-a:underline hover:prose-a:text-cyan-300 dark:hover:prose-a:text-cyan-300
                     prose-strong:font-semibold prose-strong:text-slate-100 dark:prose-strong:text-slate-100
                     prose-code:bg-slate-900/50 dark:prose-code:bg-slate-900/50 prose-code:text-cyan-300 dark:prose-code:text-cyan-300 prose-code:px-2 prose-code:py-1 prose-code:rounded prose-code:text-xs prose-code:border prose-code:border-slate-700/50 dark:prose-code:border-slate-700/50
                     prose-pre:bg-slate-900/50 dark:prose-pre:bg-slate-900/50 prose-pre:border prose-pre:border-slate-700/50 dark:prose-pre:border-slate-700/50 prose-pre:rounded-lg prose-pre:p-4 prose-pre:overflow-x-auto
                     prose-pre:text-slate-200 dark:prose-pre:text-slate-200 prose-pre:text-sm
                     prose-li:my-1 prose-li:text-slate-300 dark:prose-li:text-slate-300
                     prose-blockquote:border-l-2 prose-blockquote:border-indigo-500/50 dark:prose-blockquote:border-indigo-500/50 prose-blockquote:pl-4 prose-blockquote:text-slate-400 dark:prose-blockquote:text-slate-400 prose-blockquote:italic">
        <ReactMarkdown
          remarkPlugins={[remarkMath]}
          rehypePlugins={[[rehypeKatex, { throwOnError: false, strict: false }]]}
        >
          {agent.content}
        </ReactMarkdown>
      </div>

      {/* Report Broken Link */}
      <div className="mt-4 pt-3 border-t border-slate-700/30 dark:border-slate-700/30">
        {!showReport ? (
          <button
            onClick={() => setShowReport(true)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs text-slate-500 dark:text-slate-500 hover:text-slate-300 dark:hover:text-slate-300 hover:bg-slate-700/30 dark:hover:bg-slate-700/30 transition-all"
          >
            🔗 Reportar referência quebrada
          </button>
        ) : sent ? (
          <p className="text-xs text-emerald-400 dark:text-emerald-400">✅ Reportado! Obrigado.</p>
        ) : (
          <form onSubmit={handleReportSubmit} className="space-y-2">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Cole o link quebrado aqui"
              className="w-full px-2.5 py-1.5 rounded-lg bg-slate-800/50 dark:bg-slate-800/50 border border-slate-700/50 dark:border-slate-700/50 text-slate-50 dark:text-slate-50 placeholder-slate-500 dark:placeholder-slate-500 text-xs transition-all focus:outline-none focus:border-indigo-500/50 dark:focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/20 dark:focus:ring-indigo-500/20"
            />
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="O que aconteceu? (opcional)"
              maxLength={200}
              className="w-full px-2.5 py-1.5 rounded-lg bg-slate-800/50 dark:bg-slate-800/50 border border-slate-700/50 dark:border-slate-700/50 text-slate-50 dark:text-slate-50 placeholder-slate-500 dark:placeholder-slate-500 text-xs resize-none transition-all focus:outline-none focus:border-indigo-500/50 dark:focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/20 dark:focus:ring-indigo-500/20"
              rows={2}
            />
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={reportLoading || !url.trim()}
                className="px-3 py-1 rounded-full bg-indigo-600 dark:bg-indigo-600 hover:bg-indigo-700 dark:hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-medium transition-all"
              >
                {reportLoading ? "Enviando..." : "Enviar"}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowReport(false);
                  setUrl("");
                  setNote("");
                }}
                className="px-3 py-1 rounded-full bg-slate-700/50 dark:bg-slate-700/50 hover:bg-slate-700 dark:hover:bg-slate-700 text-slate-300 dark:text-slate-300 text-xs font-medium transition-all"
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
