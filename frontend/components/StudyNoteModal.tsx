"use client";

import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { AgentOutput, DueReview, WeeklyTopic } from "@/lib/api";
import { X, Printer } from "lucide-react";

interface StudyNoteModalProps {
  question: string;
  agents: AgentOutput[];
  sessionId: string | null;
  model: string;
  responseTimeMs: number;
  due: DueReview[];
  weeklyTopics: WeeklyTopic[];
  currentWeek: number;
  studentEmail: string;
  onClose: () => void;
}

const AGENT_META: Record<string, {
  icon: string; label: string;
  borderColor: string; bgColor: string;
  badgeBg: string; badgeText: string;
}> = {
  "Intérprete":   { icon: "🔵", label: "Análise Socrática",     borderColor: "#3B82F6", bgColor: "#EFF6FF", badgeBg: "bg-blue-100",   badgeText: "text-blue-700" },
  "Solucionador": { icon: "🟢", label: "Resolução Matemática",  borderColor: "#22C55E", bgColor: "#F0FDF4", badgeBg: "bg-green-100",  badgeText: "text-green-700" },
  "Visualizador": { icon: "🟠", label: "Visualização / Código", borderColor: "#F97316", bgColor: "#FFF7ED", badgeBg: "bg-orange-100", badgeText: "text-orange-700" },
  "Curador":      { icon: "🟣", label: "Referências Acadêmicas",borderColor: "#A855F7", bgColor: "#FAF5FF", badgeBg: "bg-purple-100", badgeText: "text-purple-700" },
  "Avaliador":    { icon: "🔴", label: "Desafio de Fixação",    borderColor: "#EF4444", bgColor: "#FFF1F2", badgeBg: "bg-red-100",    badgeText: "text-red-700" },
};

// Convert TeX delimiters before passing to remark-math (same as AgentPanel)
function normalizeTex(src: string): string {
  return src
    .replace(/\\\[/g, "$$").replace(/\\\]/g, "$$")
    .replace(/\\\(/g, "$").replace(/\\\)/g, "$");
}

function formatDate(d: Date) {
  return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric" });
}

function MasteryBar({ mastery, label }: { mastery: number; label: string }) {
  const pct = Math.round(mastery * 100);
  const color = pct >= 80 ? "bg-emerald-500" : pct >= 40 ? "bg-yellow-500" : "bg-orange-400";
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-stone-700 w-36 truncate" title={label}>{label}</span>
      <div className="flex-1 h-2 rounded-full bg-stone-200 overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-semibold text-stone-600 w-8 text-right">{pct}%</span>
    </div>
  );
}

