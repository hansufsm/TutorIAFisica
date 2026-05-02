/**
 * SM-2 Review Reminder — Supabase Edge Function
 *
 * Trigger: Supabase Cron → daily at 08:00 UTC
 * Cron expression: "0 8 * * *"
 *
 * Setup in Supabase Dashboard → Edge Functions → Schedule:
 *   Function: sm2-review-reminder
 *   Schedule: 0 8 * * *
 *
 * Required environment variables (Supabase Dashboard → Settings → Secrets):
 *   SUPABASE_URL       — project URL (auto-injected)
 *   SUPABASE_SERVICE_ROLE_KEY — service role key (auto-injected)
 *   RESEND_API_KEY     — email delivery via Resend (https://resend.com)
 *   FROM_EMAIL         — e.g. "TutorIA <noreply@tutoriafisica.com.br>"
 *   APP_URL            — e.g. "https://tutoriafisica.vercel.app"
 */

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
);

const RESEND_KEY = Deno.env.get("RESEND_API_KEY") ?? "";
const FROM_EMAIL = Deno.env.get("FROM_EMAIL") ?? "TutorIA <noreply@tutoriafisica.com.br>";
const APP_URL    = Deno.env.get("APP_URL") ?? "https://tutoriafisica.vercel.app";

interface DueConcept {
  student_id: string;
  topic: string;
  mastery_level: number;
}

interface Student {
  id: string;
  email: string;
  name: string | null;
}

async function sendEmail(to: string, name: string, concepts: DueConcept[]) {
  if (!RESEND_KEY) {
    console.log(`[skip] RESEND_API_KEY not set — would email ${to}`);
    return;
  }

  const topicList = concepts
    .slice(0, 5)
    .map((c) => `<li><strong>${c.topic}</strong> — ${Math.round(c.mastery_level * 100)}% domínio</li>`)
    .join("\n");

  const firstName = name?.split(" ")[0] ?? "estudante";
  const count = concepts.length;
  const plural = count === 1 ? "conceito precisa" : "conceitos precisam";

  const html = `
    <div style="font-family:sans-serif;max-width:480px;margin:0 auto">
      <h2 style="color:#4f46e5">⏰ Hora de revisar!</h2>
      <p>Olá, <strong>${firstName}</strong>!</p>
      <p>
        Você tem <strong>${count} ${plural}</strong> de revisão agendados no seu Caderno de Aprendizagem:
      </p>
      <ul style="line-height:1.8">${topicList}</ul>
      ${count > 5 ? `<p style="color:#6b7280">... e mais ${count - 5} conceito(s).</p>` : ""}
      <p>
        A revisão espaçada leva apenas <strong>5-10 minutos</strong> e é a forma mais eficiente de consolidar o conteúdo na memória de longo prazo.
      </p>
      <a href="${APP_URL}" style="display:inline-block;margin-top:12px;padding:10px 20px;background:#4f46e5;color:#fff;border-radius:8px;text-decoration:none;font-weight:600">
        Acessar TutorIA e revisar agora
      </a>
      <p style="margin-top:24px;font-size:12px;color:#9ca3af">
        Você recebe este e-mail porque tem uma conta no TutorIA Física - UFSM.<br>
        Para parar de receber, entre em contato conosco.
      </p>
    </div>
  `;

  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${RESEND_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from: FROM_EMAIL,
      to: [to],
      subject: `⏰ Você tem ${count} conceito${count > 1 ? "s" : ""} para revisar hoje`,
      html,
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    console.error(`[email] Failed to send to ${to}: ${err}`);
  } else {
    console.log(`[email] Sent to ${to} — ${count} concepts`);
  }
}

Deno.serve(async () => {
  const now = new Date().toISOString();
  console.log(`[sm2-reminder] Running at ${now}`);

  // Fetch all concepts due for review
  const { data: dueConcepts, error: dueErr } = await supabase
    .from("concept_status")
    .select("student_id, topic, mastery_level")
    .lte("next_review", now)
    .neq("status", "not_started");

  if (dueErr) {
    console.error("[sm2-reminder] Failed to fetch due concepts:", dueErr.message);
    return new Response(JSON.stringify({ error: dueErr.message }), { status: 500 });
  }

  if (!dueConcepts || dueConcepts.length === 0) {
    console.log("[sm2-reminder] No concepts due today.");
    return new Response(JSON.stringify({ sent: 0 }), { status: 200 });
  }

  // Group by student_id
  const byStudent = new Map<string, DueConcept[]>();
  for (const c of dueConcepts as DueConcept[]) {
    const list = byStudent.get(c.student_id) ?? [];
    list.push(c);
    byStudent.set(c.student_id, list);
  }

  // Fetch student emails
  const studentIds = [...byStudent.keys()];
  const { data: students, error: stErr } = await supabase
    .from("students")
    .select("id, email, name")
    .in("id", studentIds);

  if (stErr) {
    console.error("[sm2-reminder] Failed to fetch students:", stErr.message);
    return new Response(JSON.stringify({ error: stErr.message }), { status: 500 });
  }

  let sent = 0;
  for (const student of (students as Student[]) ?? []) {
    const concepts = byStudent.get(student.id) ?? [];
    if (concepts.length === 0) continue;
    await sendEmail(student.email, student.name ?? "", concepts);
    sent++;
  }

  console.log(`[sm2-reminder] Done — emails sent: ${sent}`);
  return new Response(JSON.stringify({ sent, total_due: dueConcepts.length }), { status: 200 });
});
