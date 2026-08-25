import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,places.websiteUri,"
    "places.nationalPhoneNumber,places.rating,places.userRatingCount,"
    "places.googleMapsUri,places.photos,nextPageToken"
)
PHOTO_MEDIA_URL = "https://places.googleapis.com/v1/{photo_name}/media"
PAGE_SIZE = 20
# Google recomenda um pequeno intervalo antes de reusar um pageToken recem-emitido.
PAGE_TOKEN_DELAY_SECONDS = 2


def _api_key() -> str:
    key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_PLACES_API_KEY não configurada no .env")
    return key


def _request(body: dict) -> dict:
    response = requests.post(
        SEARCH_URL,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": _api_key(),
            "X-Goog-FieldMask": FIELD_MASK,
        },
        json=body,
        timeout=15,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Places API retornou {response.status_code}: {response.text}")
    return response.json()


def _normalize(place: dict) -> dict:
    photos = place.get("photos") or []
    return {
        "place_id": place.get("id"),
        "name": place.get("displayName", {}).get("text"),
        "address": place.get("formattedAddress"),
        "phone": place.get("nationalPhoneNumber"),
        "rating": place.get("rating"),
        "review_count": place.get("userRatingCount"),
        "website": place.get("websiteUri"),
        "maps_url": place.get("googleMapsUri"),
        "photo_name": photos[0].get("name") if photos else None,
    }


def search_places(query: str, max_results: int = 60) -> list[dict]:
    results: list[dict] = []
    page_token = None

    while len(results) < max_results:
        body = {"textQuery": query, "pageSize": PAGE_SIZE}
        if page_token:
            body["pageToken"] = page_token

        data = _request(body)
        results.extend(_normalize(place) for place in data.get("places", []))

        page_token = data.get("nextPageToken")
        if not page_token:
            break
        time.sleep(PAGE_TOKEN_DELAY_SECONDS)

    return results[:max_results]


def fetch_photo(photo_name: str | None, max_width_px: int = 1200) -> tuple[bytes, str] | None:
    if not photo_name:
        return None

    response = requests.get(
        PHOTO_MEDIA_URL.format(photo_name=photo_name),
        params={"maxWidthPx": max_width_px, "key": _api_key()},
        timeout=15,
    )
    if response.status_code != 200:
        return None

    content_type = response.headers.get("Content-Type", "image/jpeg")
    return response.content, content_type
