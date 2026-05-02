"use client";

import { ConceptStatus } from "@/lib/api";

const SYLLABUS = [
  {
    codigo: "FSC1027",
    nome: "Física I",
    periodo: 1,
    temas: ["Cinemática", "Dinâmica", "Leis de Newton", "Trabalho", "Energia", "Gravitação"],
  },
  {
    codigo: "FSC1028",
    nome: "Física II",
    periodo: 2,
    temas: ["Fluidos", "Oscilações", "Ondas", "Termodinâmica", "Calor"],
  },
  {
    codigo: "FSC1029",
    nome: "Física III",
    periodo: 3,
    temas: ["Eletrostática", "Lei de Coulomb", "Campo Elétrico", "Potencial Elétrico", "Capacitância", "Circuitos", "Magnetismo"],
  },
  {
    codigo: "FSC1030",
    nome: "Física IV",
    periodo: 4,
    temas: ["Óptica", "Interferência", "Difração", "Relatividade", "Física Moderna", "Mecânica Quântica"],
  },
];

function masteryColor(status: ConceptStatus["status"], level: number) {
  if (status === "mastered")   return "bg-emerald-100 border-emerald-300 text-emerald-800";
  if (status === "developing") return level > 0.5
    ? "bg-yellow-100 border-yellow-300 text-yellow-800"
    : "bg-orange-100 border-orange-300 text-orange-800";
  return "bg-stone-100 border-stone-200 text-stone-500";
}

function masteryLabel(status: ConceptStatus["status"], level: number) {
  if (status === "mastered")   return "✓";
  if (status === "developing") return `${Math.round(level * 100)}%`;
  return "";
}

export function KnowledgeMap({ concepts }: { concepts: ConceptStatus[] }) {
  // index concepts by topic (normalized lowercase)
  const byTopic = new Map<string, ConceptStatus>();
  for (const c of concepts) {
    byTopic.set(c.topic.toLowerCase().trim(), c);
  }

  const totalTracked = concepts.length;
  const mastered = concepts.filter((c) => c.status === "mastered").length;
  const developing = concepts.filter((c) => c.status === "developing").length;

  return (
    <div>
      {/* Summary bar */}
      {totalTracked > 0 && (
        <div className="flex gap-4 mb-6 text-sm">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-emerald-400 inline-block" />
            {mastered} dominado{mastered !== 1 ? "s" : ""}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-yellow-400 inline-block" />
            {developing} em progresso
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-stone-300 inline-block" />
            {totalTracked - mastered - developing} não iniciado
          </span>
        </div>
      )}

      {/* Grid por disciplina */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {SYLLABUS.map((disc) => (
          <div key={disc.codigo} className="bg-white rounded-xl border border-stone-200 p-4 shadow-sm">
            <div className="mb-3">
              <p className="text-xs font-bold text-indigo-600 uppercase tracking-wide">{disc.codigo}</p>
              <h3 className="font-semibold text-stone-900 text-sm">{disc.nome}</h3>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {disc.temas.map((tema) => {
                const concept = byTopic.get(tema.toLowerCase().trim());
                const status = concept?.status ?? "not_started";
                const level = concept?.mastery_level ?? 0;
                return (
                  <span
                    key={tema}
                    title={concept ? `${tema}: ${Math.round(level * 100)}% domínio` : `${tema}: não estudado`}
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full border text-xs font-medium cursor-default transition ${masteryColor(status, level)}`}
                  >
                    {tema}
                    {masteryLabel(status, level) && (
                      <span className="opacity-70 text-[10px]">{masteryLabel(status, level)}</span>
                    )}
                  </span>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
