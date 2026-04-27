"use client";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { AgentOutput } from "@/lib/api";

const AGENT_COLORS: Record<string, { icon: string; dotColor: string }> = {
  "Intérprete": { icon: "🔵", dotColor: "bg-indigo-500" },
  "Solucionador": { icon: "🟢", dotColor: "bg-emerald-500" },
  "Visualizador": { icon: "🟠", dotColor: "bg-orange-500" },
  "Curador": { icon: "🟣", dotColor: "bg-purple-500" },
  "Avaliador": { icon: "🔴", dotColor: "bg-red-500" },
};

export function AgentPanel({
  agent,
  streaming,
}: {
  agent: AgentOutput;
  streaming?: boolean;
}) {
  const config = AGENT_COLORS[agent.agent_name] || {
    icon: "⚙️",
    dotColor: "bg-slate-500",
  };

  return (
    <div className="animate-slide-in-up border-l-4 border-slate-200 pl-4 py-4">
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <span className="text-lg">{config.icon}</span>
        <h3 className="font-semibold text-slate-900 text-sm">{agent.agent_name}</h3>
        <span className="text-xs text-slate-500">• {agent.dimension}</span>
        {streaming && (
          <span className="text-xs text-slate-500 ml-auto flex items-center gap-1">
            <span className={`w-2 h-2 rounded-full ${config.dotColor} animate-pulse`}></span>
            Gerando...
          </span>
        )}
      </div>

      {/* Content */}
      <div className="prose prose-sm max-w-none text-slate-800
                     prose-p:my-2 prose-p:leading-relaxed
                     prose-headings:font-semibold prose-headings:my-2 prose-headings:text-slate-900
                     prose-a:text-indigo-600 prose-a:underline
                     prose-strong:font-semibold prose-strong:text-slate-900
                     prose-code:bg-slate-100 prose-code:text-slate-900 prose-code:px-2 prose-code:py-1 prose-code:rounded prose-code:text-sm
                     prose-pre:bg-slate-100 prose-pre:border prose-pre:border-slate-200 prose-pre:rounded-lg prose-pre:p-3
                     prose-li:my-1
                     prose-blockquote:border-l-2 prose-blockquote:border-slate-300 prose-blockquote:pl-4 prose-blockquote:text-slate-600">
        <ReactMarkdown
          remarkPlugins={[remarkMath]}
          rehypePlugins={[rehypeKatex]}
        >
          {agent.content}
        </ReactMarkdown>
      </div>
    </div>
  );
}
