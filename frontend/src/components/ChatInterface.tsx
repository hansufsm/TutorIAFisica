"use client";
import { useState } from "react";
import { AgentPanel } from "./AgentPanel";
import { VoiceInput } from "./VoiceInput";
import { askTutorStream, AgentOutput, DueReview } from "@/lib/api";

const MODELS = ["DeepSeek Chat", "Gemini 2.0 Flash"];

export function ChatInterface() {
  const [question, setQuestion] = useState("");
  const [agents, setAgents] = useState<AgentOutput[]>([]);
  const [loading, setLoading] = useState(false);
  const [streamingAgent, setStreamingAgent] = useState<string | null>(null);
  const [model, setModel] = useState(MODELS[0]);
  const [due, setDue] = useState<DueReview[]>([]);
  const [error, setError] = useState<string | null>(null);

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
    <div className="flex flex-col h-screen bg-gray-950 text-white">
      {/* Banner de revisões pendentes */}
      {due.length > 0 && (
        <div className="bg-blue-900/40 border-b border-blue-700 px-6 py-2 text-sm text-blue-200 flex gap-4 items-center">
          <span>📚 {due.length} conceito(s) para revisar:</span>
          {due.map((d) => (
            <span
              key={d.concept_id}
              className="px-2 py-0.5 bg-blue-800 rounded-lg text-xs"
            >
              {d.concept_id} ({Math.round(d.mastery_level * 100)}%)
            </span>
          ))}
        </div>
      )}

      {/* Respostas dos agentes */}
      <div className="flex-1 overflow-y-auto p-6 space-y-1">
        {agents.length === 0 && !loading && (
          <div className="flex items-center justify-center h-full text-gray-600 text-sm">
            Digite uma dúvida de física para começar ↓
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
          <div className="text-red-400 text-sm p-4 bg-red-900/20 rounded-lg">
            ⚠️ {error}
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-gray-800 p-4 bg-gray-950">
        <div className="flex gap-2 items-end max-w-4xl mx-auto">
          <textarea
            className="flex-1 bg-gray-900 rounded-xl p-3 text-sm resize-none
                       border border-gray-700 focus:border-blue-500 outline-none
                       placeholder-gray-600"
            rows={3}
            placeholder="Ex: Qual é a diferença entre massa e peso? Por que objetos caem com a mesma aceleração?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submit();
              }
            }}
          />
          <div className="flex flex-col gap-2">
            <VoiceInput onTranscript={(t) => setQuestion(t)} />
            <button
              onClick={submit}
              disabled={loading || !question.trim()}
              className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500
                         disabled:opacity-40 disabled:cursor-not-allowed
                         font-medium text-sm transition-colors whitespace-nowrap"
            >
              {loading ? "⏳" : "Perguntar →"}
            </button>
          </div>
        </div>
        <div className="flex justify-center mt-2">
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="text-xs bg-gray-800 border border-gray-700 rounded-lg px-3 py-1 text-gray-400"
          >
            {MODELS.map((m) => (
              <option key={m}>{m}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
