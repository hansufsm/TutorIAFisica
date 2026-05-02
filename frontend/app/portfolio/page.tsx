"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { getStudentPortfolio, PortfolioData } from "@/lib/api";
import { KnowledgeMap } from "@/components/KnowledgeMap";
import { ArrowLeft, Clock, BookOpen, Brain, RefreshCw } from "lucide-react";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("pt-BR", {
    day: "2-digit", month: "short", year: "numeric",
  });
}

function formatTime(ms: number | null) {
  if (!ms) return "—";
  if (ms < 1000) return `${ms} ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

export default function PortfolioPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [data, setData] = useState<PortfolioData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<"mapa" | "sessoes">("mapa");

  useEffect(() => {
    if (authLoading) return;
    if (!user?.email) {
      router.push("/login");
      return;
    }
    setLoading(true);
    getStudentPortfolio(user.email)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [user, authLoading, router]);

  if (authLoading || loading) {
    return (
      <div className="flex h-screen items-center justify-center" style={{ background: "var(--bg-main)" }}>
        <div className="w-6 h-6 rounded-full border-2 border-indigo-400 border-t-transparent animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center" style={{ background: "var(--bg-main)" }}>
        <div className="text-center space-y-3">
          <p className="text-red-600 text-sm">{error}</p>
          <button onClick={() => router.back()} className="text-indigo-600 text-sm underline">Voltar</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ background: "var(--bg-main)" }}>
      <div className="max-w-5xl mx-auto px-6 py-8">

        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link href="/" className="p-2 rounded-lg text-stone-500 hover:bg-stone-100 transition">
            <ArrowLeft size={18} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-stone-900">Caderno de Aprendizagem</h1>
            <p className="text-sm text-stone-500">{user?.email}</p>
          </div>
        </div>

        {/* Stats cards */}
        {data && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
            {[
              { icon: <BookOpen size={16} />, label: "Sessões", value: data.stats.total_sessions, color: "text-indigo-600" },
              { icon: <Brain size={16} />, label: "Conceitos", value: data.stats.total_concepts, color: "text-purple-600" },
              { icon: <span className="text-emerald-600">✓</span>, label: "Dominados", value: data.stats.mastered, color: "text-emerald-600" },
              { icon: <RefreshCw size={16} />, label: "Para revisar", value: data.stats.due_count, color: "text-amber-600" },
            ].map(({ icon, label, value, color }) => (
              <div key={label} className="bg-white rounded-xl border border-stone-200 p-4 shadow-sm">
                <div className={`flex items-center gap-2 mb-1 ${color}`}>{icon}<span className="text-xs font-semibold uppercase tracking-wide">{label}</span></div>
                <p className="text-2xl font-bold text-stone-900">{value}</p>
              </div>
            ))}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-stone-100 rounded-lg p-1 w-fit">
          {(["mapa", "sessoes"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition ${tab === t ? "bg-white shadow-sm text-stone-900" : "text-stone-500 hover:text-stone-700"}`}
            >
              {t === "mapa" ? "🗺️ Mapa de Conhecimento" : "📋 Histórico de Sessões"}
            </button>
          ))}
        </div>

        {/* Mapa de conhecimento */}
        {tab === "mapa" && data && (
          <KnowledgeMap concepts={data.concepts} />
        )}

        {/* Histórico de sessões */}
        {tab === "sessoes" && data && (
          <div className="space-y-3">
            {data.sessions.length === 0 ? (
              <div className="text-center py-16 text-stone-400">
                <p className="text-4xl mb-3">📭</p>
                <p className="text-sm">Nenhuma sessão registrada ainda.</p>
                <Link href="/" className="mt-3 inline-block text-indigo-600 text-sm underline">Fazer primeira pergunta</Link>
              </div>
            ) : (
              data.sessions.map((s) => (
                <div key={s.id} className="bg-white rounded-xl border border-stone-200 p-4 shadow-sm hover:shadow-md transition">
                  <div className="flex items-start justify-between gap-4">
                    <p className="text-stone-800 text-sm font-medium flex-1 leading-snug">{s.question}</p>
                    <div className="flex items-center gap-1.5 text-stone-400 text-xs flex-shrink-0">
                      <Clock size={12} />
                      {formatTime(s.response_time_ms)}
                    </div>
                  </div>
                  <div className="flex items-center gap-3 mt-2">
                    {s.topic && (
                      <span className="px-2 py-0.5 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-700 text-xs">
                        {s.topic}
                      </span>
                    )}
                    <span className="text-xs text-stone-400">{formatDate(s.created_at)}</span>
                    <span className="text-xs text-stone-400">{s.model_used}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

      </div>
    </div>
  );
}
