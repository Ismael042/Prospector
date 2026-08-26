import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

from prospector.generate import _load_leads_without_site

load_dotenv()


def _client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SECRET_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_SECRET_KEY não configurados no .env")
    return create_client(url, key)


def run(input_csv: str, category: str, location: str) -> None:
    leads = _load_leads_without_site(Path(input_csv))
    if not leads:
        print("Nenhum lead sem site encontrado nesse CSV.")
        return

    client = _client()
    existing_ids = {
        row["place_id"] for row in client.table("leads").select("place_id").execute().data
    }

    inserted = 0
    skipped = 0

    for lead in leads:
        if lead["place_id"] in existing_ids:
            skipped += 1
            continue

        client.table("leads").insert(
            {
                "place_id": lead["place_id"],
                "name": lead["name"],
                "category": category,
                "location": location,
                "address": lead.get("address") or None,
                "phone": lead.get("phone") or None,
                "rating": float(lead["rating"]) if lead.get("rating") else None,
                "review_count": int(lead["review_count"]) if lead.get("review_count") else None,
                "maps_url": lead.get("maps_url") or None,
            }
        ).execute()
        inserted += 1
        print(f"  + {lead['name']}")

    print(f"\nInseridos: {inserted} | Já existiam (pulados): {skipped}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sincroniza leads sem site de um CSV do prospector.search para o Supabase."
    )
    parser.add_argument("--input", required=True, help="CSV gerado pelo prospector.search")
    parser.add_argument("--category", required=True, help='Categoria do negócio, ex: "bakery"')
    parser.add_argument("--location", required=True, help='Região buscada, ex: "Halifax, NS"')
    args = parser.parse_args()

    run(args.input, args.category, args.location)


if __name__ == "__main__":
    main()
