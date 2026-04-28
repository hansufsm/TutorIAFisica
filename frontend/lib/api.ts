const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function sanitizeError(error: string): string {
  // Remove verbose stack traces, HTML, and technical details
  let msg = error
    .replace(/<[^>]*>/g, "") // Remove HTML tags
    .split("\n")[0] // Get first line only
    .trim();

  // Extract meaningful error from common patterns
  if (msg.includes("429") || msg.includes("rate")) return "Limite de requisições atingido. Tente novamente em alguns segundos.";
  if (msg.includes("401") || msg.includes("authentication")) return "Falha de autenticação na API.";
  if (msg.includes("500")) return "Erro do servidor. Tente novamente.";
  if (msg.includes("DeepSeek") || msg.includes("deepseek")) return "Erro ao conectar com DeepSeek. Usando fallback...";
  if (msg.includes("Gemini") || msg.includes("gemini")) return "Erro ao conectar com Gemini. Tente outro modelo.";

  // Return message if it's reasonable length, otherwise generic message
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
}

export async function askTutorStream(
  req: TutorRequest,
  onAgent: (a: AgentOutput) => void,
  onDone: (due: DueReview[], sessionId?: string, responseTimeMs?: number) => void,
  onError: (e: string) => void
): Promise<void> {
  const res = await fetch(`${API}/tutor/ask/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const errorText = await res.text();
    onError(sanitizeError(errorText));
    return;
  }

  const reader = res.body!.getReader();
  const dec = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    for (const line of dec.decode(value).split("\n")) {
      if (!line.startsWith("data: ")) continue;
      try {
        const data = JSON.parse(line.slice(6));
        if (data.is_final) {
          onDone(data.due_for_review ?? [], data.session_id, data.response_time_ms);
          break;
        }
        if (data.error) {
          onError(sanitizeError(data.error));
          break;
        }
        onAgent(data as AgentOutput);
      } catch (e) {
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
    return ["DeepSeek Chat", "Gemini 2.0 Flash"];
  }
}

export async function getStudentProgress(email: string) {
  const res = await fetch(`${API}/student/${encodeURIComponent(email)}/progress`);
  if (!res.ok) throw new Error(`Failed to fetch progress: ${res.status}`);
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
