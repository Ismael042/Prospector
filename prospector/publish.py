import argparse
import os
from pathlib import Path

import boto3
from dotenv import load_dotenv
from supabase import create_client

from prospector.search import _slugify

load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LEADS_DIR = DATA_DIR / "leads"


def _r2_client():
    account_id = os.environ.get("R2_ACCOUNT_ID")
    access_key = os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    if not all([account_id, access_key, secret_key]):
        raise RuntimeError(
            "R2_ACCOUNT_ID / R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY não configurados no .env"
        )

    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )


def _supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SECRET_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def _find_place_id(slug: str) -> str | None:
    supabase = _supabase_client()
    if supabase is None:
        return None

    rows = supabase.table("leads").select("place_id, name").execute().data
    for row in rows:
        if _slugify(row["name"]) == slug:
            return row["place_id"]
    return None


def publish_lead(slug: str) -> str:
    bucket = os.environ["R2_BUCKET_NAME"]
    base_url = os.environ.get("PREVIEW_BASE_URL", "").rstrip("/")

    landing_path = LEADS_DIR / slug / "landing.html"
    if not landing_path.exists():
        raise FileNotFoundError(f"Não encontrei {landing_path}")

    _r2_client().put_object(
        Bucket=bucket,
        Key=slug,
        Body=landing_path.read_bytes(),
        ContentType="text/html; charset=utf-8",
        CacheControl="public, max-age=300",
    )
    url = f"{base_url}/{slug}"

    place_id = _find_place_id(slug)
    if place_id:
        _supabase_client().table("leads").update(
            {"preview_published": True, "preview_url": url}
        ).eq("place_id", place_id).execute()

    return url


def unpublish_lead(slug: str) -> None:
    bucket = os.environ["R2_BUCKET_NAME"]
    _r2_client().delete_object(Bucket=bucket, Key=slug)

    place_id = _find_place_id(slug)
    if place_id:
        _supabase_client().table("leads").update(
            {"preview_published": False, "preview_url": None}
        ).eq("place_id", place_id).execute()


def publish_all() -> list[tuple[str, str | None, Exception | None]]:
    results = []
    for lead_dir in sorted(LEADS_DIR.iterdir()):
        if not lead_dir.is_dir() or not (lead_dir / "landing.html").exists():
            continue
        slug = lead_dir.name
        try:
            url = publish_lead(slug)
            results.append((slug, url, None))
        except Exception as exc:
            results.append((slug, None, exc))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Publica mockups de landing page no R2.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--slug", help="Publica só um lead específico (nome da pasta em data/leads/)")
    group.add_argument("--all", action="store_true", help="Publica todos os mockups já gerados")
    parser.add_argument(
        "--unpublish",
        action="store_true",
        help="Usado com --slug: remove do R2 em vez de publicar",
    )
    args = parser.parse_args()

    if args.slug:
        if args.unpublish:
            unpublish_lead(args.slug)
            print(f"OK -> removido: {args.slug}")
        else:
            url = publish_lead(args.slug)
            print(f"OK -> {url}")
        return

    results = publish_all()
    ok = 0
    for slug, url, exc in results:
        if exc:
            print(f"FALHOU ({slug}): {exc}")
        else:
            print(f"OK -> {url}")
            ok += 1
    print(f"\nPublicados: {ok}/{len(results)}")


if __name__ == "__main__":
    main()
