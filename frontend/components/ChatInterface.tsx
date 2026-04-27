"use client";
import { useState, useRef, useEffect } from "react";
import { AgentPanel } from "./AgentPanel";
import { VoiceInput } from "./VoiceInput";
import { askTutorStream, AgentOutput, DueReview } from "@/lib/api";
import { Menu, X, Plus, MessageSquare, BookOpen, Settings, Send, ChevronDown } from "lucide-react";

const MODELS = ["DeepSeek Chat", "Gemini 2.0 Flash"];

const QUICK_ACTIONS = [
  { icon: "⚛️", label: "Conceito Físico", desc: "Entenda princípios fundamentais" },
  { icon: "📐", label: "Resolver", desc: "Soluções passo a passo" },
  { icon: "📊", label: "Visualizar", desc: "Gráficos e simulações" },
  { icon: "🎯", label: "Desafio", desc: "Teste seu conhecimento" },
];

export function ChatInterface() {
  const [question, setQuestion] = useState("");
  const [agents, setAgents] = useState<AgentOutput[]>([]);
  const [loading, setLoading] = useState(false);
  const [streamingAgent, setStreamingAgent] = useState<string | null>(null);
  const [model, setModel] = useState(MODELS[0]);
  const [due, setDue] = useState<DueReview[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [showChat, setShowChat] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [agents, loading]);

  const autoResizeTextarea = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  async function submit() {
    if (!question.trim() || loading) return;
    setLoading(true);
    setShowChat(true);
    setAgents([]);
    setError(null);

    await askTutorStream(
      {
        question,
        model_name: model,
        student_email: "aluno@ufsm.br",
      },
      (agent) => {
        setStreamingAgent(agent.agent_name);
        setAgents((prev) => [...prev, agent]);
      },
      (dueList) => {
        setDue(dueList);
        setStreamingAgent(null);
        setLoading(false);
      },
      (err) => {
        setError(err);
        setLoading(false);
      }
    );
  }

  return (
    <div className="flex h-screen bg-slate-950">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-20"
        } transition-all duration-300 border-r border-slate-700/50 glass flex flex-col p-4 overflow-y-auto`}
      >
        {/* Logo + Toggle */}
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-600 to-cyan-500 flex items-center justify-center flex-shrink-0">
            <span className="text-white font-bold">⚛️</span>
          </div>
          {sidebarOpen && (
            <div className="flex-1">
              <h1 className="font-bold text-slate-50">TutorIA</h1>
              <p className="text-xs text-slate-400">Física</p>
            </div>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg text-slate-400 hover:bg-slate-800/30 transition flex-shrink-0"
            title={sidebarOpen ? "Fechar" : "Abrir"}
          >
            {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>

        {/* Nav Items */}
        {sidebarOpen && (
          <nav className="space-y-2 mb-8 flex-1">
            <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-gradient-to-r from-indigo-600/20 to-indigo-600/10 text-indigo-300 text-sm font-medium transition hover:bg-gradient-to-r hover:from-indigo-600/30 hover:to-indigo-600/20 border border-indigo-500/20">
              <Plus size={18} />
              <span>Nova Conversa</span>
            </button>
            <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-slate-400 hover:bg-slate-800/30 text-sm transition">
              <MessageSquare size={18} />
              <span>Histórico</span>
            </button>
            <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-slate-400 hover:bg-slate-800/30 text-sm transition">
              <BookOpen size={18} />
              <span>Biblioteca</span>
            </button>
          </nav>
        )}

        {/* Model Selector */}
        <div className={`border-t border-slate-700/30 pt-4 ${!sidebarOpen && "text-center"}`}>
          {sidebarOpen && <p className="text-xs font-semibold text-slate-400 uppercase mb-3">Modelo</p>}
          <div className="relative">
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full text-sm btn-secondary appearance-none pr-8"
            >
              {MODELS.map((m) => (
                <option key={m} value={m}>
                  {sidebarOpen ? m : m.split(" ")[0]}
                </option>
              ))}
            </select>
            {sidebarOpen && <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="border-b border-slate-700/30 px-8 py-4 glass-sm flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-50">TutorIA Física 1.0</h1>
            <p className="text-xs text-slate-400">Mentor inteligente para ensino de física</p>
          </div>
          <div className="flex items-center gap-3">
            <button className="p-2 rounded-lg text-slate-400 hover:bg-slate-800/30 transition">
              <Settings size={20} />
            </button>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto px-8 py-8">
          {!showChat ? (
            /* Welcome State */
            <div className="h-full flex items-center justify-center">
              <div className="max-w-3xl w-full">
                {/* Hero Section */}
                <div className="text-center mb-12 animate-fade-in">
                  <div className="inline-block mb-6">
                    <div className="text-6xl">⚛️</div>
                  </div>
                  <h2 className="text-5xl font-bold text-slate-50 mb-4">
                    Bem-vindo ao <span className="gradient-text">TutorIA</span>
                  </h2>
                  <p className="text-lg text-slate-400 mb-8">
                    Seu mentor inteligente para dominar Física. Conceitos, soluções e desafios.
                  </p>
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-2 gap-4">
                  {QUICK_ACTIONS.map((action, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        setQuestion(action.label);
                        submit();
                      }}
                      className="group p-6 rounded-xl glass hover:glass border-slate-600/30 hover:border-indigo-500/50 transition-all duration-300 text-left hover:shadow-lg hover:shadow-indigo-500/10 active:scale-95"
                    >
                      <div className="text-3xl mb-3 group-hover:scale-110 transition">{action.icon}</div>
                      <h3 className="font-semibold text-slate-50 mb-1">{action.label}</h3>
                      <p className="text-sm text-slate-400">{action.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Chat State */
            <div className="max-w-2xl mx-auto w-full">
              {/* Due Reviews */}
              {due.length > 0 && (
                <div className="mb-6 p-4 glass rounded-lg border border-slate-600/20 animate-slide-in-up">
                  <p className="text-sm font-semibold text-slate-50 mb-3">📚 Para revisar:</p>
                  <div className="flex flex-wrap gap-2">
                    {due.map((d) => (
                      <span
                        key={d.concept_id}
                        className="px-3 py-1 bg-slate-700/30 border border-slate-600/30 text-slate-300 rounded text-xs font-medium"
                      >
                        {d.concept_id} • {Math.round(d.mastery_level * 100)}%
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Agents */}
              {agents.length > 0 && (
                <div className="space-y-4 mb-8">
                  {agents.map((a, i) => (
                    <AgentPanel
                      key={i}
                      agent={a}
                      streaming={streamingAgent === a.agent_name}
                    />
                  ))}
                </div>
              )}

              {/* Error */}
              {error && (
                <div className="fixed bottom-20 left-1/2 -translate-x-1/2 max-w-md z-50 animate-slide-in-up">
                  <div className="p-3 rounded-lg bg-red-950/80 border border-red-500/30 text-red-200 text-sm flex items-start gap-3 shadow-lg backdrop-blur">
                    <span className="text-lg flex-shrink-0">⚠️</span>
                    <div className="flex-1">
                      <p className="font-medium text-red-100">Erro</p>
                      <p className="text-red-300 text-xs mt-1">{error}</p>
                    </div>
                    <button
                      onClick={() => setError(null)}
                      className="flex-shrink-0 text-red-400 hover:text-red-300 transition"
                      title="Fechar"
                    >
                      <X size={16} />
                    </button>
                  </div>
                </div>
              )}

              {loading && !agents.length && (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <div className="inline-block w-8 h-8 rounded-full border-2 border-slate-700 border-t-indigo-500 animate-spin mb-4"></div>
                    <p className="text-slate-400">Processando sua pergunta...</p>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-slate-700/30 glass-sm px-8 py-6">
          <div className="max-w-2xl mx-auto">
            <div className="flex gap-3">
              <div className="flex-1">
                <textarea
                  ref={textareaRef}
                  className="w-full bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-sm resize-none placeholder-slate-500 text-slate-50 transition-all backdrop-blur focus:outline-none focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/20 focus:bg-slate-800/80 max-h-32"
                  rows={2}
                  placeholder="Pergunte qualquer coisa sobre Física... (Shift+Enter para quebra de linha)"
                  value={question}
                  onChange={(e) => {
                    setQuestion(e.target.value);
                    autoResizeTextarea();
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      submit();
                    }
                  }}
                />
              </div>
              <div className="flex flex-col gap-2 justify-end">
                <VoiceInput onTranscript={(t) => {
                  setQuestion(t);
                  autoResizeTextarea();
                }} />
                <button
                  onClick={submit}
                  disabled={loading || !question.trim()}
                  className="btn-primary p-3 flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <span className="inline-block animate-spin">⟳</span>
                  ) : (
                    <Send size={18} />
                  )}
                </button>
              </div>
            </div>
            <p className="text-xs text-slate-500 mt-2 text-center">Pressione <kbd className="px-2 py-1 bg-slate-800 rounded text-slate-400">Shift+Enter</kbd> para nova linha</p>
          </div>
        </div>
      </main>
    </div>
  );
}
