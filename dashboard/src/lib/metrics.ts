import { STAGE_ORDER } from "./stages";
import type { Lead } from "./types";

export type GroupMetrics = {
  key: string;
  total: number;
  byStage: Record<Lead["stage"], number>;
  closedRate: number;
  engagedRate: number;
};

function aggregate(leads: Lead[], keyFn: (lead: Lead) => string): GroupMetrics[] {
  const groups = new Map<string, Lead[]>();
  for (const lead of leads) {
    const key = keyFn(lead);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(lead);
  }

  return Array.from(groups.entries())
    .map(([key, groupLeads]) => {
      const byStage = Object.fromEntries(
        STAGE_ORDER.map((s) => [s, groupLeads.filter((l) => l.stage === s).length])
      ) as Record<Lead["stage"], number>;
      const total = groupLeads.length;
      const engaged = total - byStage.found;

      return {
        key,
        total,
        byStage,
        closedRate: total ? byStage.closed / total : 0,
        engagedRate: total ? engaged / total : 0,
      };
    })
    .sort((a, b) => b.total - a.total);
}

export function metricsByCategory(leads: Lead[]): GroupMetrics[] {
  return aggregate(leads, (lead) => lead.category);
}

export function metricsByLocation(leads: Lead[]): GroupMetrics[] {
  return aggregate(leads, (lead) => lead.location);
}
