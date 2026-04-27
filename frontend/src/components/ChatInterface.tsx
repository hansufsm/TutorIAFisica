"use client";
import { useState, useRef, useEffect } from "react";
import { AgentPanel } from "./AgentPanel";
import { VoiceInput } from "./VoiceInput";
import { askTutorStream, AgentOutput, DueReview } from "@/lib/api";
import { Zap, Lightbulb, Volume2 } from "lucide-react";

const MODELS = ["DeepSeek Chat", "Gemini 2.0 Flash"];

// SVG Illustration de Física
const PhysicsIllustration = () => (
  <svg className="w-full h-full" viewBox="0 0 400 400" fill="none" xmlns="http://www.w3.org/2000/svg">
    {/* Fundo gradiente círculo */}
    <defs>
      <linearGradient id="physicsGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#4f46e5" stopOpacity="0.1" />
        <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.1" />
      </linearGradient>
    </defs>
    <circle cx="200" cy="200" r="180" fill="url(#physicsGrad)" />

    {/* Átomo */}
    <circle cx="200" cy="200" r="50" stroke="#4f46e5" strokeWidth="2" fill="none" />
    <circle cx="200" cy="200" r="35" stroke="#06b6d4" strokeWidth="2" fill="none" opacity="0.6" />
    <circle cx="200" cy="150" r="8" fill="#ef4444" />
    <circle cx="240" cy="210" r="8" fill="#ef4444" />
    <circle cx="160" cy="210" r="8" fill="#ef4444" />
    <circle cx="200" cy="200" r="12" fill="#4f46e5" />

    {/* Energia/Ondas */}
    <path d="M 100 200 Q 120 180 140 200 T 180 200" stroke="#fbbf24" strokeWidth="2" fill="none" opacity="0.8" />
    <path d="M 220 200 Q 240 180 260 200 T 300 200" stroke="#fbbf24" strokeWidth="2" fill="none" opacity="0.8" />

    {/* Equação E=mc² em estilo minimalista */}
    <text x="200" y="310" fontSize="24" fontWeight="bold" textAnchor="middle" fill="#4f46e5" fontFamily="'Plus Jakarta Sans'">
      E = mc²
    </text>
  </svg>
);

export function ChatInterface() {
  const [question, setQuestion] = useState("");
  const [agents, setAgents] = useState<AgentOutput[]>([]);
  const [loading, setLoading] = useState(false);
  const [streamingAgent, setStreamingAgent] = useState<string | null>(null);
  const [model, setModel] = useState(MODELS[0]);
  const [due, setDue] = useState<DueReview[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [heroVisible, setHeroVisible] = useState(true);
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
    setHeroVisible(false);
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
    <div className="flex flex-col min-h-screen bg-white">
      {/* Header/Nav */}
      <nav className="flex px-6 lg:px-8 bg-white rounded-full mt-4 mx-6 py-3 px-6 shadow-sm items-center justify-between sticky top-4 z-40">
        <div className="flex items-center gap-3">
          <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-indigo-900 text-white">
            <Zap size={20} strokeWidth={3} />
          </div>
          <span className="text-base font-semibold tracking-tight text-slate-900 font-jakarta hidden sm:block">
            TutorIA Física
          </span>
        </div>
        <div className="flex items-center gap-4">
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="text-sm bg-slate-100 border border-slate-300 rounded-full px-4 py-2 text-slate-900 hover:bg-slate-200 transition-colors cursor-pointer font-geist font-medium"
          >
            {MODELS.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
      </nav>

      {/* Hero Section */}
      {heroVisible && agents.length === 0 && (
        <div className="mt-8 grid lg:grid-cols-2 gap-12 items-center container-safe py-12 animate-fade-in">
          {/* Copy */}
          <div className="">
            <h1 className="sm:text-5xl lg:text-6xl text-4xl font-semibold text-slate-900 tracking-tight font-jakarta">
              Acelere seu Aprendizado em Física
            </h1>
            <p className="mt-6 text-lg max-w-lg text-slate-600 font-geist">
              Nosso tutor de IA oferece explicações profundas, soluções matemáticas rigorosas e desafios adaptativos para dominar os conceitos de física universitária.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <div className="flex items-center gap-3">
                <div className="flex-shrink-0 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-100">
                  <Lightbulb className="text-indigo-600" size={20} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-900">Explicações Socráticas</p>
                  <p className="text-xs text-slate-600">Aprenda questionando</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex-shrink-0 flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-100">
                  <Zap className="text-cyan-600" size={20} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-900">Análise em Tempo Real</p>
                  <p className="text-xs text-slate-600">Respostas instantâneas</p>
                </div>
              </div>
            </div>
          </div>

          {/* Illustration */}
          <div className="relative h-[340px] sm:h-[420px] lg:h-[480px] hidden lg:block">
            <PhysicsIllustration />
          </div>
        </div>
      )}

      {/* Conteúdo principal */}
      <div className="flex-1 container-safe py-8">
        {/* Revisões pendentes */}
        {due.length > 0 && (
          <div className="animate-slide-in-up mb-6 p-4 bg-indigo-50 border border-indigo-200 rounded-2xl">
            <div className="flex items-start gap-3">
              <Lightbulb size={20} className="text-indigo-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-semibold text-slate-900 mb-2">📚 Conceitos para revisar:</p>
                <div className="flex flex-wrap gap-2">
                  {due.map((d) => (
                    <span
                      key={d.concept_id}
                      className="px-3 py-1 bg-white border border-indigo-300 text-indigo-700 rounded-full text-xs font-medium"
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
          <div className="animate-slide-in-up mb-6 p-4 bg-red-50 border border-red-200 rounded-2xl text-red-700 text-sm">
            <div className="flex gap-3">
              <span className="flex-shrink-0">⚠️</span>
              <div>{error}</div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Section */}
      <div className="border-t border-slate-200 bg-white py-6 sticky bottom-0">
        <div className="container-safe">
          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <textarea
                ref={textareaRef}
                className="w-full bg-slate-50 border border-slate-300 rounded-2xl p-4 text-sm resize-none
                           placeholder-slate-500 text-slate-900 transition-all focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20
                           max-h-32 font-geist"
                rows={2}
                placeholder="Qual é sua dúvida sobre física? (Ex: Qual é a diferença entre massa e peso?)"
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
                className="px-6 py-3 rounded-full font-semibold text-sm transition-all whitespace-nowrap
                           bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed
                           shadow-sm hover:shadow-md text-white
                           flex items-center justify-center gap-2 min-w-fit font-geist"
              >
                {loading ? (
                  <>
                    <span className="inline-block animate-spin">⟳</span>
                  </>
                ) : (
                  <>
                    <Zap size={18} />
                    Perguntar
                  </>
                )}
              </button>
            </div>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            💡 Use Shift+Enter para quebra de linha
          </p>
        </div>
      </div>
    </div>
  );
}
