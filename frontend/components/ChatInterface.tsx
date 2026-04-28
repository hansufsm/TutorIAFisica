"use client";
import { useState, useRef, useEffect } from "react";
import { AgentPanel } from "./AgentPanel";
import { VoiceInput } from "./VoiceInput";
import { askTutorStream, fetchModels, AgentOutput, DueReview } from "@/lib/api";
import { Plus, MessageSquare, BookOpen, Settings, Send, ChevronDown } from "lucide-react";

const MODELS_FALLBACK = ["DeepSeek Chat", "Gemini 2.0 Flash"];

const AGENT_COLORS: Record<string, { icon: string; dotColor: string; activePill: string }> = {
  "Intérprete":   { icon: "🔵", dotColor: "bg-indigo-400",  activePill: "bg-indigo-600" },
  "Solucionador": { icon: "🟢", dotColor: "bg-emerald-400", activePill: "bg-emerald-600" },
  "Visualizador": { icon: "🟠", dotColor: "bg-orange-400",  activePill: "bg-orange-600" },
  "Curador":      { icon: "🟣", dotColor: "bg-purple-400",  activePill: "bg-purple-600" },
  "Avaliador":    { icon: "🔴", dotColor: "bg-red-400",     activePill: "bg-red-600" },
};

const SOURCE_HIERARCHY = [
  { icon: "📝", label: "Notas de Aula",           desc: "Material direto do professor" },
  { icon: "📚", label: "Documentos da Disciplina", desc: "Apostilas e slides adotados" },
  { icon: "🏛️", label: "Ementa UFSM",             desc: "Conteúdo programático oficial" },
  { icon: "🌐", label: "Portais Acadêmicos",       desc: "Repositórios .edu.br" },
  { icon: "🤖", label: "Complementação de IA",     desc: "Síntese e enriquecimento" },
];

