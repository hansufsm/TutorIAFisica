"use client";
import { useState, useRef, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { AgentPanel } from "./AgentPanel";
import { VoiceInput } from "./VoiceInput";
import { askTutorStream, fetchModels, AgentOutput, DueReview } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import Link from "next/link";
import { Plus, MessageSquare, BookOpen, Settings, Send, PanelLeftClose, PanelLeftOpen, Zap, LogOut } from "lucide-react";

const MODELS_FALLBACK = ["Gemini 2.0 Flash", "DeepSeek Chat"];

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

const AGENTS_ORDER = ["Intérprete", "Solucionador", "Visualizador", "Curador", "Avaliador"];
const QUICK_AGENTS_ORDER = ["Intérprete", "Solucionador"];

const TIMER_RADIUS = 17;
const TIMER_CIRCUMFERENCE = 2 * Math.PI * TIMER_RADIUS;
const DEFAULT_TIMER = 120;
const CANCEL_SHOW_AFTER_MS = 15000;

const AGENT_PIPELINE_STYLES: Record<string, { bg: string; text: string; accent: string }> = {
  "Intérprete":   { bg: "bg-indigo-500",  text: "text-indigo-600",  accent: "bg-indigo-400" },
  "Solucionador": { bg: "bg-emerald-500", text: "text-emerald-600", accent: "bg-emerald-400" },
  "Visualizador": { bg: "bg-orange-500",  text: "text-orange-600",  accent: "bg-orange-400" },
  "Curador":      { bg: "bg-purple-500",  text: "text-purple-600",  accent: "bg-purple-400" },
  "Avaliador":    { bg: "bg-red-500",     text: "text-red-600",     accent: "bg-red-400" },
};

const PHYSICS_FACTS = [
  "A velocidade da luz no vácuo é 299.792.458 m/s — exatamente, por definição do SI.",
  "O princípio de incerteza de Heisenberg: Δx · Δp ≥ ħ/2. Posição e momento não podem ser precisos ao mesmo tempo.",
  "A temperatura do núcleo do Sol é ~15 milhões de kelvin. A superfície, 'apenas' 5.778 K.",
  "Um elétron tem massa 9,109 × 10⁻³¹ kg — cerca de 1/1836 da massa do próton.",
  "O efeito fotoelétrico foi explicado por Einstein em 1905 — e lhe rendeu o Nobel de Física.",
  "Energia cinética média de translação de uma molécula ideal: ½m⟨v²⟩ = (3/2)k_B T.",
  "Na superfície da Lua, g ≈ 1,62 m/s², cerca de 1/6 do campo gravitacional terrestre.",
  "A constante de Planck h = 6,626 × 10⁻³⁴ J·s define a escala do mundo quântico.",
  "Ondas de rádio e raios gama são ambos eletromagnéticos — diferem apenas na frequência.",
  "A pressão atmosférica ao nível do mar equivale ao peso de uma coluna de ~10 m de água.",
  "Numa corrente de 1 A fluem ~6,24 × 10¹⁸ elétrons por segundo.",
  "O teorema trabalho-energia: trabalho líquido sobre um objeto = variação da energia cinética.",
  "A força de Lorentz governa cargas em campos EM: F = q(E + v × B).",
  "Em qualquer colisão em sistema fechado, o momento linear total se conserva.",
  "O índice de refração do vidro óptico varia de ~1,45 a ~1,90 conforme a composição.",
  "O som viaja a ~340 m/s no ar a 20 °C — quase 4× mais rápido na água.",
  "Capacitância de capacitor de placas paralelas: C = ε₀ A / d.",
  "A física clássica é um caso limite da quântica quando a ação do sistema ≫ ħ.",
  "O campo elétrico criado por uma carga puntual cai com 1/r² — lei de Coulomb.",
  "A lei de Faraday: a variação do fluxo magnético induz uma fem ε = −dΦ/dt.",
];

// --- localStorage helpers for timer calibration ---
const TIMER_KEY = (model: string) => `tutoria_timer_${model.replace(/\s/g, "_")}`;
const MAX_SAMPLES = 10;

function saveTimerSample(model: string, ms: number) {
  try {
    const key = TIMER_KEY(model);
    const raw = localStorage.getItem(key);
    const samples: number[] = raw ? JSON.parse(raw) : [];
    samples.push(ms);
    if (samples.length > MAX_SAMPLES) samples.splice(0, samples.length - MAX_SAMPLES);
    localStorage.setItem(key, JSON.stringify(samples));
  } catch { /* ignore */ }
}

function loadTimerEstimate(model: string): number {
  try {
    const raw = localStorage.getItem(TIMER_KEY(model));
    if (!raw) return DEFAULT_TIMER;
    const samples: number[] = JSON.parse(raw);
    if (samples.length === 0) return DEFAULT_TIMER;
    const sorted = [...samples].sort((a, b) => a - b);
    const median = sorted[Math.floor(sorted.length / 2)];
    const estimate = Math.round((median / 1000) * 1.2);
    return Math.max(30, Math.min(180, estimate));
  } catch {
    return DEFAULT_TIMER;
  }
}

export function ChatInterface() {
  const { user, loading: authLoading, signOut } = useAuth();
  const router = useRouter();
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
  const [timeLeft, setTimeLeft] = useState<number>(DEFAULT_TIMER);
  const [quickMode, setQuickMode] = useState(false);
  const [showCancel, setShowCancel] = useState(false);
  const [factIndex, setFactIndex] = useState(0);

  // Guest mode: email is undefined when not authenticated — SM-2 and portfolio won't persist
  const studentEmail = user?.email ?? undefined;

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const timerMaxRef = useRef<number>(DEFAULT_TIMER);
  const abortRef = useRef<AbortController | null>(null);
  const cancelTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const currentModelRef = useRef<string>(MODELS_FALLBACK[0]);

  useEffect(() => {
    fetchModels().then((list) => {
      if (list.length > 0) {
        setModels(list);
        setModel(list[0]);
        currentModelRef.current = list[0];
      }
    });
  }, []);

  useEffect(() => {
    currentModelRef.current = model;
  }, [model]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [agents, loading]);

  // Source hierarchy animation
  useEffect(() => {
    if (!loading) { setActiveSource(0); return; }
    const t = setInterval(() => setActiveSource((s) => (s + 1) % SOURCE_HIERARCHY.length), 900);
    return () => clearInterval(t);
  }, [loading]);

  // Physics facts rotation every 8s while loading
  useEffect(() => {
    if (!loading) return;
    const t = setInterval(() => setFactIndex((i) => (i + 1) % PHYSICS_FACTS.length), 8000);
    return () => clearInterval(t);
  }, [loading]);

  // Countdown timer
  useEffect(() => {
    if (!loading) {
      setTimeLeft(DEFAULT_TIMER);
      timerMaxRef.current = DEFAULT_TIMER;
      return;
    }
    const estimate = loadTimerEstimate(currentModelRef.current);
    timerMaxRef.current = estimate;
    setTimeLeft(estimate);

    const t = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          const nextMax = Math.max(5, Math.round(timerMaxRef.current * 0.85));
          timerMaxRef.current = nextMax;
          return nextMax;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(t);
  }, [loading]);

  // Show cancel button after 15s
  useEffect(() => {
    if (!loading) { setShowCancel(false); return; }
    cancelTimerRef.current = setTimeout(() => setShowCancel(true), CANCEL_SHOW_AFTER_MS);
    return () => {
      if (cancelTimerRef.current) clearTimeout(cancelTimerRef.current);
    };
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

  function printPDF() { window.print(); }

  function requestSend() {
    if (!question.trim() || loading) return;
    setShowConfirm(true);
  }

  function cancelRequest() {
    abortRef.current?.abort();
    abortRef.current = null;
    setLoading(false);
    setStreamingAgent(null);
    setShowCancel(false);
  }

  function switchModel() {
    const idx = models.indexOf(currentModelRef.current);
    const nextModel = models[(idx + 1) % models.length];
    abortRef.current?.abort();
    abortRef.current = null;
    setModel(nextModel);
    currentModelRef.current = nextModel;
    // Re-submit with new model after state settles
    setTimeout(() => doSubmit(nextModel), 50);
  }

  const doSubmit = useCallback(async (overrideModel?: string) => {
    const usedModel = overrideModel ?? currentModelRef.current;
    const ctrl = new AbortController();
    abortRef.current = ctrl;

    setLoading(true);
    setShowChat(true);
    setAgents([]);
    setActiveTab(null);
    setError(null);
    setResponseTime(0);
    setShowCancel(false);
    setFactIndex(Math.floor(Math.random() * PHYSICS_FACTS.length));

    await askTutorStream(
      { question, model_name: usedModel, student_email: studentEmail, quick_mode: quickMode },

      // onToken — append token to agent's partial content
      (agentName, token, color, dimension) => {
        setStreamingAgent(agentName);
        setActiveTab(agentName);
        setAgents((prev) => {
          const idx = prev.findIndex((a) => a.agent_name === agentName);
          if (idx === -1) {
            return [...prev, { agent_name: agentName, color, dimension, content: token }];
          }
          const updated = [...prev];
          updated[idx] = { ...updated[idx], content: updated[idx].content + token };
          return updated;
        });
      },

      // onAgent — replace with final complete content
      (agent) => {
        setStreamingAgent(null);
        setAgents((prev) => {
          const idx = prev.findIndex((a) => a.agent_name === agent.agent_name);
          if (idx === -1) return [...prev, agent];
          const updated = [...prev];
          updated[idx] = agent;
          return updated;
        });
        // Auto-focus first agent tab when Intérprete completes
        if (agent.agent_name === "Intérprete") {
          setActiveTab("Intérprete");
        }
      },

      // onDone
      (dueList, sessionIdFromServer, responseTimeMs) => {
        setDue(dueList);
        setSessionId(sessionIdFromServer ?? null);
        setStreamingAgent(null);
        setLoading(false);
        setShowCancel(false);
        if (responseTimeMs) {
          setResponseTime(responseTimeMs);
          saveTimerSample(usedModel, responseTimeMs);
        }
        setActiveTab(AGENTS_ORDER[0]);
      },

      // onError
      (err) => {
        setError(err);
        setLoading(false);
        setShowCancel(false);
      },

      ctrl.signal,
    );
  }, [question, quickMode, studentEmail]);

  async function confirmAndSubmit() {
    setShowConfirm(false);
    await doSubmit();
  }

  const agentsPipelineOrder = quickMode ? QUICK_AGENTS_ORDER : AGENTS_ORDER;
  const completedAgentNames = new Set(agents.map((a) => a.agent_name));
  const pipelineActive = loading
    ? (agentsPipelineOrder.find((n) => !completedAgentNames.has(n) || n === streamingAgent) ?? null)
    : null;

  return (
    <div className="flex h-screen" style={{ background: "var(--bg-main)" }}>

      {/* Sidebar */}
      <aside className={`${sidebarOpen ? "w-64" : "w-16"} transition-all duration-300 sidebar-bg flex flex-col p-4 overflow-y-auto flex-shrink-0`}>

        {/* Logo + Toggle */}
        <div className={`flex items-center mb-8 ${sidebarOpen ? "gap-3" : "justify-center"}`}>
          {sidebarOpen && (
            <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center flex-shrink-0">
              <span className="text-white text-base">⚛️</span>
            </div>
          )}
          {sidebarOpen && (
            <div className="flex-1 min-w-0">
              <h1 className="font-bold text-stone-900 text-sm leading-tight">TutorIA</h1>
              <p className="text-xs text-stone-500">Física UFSM</p>
            </div>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="flex-shrink-0 text-stone-400 hover:text-stone-700 transition p-1 rounded-lg hover:bg-stone-100"
            title={sidebarOpen ? "Recolher painel" : "Expandir painel"}
          >
            {sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}
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
            {user ? (
              <Link
                href="/portfolio"
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-stone-600 hover:bg-stone-100 text-sm transition"
              >
                <BookOpen size={16} />
                <span>Caderno</span>
              </Link>
            ) : (
              <button
                onClick={() => router.push("/login")}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-stone-400 hover:bg-stone-100 text-sm transition"
                title="Entre para acessar seu caderno"
              >
                <BookOpen size={16} />
                <span>Caderno</span>
              </button>
            )}
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
              disabled={loading}
            >
              {models.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
            <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-stone-400 pointer-events-none text-xs">▾</span>
          </div>
        </div>

        {/* User Info / Login CTA */}
        <div className={`border-t pt-3 mt-3 ${!sidebarOpen ? "hidden" : ""}`} style={{ borderColor: "var(--border)" }}>
          {user ? (
            <>
              <p className="text-xs text-stone-400 truncate mb-1.5" title={user.email}>{user.email}</p>
              <button
                onClick={signOut}
                className="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-stone-500 hover:bg-stone-100 hover:text-stone-700 text-xs transition"
              >
                <LogOut size={13} />
                Sair
              </button>
            </>
          ) : (
            <>
              <p className="text-xs text-stone-400 mb-2">Modo visitante — progresso não salvo.</p>
              <button
                onClick={() => router.push("/login")}
                className="w-full flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium transition"
              >
                Entrar para salvar progresso
              </button>
            </>
          )}
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

              {/* Loading panel */}
              {loading && (
                <div className="animate-fade-in mb-6">
                  <div className="bg-white border rounded-xl p-5 shadow-sm" style={{ borderColor: "var(--border)" }}>

                    {/* Status header with timer */}
                    {(() => {
                      const currentMax = timerMaxRef.current;
                      const timerColor =
                        timeLeft > currentMax * 0.6 ? "#6366f1"
                        : timeLeft > currentMax * 0.2 ? "#f59e0b"
                        : "#ef4444";
                      const arcOffset = TIMER_CIRCUMFERENCE * (1 - timeLeft / currentMax);
                      const urgent = timeLeft <= Math.max(5, Math.round(currentMax * 0.2));
                      return (
                        <div className="flex items-center gap-2.5 mb-5">
                          <div className="w-3 h-3 rounded-full border-2 border-stone-200 border-t-indigo-500 animate-spin flex-shrink-0" />
                          <p className="text-sm text-stone-600 flex-1">
                            {pipelineActive ? (
                              <>
                                <span className={`font-semibold ${AGENT_PIPELINE_STYLES[pipelineActive]?.text ?? "text-stone-800"}`}>
                                  {AGENT_COLORS[pipelineActive]?.icon} {pipelineActive}
                                </span>
                                {" "}está processando…
                              </>
                            ) : agents.length > 0 ? (
                              "Concluindo…"
                            ) : (
                              "Iniciando agentes…"
                            )}
                          </p>

                          {/* Countdown arc */}
                          <div className={`flex flex-col items-center gap-0.5 flex-shrink-0 ${urgent ? "animate-pulse" : ""}`}>
                            <div className="relative w-10 h-10">
                              <svg width="40" height="40" viewBox="0 0 40 40" className="-rotate-90">
                                <circle cx="20" cy="20" r={TIMER_RADIUS} fill="none" stroke="#e7e5e4" strokeWidth="2.5" />
                                <circle
                                  cx="20" cy="20" r={TIMER_RADIUS}
                                  fill="none"
                                  stroke={timerColor}
                                  strokeWidth="2.5"
                                  strokeLinecap="round"
                                  strokeDasharray={TIMER_CIRCUMFERENCE}
                                  strokeDashoffset={arcOffset}
                                  style={{ transition: "stroke-dashoffset 1s linear, stroke 0.5s ease" }}
                                />
                              </svg>
                              <span
                                className="absolute inset-0 flex items-center justify-center text-[11px] font-bold tabular-nums"
                                style={{ color: timerColor, transition: "color 0.5s ease" }}
                              >
                                {timeLeft}
                              </span>
                            </div>
                            <span className="text-[9px] text-stone-400 text-center leading-tight">
                              Resposta<br />esperada em
                            </span>
                          </div>
                        </div>
                      );
                    })()}

                    {/* Agent pipeline nodes */}
                    <div className="flex items-start mb-5 px-1">
                      {agentsPipelineOrder.map((agentName, idx) => {
                        const ps = AGENT_PIPELINE_STYLES[agentName];
                        const ac = AGENT_COLORS[agentName];
                        const isDone = agents.some((a) => a.agent_name === agentName) && streamingAgent !== agentName;
                        const isActive = pipelineActive === agentName || streamingAgent === agentName;
                        return (
                          <div key={agentName} className="flex items-center flex-1">
                            <div className="flex flex-col items-center gap-1.5 flex-shrink-0">
                              <div className="relative w-10 h-10 flex items-center justify-center">
                                {isActive && (
                                  <div className={`absolute inset-0 rounded-full animate-ping opacity-25 ${ps.accent}`} />
                                )}
                                <div className={`
                                  relative z-10 w-9 h-9 rounded-full flex items-center justify-center transition-all duration-500
                                  ${isDone ? `${ps.bg} shadow-sm` : isActive ? `${ps.bg} shadow-lg scale-110` : "bg-stone-100 border-2 border-dashed border-stone-300"}
                                `}>
                                  {isDone
                                    ? <span className="text-white text-xs font-bold">✓</span>
                                    : <span className={`text-sm leading-none ${!isActive ? "opacity-35" : ""}`}>{ac.icon}</span>
                                  }
                                </div>
                              </div>
                              <span className={`text-[10px] font-medium text-center leading-tight w-14 transition-colors duration-300 ${
                                isDone || isActive ? ps.text : "text-stone-400"
                              }`}>
                                {agentName}
                              </span>
                            </div>
                            {idx < agentsPipelineOrder.length - 1 && (
                              <div className="flex-1 h-0.5 mx-1 mb-5 rounded-full bg-stone-100 overflow-hidden">
                                <div
                                  className={`h-full rounded-full transition-all duration-700 ${ps.accent}`}
                                  style={{ width: isDone ? "100%" : "0%" }}
                                />
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>

                    {/* Physics fact */}
                    <div className="border-t pt-3 mb-3" style={{ borderColor: "var(--border)" }}>
                      <p className="text-xs text-stone-500 italic text-center px-2 leading-relaxed transition-all duration-700">
                        💡 {PHYSICS_FACTS[factIndex]}
                      </p>
                    </div>

                    {/* Source cycling — only before first agent arrives */}
                    {!agents.length && (
                      <div className="border-t pt-3 space-y-0.5" style={{ borderColor: "var(--border)" }}>
                        {SOURCE_HIERARCHY.map((src, i) => (
                          <div
                            key={i}
                            className={`flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition-all duration-500 ${
                              activeSource === i ? "bg-indigo-50 border border-indigo-100" : ""
                            }`}
                          >
                            <span className={`text-sm inline-block transition-transform duration-200 ${activeSource === i ? "scale-110" : ""}`}>
                              {src.icon}
                            </span>
                            <span className={`text-xs flex-1 transition-colors ${activeSource === i ? "text-indigo-700 font-medium" : "text-stone-500"}`}>
                              {src.label}
                            </span>
                            {activeSource === i && (
                              <div className="flex gap-0.5 items-center">
                                {[0, 1, 2].map((d) => (
                                  <div
                                    key={d}
                                    className="w-1 h-1 rounded-full bg-indigo-400 animate-bounce"
                                    style={{ animationDelay: `${d * 120}ms` }}
                                  />
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Cancel / Switch model — appears after 15s */}
                    {showCancel && (
                      <div className="border-t pt-3 mt-3 flex gap-2 justify-center" style={{ borderColor: "var(--border)" }}>
                        <button
                          onClick={cancelRequest}
                          className="px-3 py-1.5 rounded-full bg-red-50 hover:bg-red-100 text-red-600 text-xs font-medium border border-red-200 transition active:scale-95"
                        >
                          ✕ Cancelar
                        </button>
                        {models.length > 1 && (
                          <button
                            onClick={switchModel}
                            className="px-3 py-1.5 rounded-full bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-medium border border-indigo-200 transition active:scale-95"
                          >
                            ↻ Trocar modelo
                          </button>
                        )}
                      </div>
                    )}
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
                      const isStreaming = streamingAgent === a.agent_name;
                      return (
                        <button
                          key={a.agent_name}
                          onClick={() => setActiveTab(a.agent_name)}
                          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                            isActive
                              ? `${config.activePill} text-white shadow-sm`
                              : "bg-stone-100 text-stone-600 hover:bg-stone-200 border border-stone-200"
                          } ${isStreaming ? "animate-pulse-soft" : ""}`}
                        >
                          <span className={`w-2 h-2 rounded-full ${config.dotColor}`} />
                          {config.icon} {a.agent_name}
                          {isStreaming && <span className="ml-1 text-[10px] opacity-70">…</span>}
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
                        studentEmail={studentEmail}
                        topic={question.slice(0, 60).trim()}
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
                <p className="text-sm text-stone-800 line-clamp-3 mb-3 leading-relaxed">{question}</p>
                <div className="flex gap-2 flex-wrap">
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
                  {/* Quick mode toggle in confirm */}
                  <button
                    onClick={() => setQuickMode((q) => !q)}
                    className={`ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all active:scale-95 ${
                      quickMode
                        ? "bg-amber-50 text-amber-700 border-amber-300"
                        : "bg-stone-50 text-stone-500 border-stone-200"
                    }`}
                    title="Modo Rápido: apenas Intérprete + Solucionador"
                  >
                    <Zap size={11} />
                    {quickMode ? "Rápido ativo" : "Modo rápido"}
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
                  placeholder="Ex: Uma bola de 2 kg é solta do repouso a 4,3 m de altura na superfície da Lua (g = 1,62 m/s²). Quanto tempo leva para atingir o solo? (Enter para enviar)"
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
            <div className="flex items-center justify-between mt-2">
              <p className="text-xs text-stone-400">
                <kbd className="px-2 py-0.5 bg-stone-100 border border-stone-200 rounded text-stone-500 text-xs">Shift+Enter</kbd> para nova linha
              </p>
              <button
                onClick={() => setQuickMode((q) => !q)}
                className={`flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full border transition-all ${
                  quickMode
                    ? "bg-amber-50 text-amber-700 border-amber-200"
                    : "text-stone-400 border-stone-200 hover:border-stone-300"
                }`}
                title="Modo Rápido: apenas Intérprete + Solucionador (~30s)"
              >
                <Zap size={10} />
                {quickMode ? "Rápido" : "Rápido"}
              </button>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
