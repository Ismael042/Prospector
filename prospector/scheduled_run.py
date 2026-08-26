import sys
from datetime import datetime

from prospector import generate, search, sync_supabase
from prospector.watchlist import WATCHLIST

SEARCH_MAX_RESULTS = 60
GENERATE_LIMIT = 5


def run() -> None:
    sys.stdout.reconfigure(line_buffering=True)
    print(f"=== Prospector scheduled run — {datetime.now().isoformat(timespec='seconds')} ===")

    for target in WATCHLIST:
        category = target["category"]
        location = target["location"]
        print(f"\n--- {category} / {location} ---")

        try:
            csv_path = search.run(category, location, SEARCH_MAX_RESULTS)
        except Exception as exc:
            print(f"  FALHOU (busca): {exc}")
            continue

        try:
            sync_supabase.run(str(csv_path), category, location)
        except Exception as exc:
            print(f"  FALHOU (sync Supabase): {exc}")

        try:
            generate.run(str(csv_path), category, GENERATE_LIMIT, skip_existing=True)
        except Exception as exc:
            print(f"  FALHOU (geração de pitch): {exc}")

    print("\n=== Fim do scheduled run ===")


if __name__ == "__main__":
    run()
