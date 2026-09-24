"""
Geocoding for custom places (Nominatim / OpenStreetMap, free, no API key).

Usage:
    from app.services.geocoding_service import geocode_place, GeocodingError

    geo = geocode_place("hampi")
    geo["latitude"], geo["longitude"], geo["city"], geo["display_name"]
"""
import json
import threading
import time
import urllib.parse
import urllib.request
from functools import lru_cache

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "VoyageAI/1.0 (student project)"  # Nominatim blocks requests without one
COUNTRY_CODES = "in"  # set to None later to allow international places
KARNATAKA_VIEWBOX = "74.0,18.5,78.6,11.5"  # left,top,right,bottom - a bias, NOT a hard limit

# Old / popular spellings -> current official names (tried if the typed name finds nothing)
ALIASES = {
    "bellary": "ballari",
    "bangalore": "bengaluru",
    "mysore": "mysuru",
    "mangalore": "mangaluru",
    "coorg": "kodagu",
    "hubli": "hubballi",
    "belgaum": "belagavi",
    "gulbarga": "kalaburagi",
    "bijapur": "vijayapura",
    "shimoga": "shivamogga",
    "chikmagalur": "chikkamagaluru",
    "tumkur": "tumakuru",
    "hospet": "hosapete",
}

_lock = threading.Lock()
_last_call = 0.0


class GeocodingError(Exception):
    """Raised when a place name cannot be turned into coordinates."""


def _throttle() -> None:
    """Nominatim allows max 1 request/second."""
    global _last_call
    with _lock:
        wait = 1.1 - (time.time() - _last_call)
        if wait > 0:
            time.sleep(wait)
        _last_call = time.time()


def _search(query: str) -> list:
    _throttle()
    params = {
        "q": query,
        "format": "jsonv2",
        "limit": 5,
        "addressdetails": 1,
        "viewbox": KARNATAKA_VIEWBOX,
        "bounded": 0,
    }
    if COUNTRY_CODES:
        params["countrycodes"] = COUNTRY_CODES
    url = f"{NOMINATIM_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        raise GeocodingError(f"Location service unavailable, try again: {exc}") from exc


def _city_from(address: dict):
    for key in ("city", "town", "village", "hamlet", "suburb", "county", "state_district"):
        if address.get(key):
            return address[key]
    return None


@lru_cache(maxsize=512)
def _geocode_cached(key: str):
    # Failures raise, and lru_cache does not cache exceptions, so a bad
    # attempt never gets stuck in the cache.
    candidates = [key]
    if key in ALIASES:
        candidates.append(ALIASES[key])

    for query in candidates:
        results = _search(query)
        if results:
            best = results[0]  # Nominatim's top match; the viewbox already favours Karnataka
            address = best.get("address", {})
            return (
                float(best["lat"]),
                float(best["lon"]),
                best.get("display_name", query),
                _city_from(address),
                address.get("state"),
            )

    raise GeocodingError(f"Couldn't find '{key}'. Check the spelling or add the district, e.g. 'Hampi, Vijayanagara'.")


def geocode_place(name: str) -> dict:
    cleaned = " ".join((name or "").split())
    if len(cleaned) < 2:
        raise GeocodingError("Please enter a place name.")

    lat, lon, display_name, city, state = _geocode_cached(cleaned.lower())
    return {
        "name": cleaned.title(),
        "latitude": lat,
        "longitude": lon,
        "city": city or cleaned.title(),
        "state": state,
        "display_name": display_name,  # show this in the UI so the user can confirm the right place was picked
    }


if __name__ == "__main__":
    for place in ["bellary", "hampi", "coorg", "asdfghjkl"]:
        try:
            print(place, "->", geocode_place(place))
        except GeocodingError as err:
            print(place, "-> ERROR:", err)