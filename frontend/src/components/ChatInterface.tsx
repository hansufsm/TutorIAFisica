"use client";
import { useState, useRef, useEffect } from "react";
import { AgentPanel } from "./AgentPanel";
import { VoiceInput } from "./VoiceInput";
import { askTutorStream, AgentOutput, DueReview } from "@/lib/api";
import { Sparkles, BookOpen, Zap } from "lucide-react";

const MODELS = ["DeepSeek Chat", "Gemini 2.0 Flash"];

export function ChatInterface() {
  const [question, setQuestion] = useState("");
  const [agents, setAgents] = useState<AgentOutput[]>([]);
  const [loading, setLoading] = useState(false);
  const [streamingAgent, setStreamingAgent] = useState<string | null>(null);
  const [model, setModel] = useState(MODELS[0]);
  const [due, setDue] = useState<DueReview[]>([]);
  const [error, setError] = useState<string | null>(null);
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
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      {/* Header */}
      <div className="glass border-b border-slate-800/50 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-blue-600 to-violet-600 rounded-lg">
              <Sparkles size={24} className="text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">TutorIA Física</h1>
              <p className="text-xs text-slate-400">UFSM • Mentor Inteligente</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="text-xs bg-slate-800/60 border border-slate-700 rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-700/60 transition-colors cursor-pointer"
            >
              {MODELS.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Banner de revisões pendentes */}
      {due.length > 0 && (
        <div className="animate-slide-in-up glass border-b border-slate-800/50 mx-3 mt-3 px-4 py-3 text-sm text-blue-200">
          <div className="flex items-center gap-3 max-w-5xl mx-auto">
            <BookOpen size={18} className="text-blue-400 flex-shrink-0" />
            <div className="flex-1">
              <p className="font-semibold mb-2">📚 Conceitos para revisar:</p>
              <div className="flex flex-wrap gap-2">
                {due.map((d) => (
                  <span
                    key={d.concept_id}
                    className="px-2 py-1 bg-blue-500/20 border border-blue-500/40 rounded-md text-xs font-medium"
                  >
                    {d.concept_id} ({Math.round(d.mastery_level * 100)}%)
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Respostas dos agentes */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        <div className="max-w-5xl mx-auto">
          {agents.length === 0 && !loading && (
            <div className="h-full flex flex-col items-center justify-center text-center py-12">
              <div className="p-4 bg-gradient-to-br from-blue-500/20 to-violet-500/20 rounded-2xl mb-4">
                <Zap size={32} className="text-blue-400" />
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">
                Bem-vindo ao TutorIA Física
              </h2>
              <p className="text-slate-400 max-w-md">
                Faça uma pergunta sobre física e receba uma análise profunda com explicações, soluções matemáticas e desafios adaptativos.
              </p>
            </div>
          )}
          {agents.map((a, i) => (
            <AgentPanel
              key={i}
              agent={a}
              streaming={streamingAgent === a.agent_name}
            />
          ))}
          {error && (
            <div className="animate-slide-in-up glass border border-red-500/30 bg-red-500/10 rounded-xl p-4 text-red-200 text-sm">
              <div className="flex gap-3">
                <span className="text-lg">⚠️</span>
                <div>{error}</div>
              </div>
            </div>
          )}
        </div>
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="glass border-t border-slate-800/50 px-6 py-6">
        <div className="max-w-5xl mx-auto">
          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <textarea
                ref={textareaRef}
                className="w-full bg-slate-800/60 border border-slate-700 rounded-xl p-4 text-sm resize-none
                           placeholder-slate-500 text-white transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20
                           max-h-32"
                rows={2}
                placeholder="Digite sua pergunta de física e pressione Enter..."
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
            <div className="flex flex-col gap-2">
              <VoiceInput onTranscript={(t) => {
                setQuestion(t);
                autoResizeTextarea();
              }} />
              <button
                onClick={submit}
                disabled={loading || !question.trim()}
                className="px-5 py-3 rounded-xl font-semibold text-sm transition-all whitespace-nowrap
                           bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400
                           disabled:opacity-40 disabled:cursor-not-allowed
                           shadow-lg hover:shadow-xl hover:shadow-blue-500/20 text-white
                           flex items-center justify-center gap-2 min-w-fit"
              >
                {loading ? (
                  <>
                    <span className="inline-block animate-spin">⟳</span>
                    Processando...
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    Perguntar
                  </>
                )}
              </button>
            </div>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            💡 Dica: Use Shift+Enter para quebra de linha
          </p>
        </div>
      </div>
    </div>
  );
}
