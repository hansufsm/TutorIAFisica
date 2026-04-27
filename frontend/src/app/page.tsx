'use client';

import { useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface AgentOutput {
  agent_name: string;
  color: string;
  dimension: string;
  content: string;
}

export default function Home() {
  const [question, setQuestion] = useState('');
  const [agents, setAgents] = useState<AgentOutput[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    setLoading(true);
    setError(null);
    setAgents([]);

    try {
      const res = await fetch(`${API_URL}/tutor/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          student_email: 'usuario@ufsm.br',
          student_name: 'Usuário',
          model_name: 'Gemini 3.0 Preview',
        }),
      });

      if (!res.ok) throw new Error('Erro ao enviar pergunta');
      const data = await res.json();
      setAgents(data.agents || []);
      setQuestion('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-2 text-center">🌌 TutorIA Física</h1>
        <p className="text-gray-400 text-center mb-8">
          Mentor inteligente para ensino de física universitária
        </p>

        {/* Agent Responses */}
        <div className="mb-8 space-y-4">
          {agents.length === 0 && !loading && (
            <div className="text-center text-gray-500 py-12">
              <p>Digite uma pergunta de física para começar</p>
            </div>
          )}
          {agents.map((agent, i) => (
            <div
              key={i}
              className="p-4 rounded-lg border-l-4"
              style={{ borderColor: agent.color, backgroundColor: '#1a1a2e' }}
            >
              <h3 className="font-semibold mb-2" style={{ color: agent.color }}>
                {agent.agent_name} — {agent.dimension}
              </h3>
              <p className="text-gray-300 text-sm whitespace-pre-wrap">
                {typeof agent.content === 'string'
                  ? agent.content.substring(0, 500) + (agent.content.length > 500 ? '...' : '')
                  : JSON.stringify(agent.content)}
              </p>
            </div>
          ))}
          {error && (
            <div className="p-4 rounded-lg bg-red-900/30 border border-red-500 text-red-200">
              ⚠️ {error}
            </div>
          )}
          {loading && (
            <div className="text-center py-4">
              <p className="text-gray-400">⏳ Processando... (pode demorar 30s na primeira vez)</p>
            </div>
          )}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ex: O que é força? Como se calcula F=ma?"
            disabled={loading}
            className="flex-1 px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 focus:border-blue-500 outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 font-medium"
          >
            {loading ? '⏳' : 'Perguntar →'}
          </button>
        </form>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-600 text-sm">
          <p>Backend: {API_URL}</p>
          <p>TutorIA Física v2026.2.0 • UFSM</p>
        </div>
      </div>
    </div>
  );
}
