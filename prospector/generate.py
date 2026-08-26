import argparse
import csv
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

from prospector.ai_client import generate_pitch
from prospector.places_client import fetch_photo
from prospector.search import _slugify
from prospector.template import render_landing_page

load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LEADS_DIR = DATA_DIR / "leads"

# Preco Claude Opus 5, por token (fonte: doc oficial da API)
INPUT_PRICE_PER_TOKEN = 5.00 / 1_000_000
OUTPUT_PRICE_PER_TOKEN = 25.00 / 1_000_000

EMAIL_COMPLIANCE_FOOTER = """
---
68.440.864 ISMAEL SANTANA SILVA — CNPJ 68.440.864/0001-68
12A Rua Wlissis Guimarães, s/n, Centro, Heliópolis - BA, 48445-000, Brasil
Reply STOP to opt out of future emails.
"""


def _supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SECRET_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def _load_leads_without_site(csv_path: Path) -> list[dict]:
    with csv_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [row for row in rows if row["has_real_site"] == "False"]


def run(input_csv: str, category: str, limit: int, skip_existing: bool = False) -> None:
    sys.stdout.reconfigure(line_buffering=True)

    leads = _load_leads_without_site(Path(input_csv))
    if skip_existing:
        leads = [
            lead
            for lead in leads
            if not (LEADS_DIR / _slugify(lead["name"]) / "landing.html").exists()
        ]
    leads = leads[:limit]
    if not leads:
        print("Nenhum lead sem site encontrado nesse CSV.")
        return

    LEADS_DIR.mkdir(parents=True, exist_ok=True)
    supabase = _supabase_client()

    total_cost = 0.0
    processed = 0
    failed = 0

    for lead in leads:
        print(f"Gerando pitch para: {lead['name']}...")
        try:
            copy, usage = generate_pitch(lead, category)
        except Exception as exc:
            print(f"  FALHOU (copy): {exc}")
            failed += 1
            continue

        photo = fetch_photo(lead.get("photo_name"))
        photo_bytes, photo_content_type = photo if photo else (None, None)
        print(f"  foto: {'encontrada' if photo_bytes else 'sem foto disponível'}")

        html_doc = render_landing_page(lead, copy, photo_bytes, photo_content_type, category)

        lead_dir = LEADS_DIR / _slugify(lead["name"])
        lead_dir.mkdir(parents=True, exist_ok=True)

        (lead_dir / "email.txt").write_text(
            f"Subject: {copy.email_subject}\n\n{copy.email_body}\n{EMAIL_COMPLIANCE_FOOTER}",
            encoding="utf-8",
        )
        (lead_dir / "landing.html").write_text(html_doc, encoding="utf-8")

        key_points = "\n".join(f"- {point}" for point in copy.call_key_points)
        call_script = (
            f"Ligar para: {lead['name']} — {lead.get('phone') or 'telefone não informado'}\n\n"
            f"ABERTURA\n{copy.call_opening}\n\n"
            f"PONTOS-CHAVE\n{key_points}\n\n"
            f"FECHAMENTO\n{copy.call_closing_ask}\n"
        )
        (lead_dir / "call_script.txt").write_text(call_script, encoding="utf-8")

        if supabase is not None:
            try:
                supabase.table("leads").update(
                    {
                        "landing_html": html_doc,
                        "email_subject": copy.email_subject,
                        "email_body": copy.email_body,
                        "call_script": call_script,
                    }
                ).eq("place_id", lead["place_id"]).execute()
            except Exception as exc:
                print(f"  aviso: não consegui espelhar no Supabase: {exc}")

        total_cost += (
            usage["input_tokens"] * INPUT_PRICE_PER_TOKEN
            + usage["output_tokens"] * OUTPUT_PRICE_PER_TOKEN
        )
        processed += 1
        print(f"  OK -> {lead_dir}")

    print(f"\nProcessados: {processed} | Falharam: {failed} | Custo aproximado: ${total_cost:.4f}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera copy de e-mail + mockup de landing page para leads sem site."
    )
    parser.add_argument("--input", required=True, help="CSV gerado pelo prospector.search")
    parser.add_argument("--category", required=True, help='Categoria do negócio, ex: "bakery"')
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Pula leads que já têm data/leads/<slug>/landing.html gerado",
    )
    args = parser.parse_args()

    run(args.input, args.category, args.limit, skip_existing=args.skip_existing)


if __name__ == "__main__":
    main()
