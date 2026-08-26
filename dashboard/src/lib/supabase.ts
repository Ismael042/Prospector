import { createClient } from "@supabase/supabase-js";

export type Lead = {
  id: string;
  place_id: string;
  name: string;
  category: string;
  location: string;
  address: string | null;
  phone: string | null;
  rating: number | null;
  review_count: number | null;
  maps_url: string | null;
  stage: "found" | "contacted" | "replied" | "meeting" | "closed" | "lost";
  created_at: string;
  updated_at: string;
};

export function createSupabaseClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
