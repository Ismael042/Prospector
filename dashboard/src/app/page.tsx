import { createClient } from "@/lib/supabase/server";
import type { Lead } from "@/lib/types";
import { STAGE_DOT, STAGE_LABELS, STAGE_ORDER, categoryLabel } from "@/lib/stages";
import { LogoutButton } from "./LogoutButton";
import { StageSelect } from "./StageSelect";

export const dynamic = "force-dynamic";

async function getLeads(): Promise<Lead[]> {
  const supabase = await createClient();
  const { data, error } = await supabase
    .from("leads")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) throw error;
  return data as Lead[];
}

export default async function Home() {
  const leads = await getLeads();

  return (
    <div className="min-h-screen bg-neutral-50">
      <header className="flex items-start justify-between border-b border-neutral-200 bg-white px-8 py-6">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="h-2.5 w-2.5 rounded-sm bg-indigo-600" />
            <h1 className="text-xl font-semibold tracking-tight text-neutral-900">
              Prospector
            </h1>
          </div>
          <p className="mt-1 text-sm text-neutral-500">
            {leads.length} lead{leads.length === 1 ? "" : "s"} no funil
          </p>
        </div>
        <LogoutButton />
      </header>

      <main className="px-8 py-8">
        {STAGE_ORDER.map((stage) => {
          const stageLeads = leads.filter((lead) => lead.stage === stage);
          if (stageLeads.length === 0) return null;

          return (
            <section key={stage} className="mb-10">
              <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-neutral-600">
                <span className={`h-2 w-2 rounded-full ${STAGE_DOT[stage]}`} />
                {STAGE_LABELS[stage]}
                <span className="rounded-full bg-neutral-200 px-2 py-0.5 text-xs font-medium text-neutral-600">
                  {stageLeads.length}
                </span>
              </h2>
              <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white shadow-sm">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-neutral-200 text-left text-neutral-500">
                      <th className="px-4 py-2.5 font-medium">Nome</th>
                      <th className="px-4 py-2.5 font-medium">Categoria</th>
                      <th className="px-4 py-2.5 font-medium">Região</th>
                      <th className="px-4 py-2.5 font-medium">Avaliação</th>
                      <th className="px-4 py-2.5 font-medium">Telefone</th>
                      <th className="px-4 py-2.5 font-medium">Estágio</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stageLeads.map((lead) => (
                      <tr
                        key={lead.id}
                        className="border-b border-neutral-100 last:border-0 hover:bg-neutral-50"
                      >
                        <td className="px-4 py-3 font-medium text-neutral-900">
                          {lead.maps_url ? (
                            <a
                              href={lead.maps_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="underline decoration-neutral-300 underline-offset-2 hover:decoration-neutral-500"
                            >
                              {lead.name}
                            </a>
                          ) : (
                            lead.name
                          )}
                        </td>
                        <td className="px-4 py-3 text-neutral-600">
                          {categoryLabel(lead.category)}
                        </td>
                        <td className="px-4 py-3 text-neutral-600">{lead.location}</td>
                        <td className="px-4 py-3 text-neutral-600 tabular-nums">
                          {lead.rating ? `★ ${lead.rating} (${lead.review_count})` : "—"}
                        </td>
                        <td className="px-4 py-3 text-neutral-600 tabular-nums">
                          {lead.phone ?? "—"}
                        </td>
                        <td className="px-4 py-3">
                          <StageSelect leadId={lead.id} stage={lead.stage} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          );
        })}

        {leads.length === 0 && (
          <p className="text-neutral-500">
            Nenhum lead ainda. Rode <code>prospector.sync_supabase</code> pra importar.
          </p>
        )}
      </main>
    </div>
  );
}
