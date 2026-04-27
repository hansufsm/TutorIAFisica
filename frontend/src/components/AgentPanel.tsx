"use client";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { AgentOutput } from "@/lib/api";

const ICONS: Record<string, string> = {
  "Intérprete": "🔵",
  "Solucionador": "🟢",
  "Visualizador": "🟠",
  "Curador": "🟣",
  "Avaliador": "🔴",
};

export function AgentPanel({
  agent,
  streaming,
}: {
  agent: AgentOutput;
  streaming?: boolean;
}) {
  return (
    <div
      className="rounded-xl border p-4 mb-3 bg-gray-900/80 backdrop-blur"
      style={{ borderColor: agent.color + "66" }}
    >
      <div className="flex items-center gap-2 mb-3">
        <span>{ICONS[agent.agent_name] ?? "🤖"}</span>
        <span className="font-semibold text-sm" style={{ color: agent.color }}>
          {agent.agent_name}
        </span>
        <span className="text-xs text-gray-500">— {agent.dimension}</span>
        {streaming && (
          <span className="ml-auto text-xs text-gray-500 animate-pulse">
            ✦ gerando...
          </span>
        )}
      </div>
      <div className="prose prose-invert prose-sm max-w-none text-gray-200">
        <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
          {agent.content}
        </ReactMarkdown>
      </div>
    </div>
  );
}
