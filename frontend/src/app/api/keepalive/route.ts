export async function GET() {
  const url = `${process.env.SUPABASE_URL}/rest/v1/students?limit=1`;
  const res = await fetch(url, {
    headers: { apikey: process.env.SUPABASE_ANON_KEY ?? "" },
  });
  return Response.json({ status: res.status, ok: res.ok });
}
