"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { publishPreview, unpublishPreview } from "./actions";

export function PreviewToggle({
  leadId,
  leadName,
  published,
  previewUrl,
  hasContent,
}: {
  leadId: string;
  leadName: string;
  published: boolean;
  previewUrl: string | null;
  hasContent: boolean;
}) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleToggle() {
    setPending(true);
    setError(null);
    try {
      if (published) {
        await unpublishPreview(leadId, leadName);
      } else {
        await publishPreview(leadId, leadName);
      }
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falhou");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handleToggle}
        disabled={pending || (!published && !hasContent)}
        title={!hasContent && !published ? "Gere o mockup primeiro (generate.py)" : undefined}
        className={`rounded px-2 py-1 text-xs font-medium disabled:opacity-40 ${
          published
            ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-200"
            : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
        }`}
      >
        {pending ? "..." : published ? "Publicado" : "Não publicado"}
      </button>
      {published && previewUrl && (
        <a
          href={previewUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-indigo-600 underline"
        >
          ver
        </a>
      )}
      {error && <span className="text-xs text-red-600">{error}</span>}
    </div>
  );
}