export function StudyNoteModal({
  question, agents, sessionId, model, responseTimeMs,
  due, weeklyTopics, currentWeek, studentEmail, onClose,
}: StudyNoteModalProps) {
  const now = new Date();
  const dateStr = formatDate(now);
  const timeStr = `${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}`;
  const respSec = responseTimeMs > 0 ? (responseTimeMs / 1000).toFixed(1) : null;

  // Derive discipline/topic from weeklyTopics or due concepts
  const primaryTopic = weeklyTopics[0]?.tema ?? due[0]?.topic ?? "";
  const primaryDisc  = weeklyTopics[0]
    ? `${weeklyTopics[0].disciplina_codigo} — ${weeklyTopics[0].disciplina_nome}`
    : "";

  const sessionShort = sessionId ? sessionId.slice(0, 8) : "—";

  return (
    <div className="study-note-print fixed inset-0 z-50 overflow-y-auto bg-white">

      {/* ── Controls bar (hidden on print) ── */}
      <div className="print:hidden sticky top-0 z-10 flex items-center justify-between gap-3 bg-white/95 backdrop-blur border-b border-stone-200 px-6 py-3">
        <div className="flex items-center gap-2 text-sm text-stone-600">
          <span className="font-semibold text-stone-800">Nota de Estudo</span>
          <span className="text-stone-300">·</span>
          <span>{dateStr}</span>
          {primaryTopic && (
            <>
              <span className="text-stone-300">·</span>
              <span className="px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700 text-xs font-medium">{primaryTopic}</span>
            </>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => window.print()}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold transition"
          >
            <Printer size={13} />
            Imprimir / Salvar PDF
          </button>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-stone-400 hover:bg-stone-100 hover:text-stone-700 transition"
            title="Fechar"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {/* ── Note body ── */}
      <div className="max-w-3xl mx-auto px-8 py-10 print:px-10 print:py-8">

        {/* Print-only page header */}
        <div className="hidden print:flex items-center justify-between mb-6 pb-3 border-b border-stone-300 text-[10px] text-stone-500">
          <span>TutorIA Física UFSM{primaryDisc ? ` · ${primaryDisc}` : ""}</span>
          <span>{studentEmail} · {dateStr} {timeStr}{currentWeek > 0 ? ` · Semana ${currentWeek}` : ""}</span>
        </div>

        {/* ── Cover ── */}
        <div className="mb-8 rounded-2xl border-2 border-stone-200 bg-gradient-to-br from-indigo-50 to-stone-50 p-6">
          <div className="flex flex-wrap gap-2 mb-3">
            {primaryDisc && (
              <span className="px-2.5 py-1 rounded-full bg-indigo-600 text-white text-xs font-bold tracking-wide">
                {weeklyTopics[0]?.disciplina_codigo}
              </span>
            )}
            {primaryTopic && (
              <span className="px-2.5 py-1 rounded-full bg-stone-800 text-white text-xs font-medium">
                {primaryTopic}
              </span>
            )}
            {currentWeek > 0 && (
              <span className="px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 text-xs font-medium">
                Semana {currentWeek}
              </span>
            )}
          </div>

          <blockquote className="text-xl font-semibold text-stone-900 leading-snug mb-4 border-l-4 border-indigo-400 pl-4">
            {question}
          </blockquote>

          <div className="flex flex-wrap items-center gap-4 text-xs text-stone-500">
            <span>👤 {studentEmail}</span>
            <span>🤖 {model}</span>
            {respSec && <span>⏱ {respSec}s</span>}
            <span>📅 {dateStr} {timeStr}</span>
            <span className="ml-auto font-mono text-stone-400">#{sessionShort}</span>
          </div>
        </div>

        {/* ── Agent sections ── */}
        <div className="space-y-7">
          {agents.map((agent, i) => {
            const meta = AGENT_META[agent.agent_name] ?? {
              icon: "⚙️", label: agent.dimension,
              borderColor: "#6b7280", bgColor: "#f9fafb",
              badgeBg: "bg-stone-100", badgeText: "text-stone-700",
            };
            return (
              <section
                key={agent.agent_name}
                className="rounded-xl overflow-hidden border border-stone-200 print:break-inside-avoid"
                style={{ borderLeftWidth: 4, borderLeftColor: meta.borderColor }}
              >
                {/* Section header */}
                <div
                  className="flex items-center gap-2.5 px-5 py-3"
                  style={{ backgroundColor: meta.bgColor }}
                >
                  <span className="font-mono font-bold text-sm tabular-nums" style={{ color: meta.borderColor }}>
                    {String(i + 1).padStart(2, "0")}.
                  </span>
                  <span className="text-base">{meta.icon}</span>
                  <div className="flex-1">
                    <span className="font-bold text-stone-900 text-sm">{agent.agent_name}</span>
                    <span className={`ml-2 px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wide ${meta.badgeBg} ${meta.badgeText}`}>
                      {meta.label}
                    </span>
                  </div>
                </div>

                {/* Section content */}
                <div className="px-5 py-4 bg-white">
                  <div className="prose prose-sm max-w-none prose-headings:text-stone-800 prose-code:text-[13px] prose-pre:bg-stone-950 prose-pre:text-stone-100">
                    <ReactMarkdown
                      remarkPlugins={[remarkMath]}
                      rehypePlugins={[[rehypeKatex, { throwOnError: false, strict: false }]]}
                    >
                      {normalizeTex(agent.content)}
                    </ReactMarkdown>
                  </div>
                </div>
              </section>
            );
          })}
        </div>

        {/* ── Footer card ── */}
        <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 gap-5 print:break-inside-avoid">

          {/* SM-2 — Conceitos para revisar */}
          {due.length > 0 && (
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
              <p className="text-xs font-bold text-amber-700 uppercase tracking-wide mb-3">
                🔄 Para revisar (SM-2)
              </p>
              <div className="space-y-2">
                {due.slice(0, 6).map((d) => (
                  <MasteryBar key={d.concept_id} mastery={d.mastery_level} label={d.topic} />
                ))}
              </div>
            </div>
          )}

          {/* Weekly curriculum */}
          {weeklyTopics.length > 0 && (
            <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-4">
              <p className="text-xs font-bold text-indigo-700 uppercase tracking-wide mb-3">
                📅 Semana {currentWeek} do semestre UFSM
              </p>
              <ul className="space-y-1.5">
                {weeklyTopics.map((t) => (
                  <li key={t.disciplina_codigo} className="flex items-center justify-between gap-2 text-xs">
                    <span className="text-stone-700 font-medium">{t.disciplina_codigo}</span>
                    <span className="text-stone-600">{t.tema}</span>
                    <span className={`px-1.5 py-0.5 rounded-full text-[10px] font-medium ${
                      t.status === "mastered"   ? "bg-emerald-100 text-emerald-700" :
                      t.status === "developing" ? "bg-yellow-100  text-yellow-700"  :
                                                 "bg-stone-200   text-stone-500"
                    }`}>
                      {t.status === "mastered" ? "✓ dominado" : t.status === "developing" ? `${Math.round(t.mastery_level * 100)}%` : "novo"}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Print-only footer */}
        <div className="hidden print:flex items-center justify-between mt-8 pt-3 border-t border-stone-300 text-[10px] text-stone-400">
          <span>Apostila TutorIA Física UFSM — gerada automaticamente</span>
          <span>Sessão {sessionId ?? "—"}</span>
        </div>

      </div>
    </div>
  );
}
