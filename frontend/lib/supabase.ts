import { createBrowserClient } from "@supabase/ssr";

// Fallbacks allow SSR/static build to succeed when env vars are not yet configured.
// Auth calls will fail gracefully until real values are set in the deployment dashboard.
export function createSupabaseClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL || "https://placeholder.supabase.co",
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "placeholder-anon-key"
  );
}
