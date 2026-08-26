import sys
import time
from datetime import date, datetime
from pathlib import Path

from prospector import generate, search, sync_supabase
from prospector.watchlist import WATCHLIST

SEARCH_MAX_RESULTS = 60
GENERATE_LIMIT = 5

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LOG_PATH = DATA_DIR / "scheduled_run.log"
LOG_RETENTION_DAYS = 30


class _Tee:
    """Escreve em vários streams ao mesmo tempo (console + arquivo de log)."""

    def __init__(self, *streams):
        self._streams = streams

    def write(self, data):
        for stream in self._streams:
            stream.write(data)

    def flush(self):
        for stream in self._streams:
            stream.flush()

    def reconfigure(self, **kwargs):
        # generate.py chama isso pra ligar line-buffering; como o Tee já
        # repassa cada write() na hora, não há buffer interno pra ajustar.
        pass


def _rotate_log_if_stale() -> None:
    """Arquiva o log do dia anterior antes de começar a escrever um novo.

    Precisa rodar ANTES de abrir o arquivo pra escrita - se o log já
    estivesse aberto (ex: via redirecionamento de shell) e fosse renomeado
    por baixo, quem já tem o handle aberto continuaria escrevendo no
    arquivo antigo, não no novo caminho.
    """
    if not LOG_PATH.exists():
        return

    last_modified = datetime.fromtimestamp(LOG_PATH.stat().st_mtime).date()
    if last_modified == date.today():
        return

    archived = DATA_DIR / f"scheduled_run.{last_modified.isoformat()}.log"
    LOG_PATH.rename(archived)

    cutoff = time.time() - LOG_RETENTION_DAYS * 86400
    for old_log in DATA_DIR.glob("scheduled_run.*.log"):
        if old_log.stat().st_mtime < cutoff:
            old_log.unlink()


def _run_targets() -> list[str]:
    summary = []

    for target in WATCHLIST:
        category = target["category"]
        location = target["location"]
        print(f"\n--- {category} / {location} — {datetime.now().isoformat(timespec='seconds')} ---")

        target_ok = True
        try:
            csv_path = search.run(category, location, SEARCH_MAX_RESULTS)
        except Exception as exc:
            print(f"  FALHOU (busca): {exc}")
            summary.append(f"{category} / {location}: falhou na busca")
            continue

        try:
            sync_supabase.run(str(csv_path), category, location)
        except Exception as exc:
            print(f"  FALHOU (sync Supabase): {exc}")
            target_ok = False

        try:
            generate.run(str(csv_path), category, GENERATE_LIMIT, skip_existing=True)
        except Exception as exc:
            print(f"  FALHOU (geração de pitch): {exc}")
            target_ok = False

        summary.append(f"{category} / {location}: {'ok' if target_ok else 'com falhas'}")

    return summary


def run() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    _rotate_log_if_stale()

    original_stdout = sys.stdout
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        sys.stdout = _Tee(original_stdout, log_file)
        try:
            start = time.monotonic()
            print(f"\n=== Prospector scheduled run — {datetime.now().isoformat(timespec='seconds')} ===")

            summary = _run_targets()

            elapsed = time.monotonic() - start
            print(f"\n=== Resumo ({elapsed:.0f}s) ===")
            for line in summary:
                print(f"  - {line}")
            print(f"=== Fim do scheduled run — {datetime.now().isoformat(timespec='seconds')} ===")
        finally:
            sys.stdout = original_stdout


if __name__ == "__main__":
    run()
