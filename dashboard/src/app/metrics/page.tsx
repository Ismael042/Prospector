import Link from "next/link";
import { createClient } from "@/lib/supabase/server";
import type { Lead } from "@/lib/types";
import { metricsByCategory, metricsByLocation } from "@/lib/metrics";
import { LogoutButton } from "../LogoutButton";
import { MetricsTable } from "./MetricsTable";

export const dynamic = "force-dynamic";

async function getLeads(): Promise<Lead[]> {
  const supabase = await createClient();
  const { data, error } = await supabase.from("leads").select("*");
  if (error) throw error;
  return data as Lead[];
}

export default async function MetricsPage() {
  const leads = await getLeads();
  const byCategory = metricsByCategory(leads);
  const byLocation = metricsByLocation(leads);

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
          <nav className="mt-2 flex gap-4 text-sm">
            <Link href="/" className="text-neutral-500 hover:text-neutral-800">
              Leads
            </Link>
            <Link href="/metrics" className="font-medium text-indigo-600">
              Métricas
            </Link>
          </nav>
        </div>
        <LogoutButton />
      </header>

      <main className="px-8 py-8">
        <MetricsTable title="Por categoria" rows={byCategory} translateLabel />
        <MetricsTable title="Por região" rows={byLocation} />

        {leads.length === 0 && (
          <p className="text-neutral-500">Nenhum lead ainda pra calcular métricas.</p>
        )}
      </main>
    </div>
  );
}