export function ChatInterface() {
  const [question, setQuestion] = useState("");
  const [agents, setAgents] = useState<AgentOutput[]>([]);
  const [loading, setLoading] = useState(false);
  const [streamingAgent, setStreamingAgent] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [models, setModels] = useState<string[]>(MODELS_FALLBACK);
  const [model, setModel] = useState(MODELS_FALLBACK[0]);
  const [due, setDue] = useState<DueReview[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [showChat, setShowChat] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showConfirm, setShowConfirm] = useState(false);
  const [activeSource, setActiveSource] = useState(0);
  const [responseTime, setResponseTime] = useState<number>(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const startTimeRef = useRef<number>(0);

  useEffect(() => {
    fetchModels().then((list) => {
      if (list.length > 0) {
        setModels(list);
        setModel(list[0]);
      }
    });
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [agents, loading]);

  // Animate source hierarchy while loading
  useEffect(() => {
    if (!loading) { setActiveSource(0); return; }
    const t = setInterval(() => {
      setActiveSource((s) => (s + 1) % SOURCE_HIERARCHY.length);
    }, 900);
    return () => clearInterval(t);
  }, [loading]);

  const autoResizeTextarea = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  function downloadMarkdown() {
    const lines = [`# TutorIA Física\n\n**Pergunta:** ${question}\n`];
    for (const a of agents) {
      lines.push(`\n## ${a.agent_name} (${a.dimension})\n\n${a.content}`);
    }
    const blob = new Blob([lines.join('\n')], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const el = document.createElement('a');
    el.href = url;
    el.download = `tutoria_${Date.now()}.md`;
    el.click();
    URL.revokeObjectURL(url);
  }

  function printPDF() {
    window.print();
  }

  // Step 1: show confirmation
  function requestSend() {
    if (!question.trim() || loading) return;
    setShowConfirm(true);
  }

  // Step 2: confirmed → actually send
  async function confirmAndSubmit() {
    setShowConfirm(false);
    setLoading(true);
    setShowChat(true);
    setAgents([]);
    setActiveTab(null);
    setError(null);
    setResponseTime(0);
    startTimeRef.current = Date.now();

    await askTutorStream(
      { question, model_name: model, student_email: "aluno@ufsm.br" },
      (agent) => {
        setStreamingAgent(agent.agent_name);
        setActiveTab(agent.agent_name);
        setAgents((prev) => [...prev, agent]);
      },
      (dueList, sessionIdFromServer, responseTimeMs) => {
        setDue(dueList);
        setSessionId(sessionIdFromServer ?? null);
        setStreamingAgent(null);
        setLoading(false);
        if (responseTimeMs) setResponseTime(responseTimeMs);
      },
      (err) => {
        setError(err);
        setLoading(false);
      }
    );
  }

  return (
    <div className="flex h-screen" style={{ background: "var(--bg-main)" }}>

      {/* Sidebar */}
      <aside className={`${sidebarOpen ? "w-64" : "w-16"} transition-all duration-300 sidebar-bg flex flex-col p-4 overflow-y-auto flex-shrink-0`}>

        {/* Logo + Toggle */}
        <div className="flex items-center gap-3 mb-8">
          <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center flex-shrink-0">
            <span className="text-white text-base">⚛️</span>
          </div>
          {sidebarOpen && (
            <div className="flex-1 min-w-0">
              <h1 className="font-bold text-stone-900 text-sm leading-tight">TutorIA</h1>
              <p className="text-xs text-stone-500">Física UFSM</p>
            </div>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="flex-shrink-0 text-xs font-mono font-bold text-stone-400 hover:text-stone-700 transition px-1"
            title={sidebarOpen ? "Recolher" : "Expandir"}
          >
            {sidebarOpen ? "«" : "»"}
          </button>
        </div>

        {/* Nav */}
        {sidebarOpen && (
          <nav className="space-y-1 mb-8 flex-1">
            <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-100 text-sm font-medium transition">
              <Plus size={16} />
              <span>Nova Conversa</span>
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-stone-600 hover:bg-stone-100 text-sm transition">
              <MessageSquare size={16} />
              <span>Histórico</span>
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-stone-600 hover:bg-stone-100 text-sm transition">
              <BookOpen size={16} />
              <span>Biblioteca</span>
            </button>
          </nav>
        )}

        {/* Model Selector */}
        <div className={`border-t pt-4 space-y-2 ${!sidebarOpen ? "hidden" : ""}`} style={{ borderColor: "var(--border)" }}>
          <p className="text-xs font-semibold text-stone-400 uppercase tracking-wider">Modelo</p>
          <div className="relative">
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full text-sm appearance-none pr-7 py-2 px-3 rounded-lg border text-stone-800 bg-white"
              style={{ borderColor: "var(--border)" }}
            >
              {models.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
            <ChevronDown size={13} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-stone-400 pointer-events-none" />
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col overflow-hidden">

        {/* Header */}
        <header className="glass-sm px-8 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-stone-900">TutorIA Física 1.0</h1>
            <p className="text-xs text-stone-500">Mentor inteligente para ensino de física — UFSM</p>
          </div>
          <button className="p-2 rounded-lg text-stone-400 hover:bg-stone-100 transition">
            <Settings size={19} />
          </button>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto px-8 py-8">
          {!showChat ? (

            /* Welcome */
            <div className="h-full flex items-center justify-center">
              <div className="max-w-lg w-full text-center animate-fade-in">
                <div className="text-5xl mb-5">⚛️</div>
                <h2 className="text-4xl font-bold text-stone-900 mb-3">
                  Bem-vindo ao <span className="gradient-text">TutorIA</span>
                </h2>
                <p className="text-stone-500 text-base">
                  Seu mentor inteligente para dominar Física universitária.
                  <br />Digite sua dúvida abaixo para começar.
                </p>
              </div>
            </div>

          ) : (

            /* Chat */
            <div className="max-w-2xl mx-auto w-full">

              {/* Due Reviews */}
              {due.length > 0 && (
                <div className="mb-6 p-4 bg-white border rounded-xl animate-slide-in-up" style={{ borderColor: "var(--border)" }}>
                  <p className="text-xs font-semibold text-stone-700 mb-2">📚 Para revisar:</p>
                  <div className="flex flex-wrap gap-2">
                    {due.map((d) => (
                      <span key={d.concept_id} className="px-3 py-1 bg-stone-100 border text-stone-700 rounded-full text-xs font-medium" style={{ borderColor: "var(--border)" }}>
                        {d.concept_id} · {Math.round(d.mastery_level * 100)}%
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Source Hierarchy Loading Card */}
              {loading && !agents.length && (
                <div className="animate-fade-in mb-8">
                  <div className="bg-white border rounded-xl p-5 shadow-sm" style={{ borderColor: "var(--border)" }}>
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-4 h-4 rounded-full border-2 border-stone-200 border-t-indigo-500 animate-spin flex-shrink-0" />
                      <p className="text-sm font-semibold text-stone-800">Consultando Fontes</p>
                    </div>
                    <div className="space-y-1">
                      {SOURCE_HIERARCHY.map((src, i) => (
                        <div
                          key={i}
                          className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors duration-500 ${
                            activeSource === i ? "bg-indigo-50 border border-indigo-100" : "bg-transparent"
                          }`}
                        >
                          <span className="text-base leading-none">{src.icon}</span>
                          <div className="flex-1 min-w-0">
                            <p className={`text-xs font-medium transition-colors ${activeSource === i ? "text-indigo-700" : "text-stone-600"}`}>
                              {src.label}
                            </p>
                            <p className="text-xs text-stone-400 truncate">{src.desc}</p>
                          </div>
                          {activeSource === i && (
                            <span className="text-xs text-indigo-500 animate-pulse-soft font-medium">Buscando…</span>
                          )}
                        </div>
                      ))}
                    </div>
                    {/* Priority flow indicator */}
                    <div className="mt-4 pt-3 border-t" style={{ borderColor: "var(--border)" }}>
                      <p className="text-xs text-stone-400 text-center">Prioridade: Notas → Disciplina → Ementa → Web → IA</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Agent Tabs */}
              {agents.length > 0 && (
                <>
                  <div className="flex gap-2 flex-wrap mb-4 items-center">
                    {agents.map((a) => {
                      const config = AGENT_COLORS[a.agent_name] || { icon: "⚙️", dotColor: "bg-stone-400", activePill: "bg-stone-600" };
                      const isActive = activeTab === a.agent_name;
                      return (
                        <button
                          key={a.agent_name}
                          onClick={() => setActiveTab(a.agent_name)}
                          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                            isActive
                              ? `${config.activePill} text-white shadow-sm`
                              : "bg-stone-100 text-stone-600 hover:bg-stone-200 border border-stone-200"
                          } ${streamingAgent === a.agent_name ? "animate-pulse-soft" : ""}`}
                        >
                          <span className={`w-2 h-2 rounded-full ${config.dotColor}`} />
                          {config.icon} {a.agent_name}
                        </button>
                      );
                    })}
                    {responseTime > 0 && !loading && (
                      <span className="text-xs text-stone-400 ml-auto">⏱ {(responseTime / 1000).toFixed(1)}s</span>
                    )}
                    {!loading && (
                      <div className="ml-auto flex gap-1.5">
                        <button
                          onClick={downloadMarkdown}
                          className="px-2.5 py-1.5 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-600 text-xs font-medium transition-all border border-stone-200"
                          title="Download as Markdown"
                        >
                          📄 .md
                        </button>
                        <button
                          onClick={printPDF}
                          className="px-2.5 py-1.5 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-600 text-xs font-medium transition-all border border-stone-200"
                          title="Print as PDF"
                        >
                          🖨️ PDF
                        </button>
                      </div>
                    )}
                  </div>

                  {activeTab && (
                    <div className="mb-8 animate-slide-in-up">
                      <AgentPanel
                        agent={agents.find((a) => a.agent_name === activeTab)!}
                        streaming={streamingAgent === activeTab}
                        sessionId={sessionId}
                        studentEmail="aluno@ufsm.br"
                      />
                    </div>
                  )}
                </>
              )}

              {/* Error Toast */}
              {error && (
                <div className="fixed bottom-24 left-1/2 -translate-x-1/2 max-w-sm z-50 animate-slide-in-up">
                  <div className="px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-start gap-3 shadow-md">
                    <span className="flex-shrink-0">⚠️</span>
                    <p className="flex-1">{error}</p>
                    <button onClick={() => setError(null)} className="flex-shrink-0 text-red-400 hover:text-red-600 transition font-bold">×</button>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="relative glass-sm px-8 py-5">

          {/* Confirmation overlay */}
          {showConfirm && (
            <div className="absolute bottom-full left-0 right-0 px-8 pb-2 z-20 animate-slide-in-up">
              <div className="max-w-2xl mx-auto bg-white border rounded-xl p-4 shadow-lg" style={{ borderColor: "var(--border)" }}>
                <p className="text-xs font-semibold text-stone-500 uppercase tracking-wide mb-1">Confirmar envio</p>
                <p className="text-sm text-stone-800 line-clamp-3 mb-3 leading-relaxed">
                  {question}
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={confirmAndSubmit}
                    className="px-4 py-1.5 rounded-full bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium transition-all active:scale-95"
                  >
                    ✓ Enviar
                  </button>
                  <button
                    onClick={() => setShowConfirm(false)}
                    className="px-4 py-1.5 rounded-full bg-stone-100 hover:bg-stone-200 text-stone-700 text-sm font-medium transition-all border border-stone-200 active:scale-95"
                  >
                    ← Editar
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="max-w-2xl mx-auto">
            <div className="flex gap-3">
              <div className="flex-1">
                <textarea
                  ref={textareaRef}
                  className="w-full rounded-xl px-4 py-3 text-sm resize-none max-h-32 border focus:outline-none focus:ring-2 focus:ring-indigo-400/30 text-stone-900 placeholder-stone-400 bg-white"
                  style={{ borderColor: "var(--border)" }}
                  rows={2}
                  placeholder="Pergunte qualquer coisa sobre Física… (Enter para enviar)"
                  value={question}
                  onChange={(e) => { setQuestion(e.target.value); autoResizeTextarea(); }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      requestSend();
                    }
                  }}
                />
              </div>
              <div className="flex flex-col gap-2 justify-end">
                <VoiceInput onTranscript={(t) => { setQuestion(t); autoResizeTextarea(); }} />
                <button
                  onClick={requestSend}
                  disabled={loading || !question.trim()}
                  className="btn-primary p-3"
                >
                  {loading
                    ? <span className="inline-block animate-spin text-base">⟳</span>
                    : <Send size={17} />}
                </button>
              </div>
            </div>
            <p className="text-xs text-stone-400 mt-2 text-center">
              <kbd className="px-2 py-0.5 bg-stone-100 border border-stone-200 rounded text-stone-500 text-xs">Shift+Enter</kbd> para nova linha
            </p>
          </div>
        </div>

      </main>
    </div>
  );
}
