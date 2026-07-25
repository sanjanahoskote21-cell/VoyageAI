# app/services/google_places_client.py

import requests
from app.core.config import get_settings

settings = get_settings()

GOOGLE_PLACES_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

# Curated fallback data, used whenever the live Google Places call fails
# (e.g. billing not enabled on the Cloud project) or GOOGLE_MAPS_API_KEY
# is empty. Keeps the sync pipeline fully testable without a working key —
# swap to live results automatically once billing is enabled, no code change.
MOCK_PLACES_BY_CITY: dict[str, list[dict]] = {
    "mysore": [
        {"name": "Mysore Palace", "category": "palace", "latitude": 12.3052, "longitude": 76.6552, "rating": 4.6, "external_place_id": "mock_mysore_palace"},
        {"name": "Chamundi Hills", "category": "temple", "latitude": 12.2724, "longitude": 76.6698, "rating": 4.5, "external_place_id": "mock_chamundi_hills"},
        {"name": "Brindavan Gardens", "category": "garden", "latitude": 12.4244, "longitude": 76.5732, "rating": 4.3, "external_place_id": "mock_brindavan_gardens"},
    ],
    "coorg": [
        {"name": "Abbey Falls", "category": "waterfall", "latitude": 12.4322, "longitude": 75.7392, "rating": 4.2, "external_place_id": "mock_abbey_falls"},
        {"name": "Raja's Seat", "category": "viewpoint", "latitude": 12.4184, "longitude": 75.7382, "rating": 4.4, "external_place_id": "mock_rajas_seat"},
        {"name": "Dubare Elephant Camp", "category": "wildlife", "latitude": 12.4041, "longitude": 75.8622, "rating": 4.3, "external_place_id": "mock_dubare_camp"},
    ],
    "hampi": [
        {"name": "Virupaksha Temple", "category": "temple", "latitude": 15.3350, "longitude": 76.4600, "rating": 4.6, "external_place_id": "mock_virupaksha_temple"},
        {"name": "Vittala Temple", "category": "temple", "latitude": 15.3406, "longitude": 76.4772, "rating": 4.7, "external_place_id": "mock_vittala_temple"},
        {"name": "Hampi Bazaar", "category": "market", "latitude": 15.3350, "longitude": 76.4620, "rating": 4.1, "external_place_id": "mock_hampi_bazaar"},
    ],
    "bengaluru": [
        {"name": "Lalbagh Botanical Garden", "category": "garden", "latitude": 12.9507, "longitude": 77.5848, "rating": 4.5, "external_place_id": "mock_lalbagh"},
        {"name": "Bangalore Palace", "category": "palace", "latitude": 12.9987, "longitude": 77.5920, "rating": 4.3, "external_place_id": "mock_bangalore_palace"},
    ],
}


def search_google_places(city: str, query: str | None = None) -> list[dict]:
    """
    Attempts a live Google Places Text Search call. Falls back to curated
    mock data for the given city if no API key is configured or the live
    call fails (most commonly: billing not enabled on the Cloud project).

    Each returned dict has: name, category, latitude, longitude, rating,
    external_place_id — matching what place_sync_service expects.
    """
    if settings.GOOGLE_MAPS_API_KEY:
        try:
            response = requests.get(
                GOOGLE_PLACES_TEXT_SEARCH_URL,
                params={
                    "query": f"{query or 'tourist attractions'} in {city}",
                    "key": settings.GOOGLE_MAPS_API_KEY,
                },
                timeout=5,
            )
            data = response.json()
            if data.get("status") == "OK":
                return [
                    {
                        "name": r["name"],
                        "category": (r.get("types") or ["point_of_interest"])[0],
                        "latitude": r["geometry"]["location"]["lat"],
                        "longitude": r["geometry"]["location"]["lng"],
                        "rating": r.get("rating"),
                        "external_place_id": r["place_id"],
                    }
                    for r in data.get("results", [])
                ]
            print(
                f"[places sync] Google Places API returned status="
                f"{data.get('status')} — falling back to mock data for {city}"
            )
        except requests.RequestException as exc:
            print(f"[places sync] Google Places API request failed ({exc}) — falling back to mock data")

    return MOCK_PLACES_BY_CITY.get(city.lower().strip(), [])