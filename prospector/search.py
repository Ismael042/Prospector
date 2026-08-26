import argparse
import csv
import re
import unicodedata
from datetime import datetime
from pathlib import Path

from prospector.filters import has_real_website
from prospector.places_client import search_places

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSV_FIELDS = [
    "place_id",
    "name",
    "address",
    "phone",
    "rating",
    "review_count",
    "website",
    "has_real_site",
    "maps_url",
    "photo_name",
]


def _slugify(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def run(category: str, location: str, max_results: int) -> Path:
    query = f"{category} in {location}"
    places = search_places(query, max_results=max_results)

    rows = []
    for place in places:
        row = dict(place)
        row["has_real_site"] = has_real_website(place)
        rows.append(row)

    DATA_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"results_{_slugify(category)}_{_slugify(location)}_{timestamp}.csv"
    output_path = DATA_DIR / filename

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    without_site = sum(1 for row in rows if not row["has_real_site"])
    print(f"Total encontrado: {len(rows)} | Sem site: {without_site}")
    print(f"Salvo em: {output_path}")

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Busca negócios e filtra quem não tem site.")
    parser.add_argument("--category", required=True, help='Categoria do negócio, ex: "plumber"')
    parser.add_argument("--location", required=True, help='Região, ex: "Austin, TX"')
    parser.add_argument("--max-results", type=int, default=60)
    args = parser.parse_args()

    run(args.category, args.location, args.max_results)


if __name__ == "__main__":
    main()
