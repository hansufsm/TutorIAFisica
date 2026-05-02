"use client";

import { useState } from "react";
import { useAuth } from "@/context/AuthContext";

export default function LoginPage() {
  const { signInWithMagicLink } = useAuth();
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;
    setLoading(true);
    setError(null);
    const { error } = await signInWithMagicLink(email.trim().toLowerCase());
    setLoading(false);
    if (error) {
      setError(error);
    } else {
      setSent(true);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-stone-50 px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8 gap-3">
          <div className="w-12 h-12 rounded-xl bg-indigo-600 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
            ⚛
          </div>
          <div className="text-center">
            <h1 className="text-xl font-semibold text-stone-900">TutorIA Física</h1>
            <p className="text-sm text-stone-500 mt-0.5">UFSM — Acesse com seu email</p>
          </div>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl border border-stone-200 shadow-sm p-6">
          {sent ? (
            <div className="text-center space-y-3">
              <div className="text-4xl">📬</div>
              <h2 className="font-semibold text-stone-900">Link enviado!</h2>
              <p className="text-sm text-stone-500">
                Verifique sua caixa de entrada em{" "}
                <span className="font-medium text-stone-700">{email}</span>.
                Clique no link para entrar.
              </p>
              <button
                onClick={() => { setSent(false); setEmail(""); }}
                className="mt-2 text-xs text-indigo-600 hover:text-indigo-800 underline"
              >
                Usar outro email
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-stone-700 mb-1.5"
                >
                  Email institucional
                </label>
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="aluno@acad.ufsm.br"
                  required
                  className="w-full px-3 py-2.5 rounded-lg border border-stone-300 bg-white text-stone-900 placeholder-stone-400 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400/40 focus:border-indigo-400 transition"
                />
              </div>

              {error && (
                <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                  {error}
                </p>
              )}

              <button
                type="submit"
                disabled={loading || !email.trim()}
                className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium transition-all shadow-sm"
              >
                {loading ? "Enviando…" : "Enviar link de acesso"}
              </button>

              <p className="text-xs text-stone-400 text-center">
                Sem senha — você recebe um link por email.
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
