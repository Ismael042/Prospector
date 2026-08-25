import argparse
import csv
import sys
from pathlib import Path

from prospector.ai_client import generate_pitch
from prospector.places_client import fetch_photo
from prospector.search import _slugify
from prospector.template import render_landing_page

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LEADS_DIR = DATA_DIR / "leads"

# Preco Claude Opus 5, por token (fonte: doc oficial da API)
INPUT_PRICE_PER_TOKEN = 5.00 / 1_000_000
OUTPUT_PRICE_PER_TOKEN = 25.00 / 1_000_000


def _load_leads_without_site(csv_path: Path) -> list[dict]:
    with csv_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [row for row in rows if row["has_real_site"] == "False"]


def run(input_csv: str, category: str, limit: int) -> None:
    sys.stdout.reconfigure(line_buffering=True)

    leads = _load_leads_without_site(Path(input_csv))[:limit]
    if not leads:
        print("Nenhum lead sem site encontrado nesse CSV.")
        return

    LEADS_DIR.mkdir(parents=True, exist_ok=True)

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
            f"Subject: {copy.email_subject}\n\n{copy.email_body}\n", encoding="utf-8"
        )
        (lead_dir / "landing.html").write_text(html_doc, encoding="utf-8")

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
    args = parser.parse_args()

    run(args.input, args.category, args.limit)


if __name__ == "__main__":
    main()
