const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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
  onDone: (due: DueReview[]) => void,
  onError: (e: string) => void
): Promise<void> {
  const res = await fetch(`${API}/tutor/ask/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    onError(await res.text());
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
          onDone(data.due_for_review ?? []);
          break;
        }
        if (data.error) {
          onError(data.error);
          break;
        }
        onAgent(data as AgentOutput);
      } catch (e) {
        // skip malformed lines
      }
    }
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
