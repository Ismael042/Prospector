import type { Lead } from "./types";

export const STAGE_ORDER: Lead["stage"][] = [
  "found",
  "contacted",
  "replied",
  "meeting",
  "closed",
  "lost",
];

export const STAGE_LABELS: Record<Lead["stage"], string> = {
  found: "Encontrado",
  contacted: "Contatado",
  replied: "Respondeu",
  meeting: "Reunião",
  closed: "Fechado",
  lost: "Perdido",
};

// Cor semântica por estágio do funil (independe do accent do site/e-mail gerado
// pela IA no Prospector - aqui é só pra dar leitura rápida de status no dashboard).
export const STAGE_DOT: Record<Lead["stage"], string> = {
  found: "bg-neutral-400",
  contacted: "bg-sky-500",
  replied: "bg-amber-500",
  meeting: "bg-violet-500",
  closed: "bg-emerald-500",
  lost: "bg-red-400",
};

// Categorias sao texto livre (o que foi passado pro --category na busca) -
// traduz as que ja apareceram no uso real do projeto; o que nao estiver aqui
// cai no fallback (capitaliza a primeira letra) em vez de travar em ingles cru.
const CATEGORY_LABELS: Record<string, string> = {
  bakery: "Padaria",
  plumber: "Encanador",
  restaurant: "Restaurante",
  cafe: "Café",
  electrician: "Eletricista",
};

export function categoryLabel(category: string): string {
  const known = CATEGORY_LABELS[category.toLowerCase()];
  if (known) return known;
  return category.charAt(0).toUpperCase() + category.slice(1);
}
