import { STAGE_LABELS, STAGE_ORDER, categoryLabel } from "@/lib/stages";
import type { GroupMetrics } from "@/lib/metrics";

function pct(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function MetricsTable({
  title,
  rows,
  translateLabel,
}: {
  title: string;
  rows: GroupMetrics[];
  translateLabel?: boolean;
}) {
  if (rows.length === 0) return null;

  return (
    <section className="mb-10">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-neutral-600">
        {title}
      </h2>
      <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-neutral-200 text-left text-neutral-500">
              <th className="px-4 py-2.5 font-medium">{title === "Por categoria" ? "Categoria" : "Região"}</th>
              <th className="px-4 py-2.5 font-medium">Total</th>
              {STAGE_ORDER.map((s) => (
                <th key={s} className="px-4 py-2.5 font-medium">
                  {STAGE_LABELS[s]}
                </th>
              ))}
              <th className="px-4 py-2.5 font-medium">Engajamento</th>
              <th className="px-4 py-2.5 font-medium">Fechamento</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.key} className="border-b border-neutral-100 last:border-0">
                <td className="px-4 py-3 font-medium text-neutral-900">
                  {translateLabel ? categoryLabel(row.key) : row.key}
                </td>
                <td className="px-4 py-3 text-neutral-600 tabular-nums">{row.total}</td>
                {STAGE_ORDER.map((s) => (
                  <td key={s} className="px-4 py-3 text-neutral-600 tabular-nums">
                    {row.byStage[s]}
                  </td>
                ))}
                <td className="px-4 py-3 tabular-nums font-medium text-sky-700">
                  {pct(row.engagedRate)}
                </td>
                <td className="px-4 py-3 tabular-nums font-medium text-emerald-700">
                  {pct(row.closedRate)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
