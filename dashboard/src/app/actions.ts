"use server";

import { env } from "cloudflare:workers";
import { revalidatePath } from "next/cache";
import { createClient } from "@/lib/supabase/server";
import { slugify } from "@/lib/slug";

const PREVIEW_BASE_URL = "https://preview.isdev.online";

export async function publishPreview(leadId: string, leadName: string) {
  const supabase = await createClient();

  const { data: lead, error: fetchError } = await supabase
    .from("leads")
    .select("landing_html")
    .eq("id", leadId)
    .single();

  if (fetchError) throw fetchError;
  if (!lead?.landing_html) {
    throw new Error("Esse lead ainda não tem mockup gerado (rode o generate.py primeiro).");
  }

  const slug = slugify(leadName);

  await env.PREVIEWS.put(slug, lead.landing_html, {
    httpMetadata: { contentType: "text/html; charset=utf-8" },
  });

  const { error: updateError } = await supabase
    .from("leads")
    .update({ preview_published: true, preview_url: `${PREVIEW_BASE_URL}/${slug}` })
    .eq("id", leadId);

  if (updateError) throw updateError;

  revalidatePath("/");
}

export async function unpublishPreview(leadId: string, leadName: string) {
  const supabase = await createClient();
  const slug = slugify(leadName);

  await env.PREVIEWS.delete(slug);

  const { error } = await supabase
    .from("leads")
    .update({ preview_published: false, preview_url: null })
    .eq("id", leadId);

  if (error) throw error;

  revalidatePath("/");
}
