const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function sanitizeError(error: string): string {
  let msg = error
    .replace(/<[^>]*>/g, "")
    .split("\n")[0]
    .trim();

  if (msg.includes("429") || msg.includes("rate")) return "Limite de requisições atingido. Tente novamente em alguns segundos.";
  if (msg.includes("401") || msg.includes("authentication")) return "Falha de autenticação na API.";
  if (msg.includes("500")) return "Erro do servidor. Tente novamente.";
  if (msg.includes("DeepSeek") || msg.includes("deepseek")) return "Erro ao conectar com DeepSeek. Usando fallback...";
  if (msg.includes("Gemini") || msg.includes("gemini")) return "Erro ao conectar com Gemini. Tente outro modelo.";

  return msg.length > 150 ? "Erro ao processar sua pergunta. Tente novamente." : msg;
}

export interface AgentOutput {
  agent_name: string;
  color: string;
  dimension: string;
  content: string;
  source_tag?: string;
}

export interface TutorResponse {
  agents: AgentOutput[];
  used_model: string;
  fallback_occurred: boolean;
  due_for_review: DueReview[];
  session_id?: string;
}

export interface DueReview {
  concept_id: string;
  topic: string;
  mastery_level: number;
}

export interface TutorRequest {
  question: string;
  student_email?: string;
  student_name?: string;
  model_name?: string;
  image_base64?: string;
  image_media_type?: string;
  quick_mode?: boolean;
}

/**
 * SSE streaming request.
 * onToken   — called for each token during agent generation (agent_name, token, color, dimension)
 * onAgent   — called when an agent completes with its full content
 * onDone    — called once when the pipeline finishes
 * onError   — called on network or parse errors
 * signal    — optional AbortSignal to cancel mid-stream
 */
export async function askTutorStream(
  req: TutorRequest,
  onToken: (agentName: string, token: string, color: string, dimension: string) => void,
  onAgent: (a: AgentOutput) => void,
  onDone: (due: DueReview[], sessionId?: string, responseTimeMs?: number) => void,
  onError: (e: string) => void,
  signal?: AbortSignal
): Promise<void> {
  let res: Response;
  try {
    res = await fetch(`${API}/tutor/ask/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
      signal,
    });
  } catch (e: unknown) {
    if (e instanceof DOMException && e.name === "AbortError") return;
    onError("Não foi possível conectar ao servidor.");
    return;
  }

  if (!res.ok) {
    const errorText = await res.text();
    onError(sanitizeError(errorText));
    return;
  }

  const reader = res.body!.getReader();
  const dec = new TextDecoder();
  let buffer = "";

  while (true) {
    let done: boolean;
    let value: Uint8Array | undefined;
    try {
      ({ done, value } = await reader.read());
    } catch {
      return; // aborted
    }
    if (done) break;

    buffer += dec.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      try {
        const data = JSON.parse(line.slice(6));

        if (data.is_final) {
          onDone(data.due_for_review ?? [], data.session_id, data.response_time_ms);
          return;
        }
        if (data.error) {
          onError(sanitizeError(data.error));
          return;
        }

        if (data.type === "token") {
          onToken(data.agent_name, data.token, data.color, data.dimension);
        } else if (data.type === "agent_complete") {
          onAgent(data as AgentOutput);
        }
      } catch {
        // skip malformed lines
      }
    }
  }
}

export async function fetchModels(): Promise<string[]> {
  try {
    const res = await fetch(`${API}/models`);
    if (!res.ok) throw new Error();
    const data: Record<string, unknown> = await res.json();
    return Object.keys(data);
  } catch {
    return ["Gemini 2.0 Flash", "DeepSeek Chat"];
  }
}

export async function getStudentProgress(email: string) {
  const res = await fetch(`${API}/student/${encodeURIComponent(email)}/progress`);
  if (!res.ok) throw new Error(`Failed to fetch progress: ${res.status}`);
  return res.json();
}

export interface ConceptStatus {
  concept_id: string;
  topic: string;
  status: "mastered" | "developing" | "not_started";
  mastery_level: number;
  last_reviewed: string | null;
  next_review: string | null;
  date_mastered: string | null;
}

export interface SessionEntry {
  id: string;
  question: string;
  topic: string;
  model_used: string;
  response_time_ms: number | null;
  created_at: string;
}

export interface PortfolioData {
  sessions: SessionEntry[];
  concepts: ConceptStatus[];
  stats: {
    total_sessions: number;
    total_concepts: number;
    mastered: number;
    developing: number;
    due_count: number;
  };
}

export async function getStudentPortfolio(email: string, limit = 30): Promise<PortfolioData> {
  const res = await fetch(
    `${API}/student/${encodeURIComponent(email)}/portfolio?limit=${limit}`
  );
  if (!res.ok) throw new Error(`Failed to fetch portfolio: ${res.status}`);
  return res.json();
}

export async function submitFeedback(
  studentEmail: string,
  conceptId: string,
  topic: string,
  correct: boolean,
  quality: number
) {
  const res = await fetch(`${API}/tutor/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      student_email: studentEmail,
      concept_id: conceptId,
      topic,
      correct,
      quality,
    }),
  });
  if (!res.ok) throw new Error(`Feedback submission failed: ${res.status}`);
}

export async function reportBrokenLink(payload: {
  studentEmail: string;
  sessionId?: string;
  agentName: string;
  url: string;
  note?: string;
}) {
  const res = await fetch(`${API}/tutor/report-link`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      student_email: payload.studentEmail,
      session_id: payload.sessionId,
      agent_name: payload.agentName,
      url: payload.url,
      note: payload.note,
    }),
  });
  if (!res.ok) throw new Error(`Broken link report failed: ${res.status}`);
}
