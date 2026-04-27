"use client";
import { useState, useRef, useEffect } from "react";
import { AgentPanel } from "./AgentPanel";
import { VoiceInput } from "./VoiceInput";
import { askTutorStream, AgentOutput, DueReview } from "@/lib/api";
import { Menu, Plus, MessageSquare, BookOpen, Search, Zap, Send } from "lucide-react";

const MODELS = ["DeepSeek Chat", "Gemini 2.0 Flash"];

const QUICK_ACTIONS = [
  { icon: "⚛️", label: "Explicar Conceito", desc: "Entenda princípios de física" },
  { icon: "📐", label: "Resolver Problema", desc: "Soluções matemáticas passo a passo" },
  { icon: "📊", label: "Visualizar", desc: "Gráficos e diagramas interativos" },
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
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 100)}px`;
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
    <div className="flex h-screen bg-white">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-200 bg-white flex flex-col p-4 overflow-y-auto">
        {/* Logo */}
        <div className="flex items-center gap-3 mb-8">
          <div className="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center">
            <Zap size={18} className="text-white" strokeWidth={3} />
          </div>
          <span className="font-semibold text-slate-900">TutorIA Física</span>
        </div>

        {/* Menu principal */}
        <nav className="space-y-3 mb-8 flex-1">
          <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg bg-slate-100 text-slate-900 text-sm font-medium hover:bg-slate-200 transition">
            <Plus size={18} />
            Nova pergunta
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg text-slate-700 hover:bg-slate-50 text-sm transition">
            <MessageSquare size={18} />
            Histórico
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg text-slate-700 hover:bg-slate-50 text-sm transition">
            <BookOpen size={18} />
            Biblioteca
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg text-slate-700 hover:bg-slate-50 text-sm transition">
            <Search size={18} />
            Pesquisar
          </button>
        </nav>

        {/* Model selector */}
        <div className="border-t border-slate-200 pt-4">
          <p className="text-xs font-semibold text-slate-500 uppercase mb-3">Modelo</p>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 bg-white text-slate-900 hover:bg-slate-50 cursor-pointer"
          >
            {MODELS.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="border-b border-slate-200 px-8 py-4 flex items-center justify-between bg-white">
          <div>
            <h1 className="text-xl font-semibold text-slate-900">TutorIA Física 1.0</h1>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-slate-100 rounded-lg transition">
              <Menu size={20} className="text-slate-600" />
            </button>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto">
          {!showChat ? (
            /* Welcome State */
            <div className="flex items-center justify-center h-full px-8">
              <div className="max-w-2xl w-full text-center">
                <h2 className="text-5xl font-normal text-slate-900 mb-8" style={{ fontFamily: 'Georgia, serif' }}>
                  O que posso fazer por você?
                </h2>

                {/* Quick Actions Grid */}
                <div className="grid grid-cols-2 gap-4 mb-8">
                  {QUICK_ACTIONS.map((action, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        setQuestion(action.label);
                        setShowChat(true);
                      }}
                      className="p-4 border border-slate-200 rounded-xl hover:border-slate-400 hover:bg-slate-50 transition text-left"
                    >
                      <div className="text-2xl mb-2">{action.icon}</div>
                      <p className="font-medium text-slate-900 text-sm">{action.label}</p>
                      <p className="text-xs text-slate-600 mt-1">{action.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Chat State */
            <div className="px-8 py-8 max-w-3xl mx-auto w-full">
              {/* Revisões */}
              {due.length > 0 && (
                <div className="mb-6 p-4 bg-slate-50 border border-slate-200 rounded-lg">
                  <p className="text-sm font-semibold text-slate-900 mb-3">📚 Conceitos para revisar:</p>
                  <div className="flex flex-wrap gap-2">
                    {due.map((d) => (
                      <span
                        key={d.concept_id}
                        className="px-2.5 py-1 bg-white border border-slate-300 text-slate-700 rounded text-xs font-medium"
                      >
                        {d.concept_id} ({Math.round(d.mastery_level * 100)}%)
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Respostas dos agentes */}
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

              {/* Erro */}
              {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                  <span className="font-medium">Erro:</span> {error}
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-slate-200 bg-white px-8 py-6">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-3">
              <div className="flex-1">
                <textarea
                  ref={textareaRef}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl p-4 text-sm resize-none
                             placeholder-slate-500 text-slate-900 transition-all
                             focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:border-slate-400
                             max-h-24"
                  rows={2}
                  placeholder="Atribua uma tarefa ou pergunte qualquer coisa"
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
                  className="px-4 py-3 rounded-lg bg-slate-900 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed
                             transition text-white flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <span className="inline-block animate-spin">⟳</span>
                  ) : (
                    <Send size={18} />
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
