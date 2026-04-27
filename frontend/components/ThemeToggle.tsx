"use client";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const stored = localStorage.getItem("theme") || "dark";
    setTheme(stored as "dark" | "light");
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "dark" ? "light" : "dark";
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    document.documentElement.classList.remove(theme);
    document.documentElement.classList.add(newTheme);
  };

  if (!mounted) return null;

  return (
    <button
      onClick={toggleTheme}
      className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/40 dark:bg-slate-800/40 border border-slate-700/30 dark:border-slate-700/30 hover:border-slate-600/50 dark:hover:border-slate-600/50 transition-all"
      title={`Alternar para tema ${theme === "dark" ? "claro" : "escuro"}`}
    >
      {theme === "dark" ? (
        <>
          <span className="text-lg">☀️</span>
          <span className="text-xs text-slate-400 dark:text-slate-400">Claro</span>
        </>
      ) : (
        <>
          <span className="text-lg">🌙</span>
          <span className="text-xs text-slate-600">Escuro</span>
        </>
      )}
    </button>
  );
}
