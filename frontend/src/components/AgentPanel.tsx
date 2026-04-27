"use client";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { AgentOutput } from "@/lib/api";
import { Brain, Zap, BarChart3, BookMarked, Target } from "lucide-react";

const AGENT_CONFIG: Record<string, { icon: React.ReactNode; bgColor: string; borderColor: string; textColor: string; lightBg: string }> = {
  "Intérprete": {
    icon: <Brain size={20} />,
    bgColor: "bg-indigo-600",
    borderColor: "border-indigo-200",
    textColor: "text-indigo-900",
    lightBg: "bg-indigo-50",
  },
  "Solucionador": {
    icon: <Zap size={20} />,
    bgColor: "bg-emerald-600",
    borderColor: "border-emerald-200",
    textColor: "text-emerald-900",
    lightBg: "bg-emerald-50",
  },
  "Visualizador": {
    icon: <BarChart3 size={20} />,
    bgColor: "bg-amber-600",
    borderColor: "border-amber-200",
    textColor: "text-amber-900",
    lightBg: "bg-amber-50",
  },
  "Curador": {
    icon: <BookMarked size={20} />,
    bgColor: "bg-purple-600",
    borderColor: "border-purple-200",
    textColor: "text-purple-900",
    lightBg: "bg-purple-50",
  },
  "Avaliador": {
    icon: <Target size={20} />,
    bgColor: "bg-rose-600",
    borderColor: "border-rose-200",
    textColor: "text-rose-900",
    lightBg: "bg-rose-50",
  },
};

export function AgentPanel({
  agent,
  streaming,
}: {
  agent: AgentOutput;
  streaming?: boolean;
}) {
  const config = AGENT_CONFIG[agent.agent_name] || {
    icon: <Brain size={20} />,
    bgColor: "bg-slate-600",
    borderColor: "border-slate-200",
    textColor: "text-slate-900",
    lightBg: "bg-slate-50",
  };

  return (
    <div
      className={`animate-slide-in-up rounded-2xl border-2 overflow-hidden transition-all duration-300 shadow-sm hover:shadow-md ${config.borderColor} ${config.lightBg}`}
    >
      {/* Header */}
      <div className={`${config.bgColor} text-white px-6 py-4 flex items-center justify-between`}>
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-lg bg-white/20">
            {config.icon}
          </div>
          <div>
            <h3 className="font-jakarta font-bold text-lg">{agent.agent_name}</h3>
            <p className="text-sm text-white/80">{agent.dimension}</p>
          </div>
        </div>
        {streaming && (
          <div className="flex items-center gap-2 text-sm animate-pulse-soft">
            <span className="inline-block w-2 h-2 rounded-full bg-white"></span>
            Gerando...
          </div>
        )}
      </div>

      {/* Content */}
      <div className="px-6 py-5">
        <div
          className="prose prose-sm max-w-none
                     prose-headings:font-jakarta prose-headings:font-bold prose-headings:text-slate-900 prose-headings:mt-4 prose-headings:mb-2
                     prose-p:text-slate-700 prose-p:leading-relaxed prose-p:my-2
                     prose-a:text-indigo-600 prose-a:font-medium prose-a:no-underline hover:prose-a:underline
                     prose-strong:text-slate-900 prose-strong:font-semibold
                     prose-code:bg-slate-200 prose-code:text-slate-900 prose-code:px-2 prose-code:py-1 prose-code:rounded prose-code:font-mono prose-code:text-sm
                     prose-pre:bg-slate-900 prose-pre:text-slate-100 prose-pre:border prose-pre:border-slate-700 prose-pre:rounded-xl
                     prose-li:text-slate-700 prose-li:my-1
                     prose-blockquote:border-l-4 prose-blockquote:border-slate-300 prose-blockquote:text-slate-600 prose-blockquote:italic
                     prose-img:rounded-xl prose-img:border prose-img:border-slate-200 prose-img:my-4 prose-img:shadow-sm"
        >
          <ReactMarkdown
            remarkPlugins={[remarkMath]}
            rehypePlugins={[rehypeKatex]}
            components={{
              img: (props) => (
                <img
                  {...props}
                  className="max-w-full h-auto rounded-xl border border-slate-200 my-4 shadow-sm"
                />
              ),
              code: ({ children, className }) => {
                const isInline = !className;
                if (isInline) {
                  return (
                    <code className="bg-slate-200 text-slate-900 px-2 py-1 rounded font-mono text-sm">
                      {children}
                    </code>
                  );
                }
                return (
                  <pre className="bg-slate-900 text-slate-100 rounded-xl p-4 overflow-x-auto my-4 border border-slate-700 font-mono text-sm">
                    <code className={className}>{children}</code>
                  </pre>
                );
              },
            }}
          >
            {agent.content}
          </ReactMarkdown>
        </div>
      </div>

      {/* Footer */}
      {streaming && (
        <div className={`border-t-2 ${config.borderColor} px-6 py-3 flex items-center gap-2 ${config.lightBg}`}>
          <span className={`text-xs font-semibold ${config.textColor}`}>
            {agent.agent_name} • Transmitindo resposta
          </span>
        </div>
      )}
    </div>
  );
}
