"use client";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { AgentOutput } from "@/lib/api";
import {
  Brain, Zap, BarChart3, BookMarked, Target
} from "lucide-react";

const AGENT_CONFIG: Record<string, { icon: React.ReactNode; bgGradient: string; badgeClass: string; labelColor: string }> = {
  "Intérprete": {
    icon: <Brain size={18} />,
    bgGradient: "from-blue-600/10 to-blue-400/5",
    badgeClass: "agent-badge-interpreter",
    labelColor: "text-blue-400",
  },
  "Solucionador": {
    icon: <Zap size={18} />,
    bgGradient: "from-emerald-600/10 to-emerald-400/5",
    badgeClass: "agent-badge-solver",
    labelColor: "text-emerald-400",
  },
  "Visualizador": {
    icon: <BarChart3 size={18} />,
    bgGradient: "from-orange-600/10 to-orange-400/5",
    badgeClass: "agent-badge-visualizer",
    labelColor: "text-orange-400",
  },
  "Curador": {
    icon: <BookMarked size={18} />,
    bgGradient: "from-violet-600/10 to-violet-400/5",
    badgeClass: "agent-badge-curator",
    labelColor: "text-violet-400",
  },
  "Avaliador": {
    icon: <Target size={18} />,
    bgGradient: "from-red-600/10 to-red-400/5",
    badgeClass: "agent-badge-evaluator",
    labelColor: "text-red-400",
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
    icon: <Brain size={18} />,
    bgGradient: "from-slate-600/10 to-slate-400/5",
    badgeClass: "agent-badge-interpreter",
    labelColor: "text-slate-400",
  };

  return (
    <div
      className={`animate-slide-in-up rounded-xl border border-slate-700/50 overflow-hidden backdrop-blur-sm transition-all duration-300 ${
        streaming ? "ring-2 ring-blue-500/40 ring-offset-2 ring-offset-slate-950" : ""
      }`}
      style={{
        background: `linear-gradient(135deg, rgba(15,23,42,0.8), rgba(15,23,42,0.6))`,
      }}
    >
      {/* Header */}
      <div className={`bg-gradient-to-r ${config.bgGradient} border-b border-slate-700/50 px-5 py-3 flex items-center justify-between`}>
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${config.labelColor} bg-slate-800/80`}>
            {config.icon}
          </div>
          <div>
            <h3 className={`font-bold text-sm ${config.labelColor}`}>
              {agent.agent_name}
            </h3>
            <p className="text-xs text-slate-500">
              {agent.dimension}
            </p>
          </div>
        </div>
        {streaming && (
          <div className="flex items-center gap-2 text-xs text-blue-400 animate-pulse-subtle">
            <span className="inline-block w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
            Gerando...
          </div>
        )}
      </div>

      {/* Content */}
      <div className="px-5 py-4">
        <div className="prose prose-invert prose-sm max-w-none
                       prose-headings:font-bold prose-headings:text-white
                       prose-p:text-slate-300 prose-p:leading-relaxed
                       prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline
                       prose-strong:text-slate-100 prose-strong:font-semibold
                       prose-code:bg-slate-800 prose-code:text-amber-300 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded
                       prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-700
                       prose-li:text-slate-300
                       prose-blockquote:border-l-4 prose-blockquote:border-slate-600 prose-blockquote:text-slate-400
                       prose-img:rounded-lg prose-img:border prose-img:border-slate-700">
          <ReactMarkdown
            remarkPlugins={[remarkMath]}
            rehypePlugins={[rehypeKatex]}
            components={{
              img: (props) => (
                <img
                  {...props}
                  className="max-w-full h-auto rounded-lg border border-slate-700 my-3"
                />
              ),
              code: (props) => {
                const { children, className } = props as any;
                const isInline = !className;
                if (isInline) {
                  return (
                    <code className="bg-slate-800 text-amber-300 px-2 py-1 rounded text-xs">
                      {children}
                    </code>
                  );
                }
                return (
                  <pre className="bg-slate-900 border border-slate-700 rounded-lg p-3 overflow-x-auto my-3">
                    <code className={className}>
                      {children}
                    </code>
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
      <div className="px-5 py-2 bg-slate-900/50 border-t border-slate-700/30 flex items-center gap-2">
        <span className={`text-xs font-medium ${config.badgeClass}`}>
          {agent.agent_name}
        </span>
        {streaming && (
          <span className="text-xs text-slate-500">• transmitindo resposta</span>
        )}
      </div>
    </div>
  );
}
