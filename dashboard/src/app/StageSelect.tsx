"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { createSupabaseClient, type Lead } from "@/lib/supabase";
import { STAGE_LABELS, STAGE_ORDER } from "@/lib/stages";

export function StageSelect({ leadId, stage }: { leadId: string; stage: Lead["stage"] }) {
  const router = useRouter();
  const [pending, setPending] = useState(false);

  async function handleChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const next = e.target.value as Lead["stage"];
    setPending(true);
    const supabase = createSupabaseClient();
    await supabase.from("leads").update({ stage: next }).eq("id", leadId);
    setPending(false);
    router.refresh();
  }

  return (
    <select
      defaultValue={stage}
      onChange={handleChange}
      disabled={pending}
      className="rounded border border-neutral-300 bg-white px-2 py-1.5 text-sm text-neutral-800 disabled:opacity-50"
    >
      {STAGE_ORDER.map((s) => (
        <option key={s} value={s}>
          {STAGE_LABELS[s]}
        </option>
      ))}
    </select>
  );
}
