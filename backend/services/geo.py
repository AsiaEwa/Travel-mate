"""Geocode on explicit search and fetch a bounded set of nearby OpenStreetMap POIs.

Public endpoints are best-effort. Demo cities work offline. No autocomplete,
Nominatim is rate-limited and cached to respect their public server policy.
"""
from __future__ import annotations
import os
import threading
import time
import httpx
from backend.services.seed import CITIES, match_city, city_places, normalized

CACHE: dict[str, tuple[float, object]] = {}
NOMINATIM_LOCK = threading.Lock()
LAST_NOMINATIM = 0.0
HEADERS = {"User-Agent": os.getenv("OSM_USER_AGENT", "TravelMateMVP/1.0 (educational-demo; contact: github.com)"),
           "Accept": "application/json"}


def cached(key: str, max_age: float = 86400):
    record = CACHE.get(key)
    return record[1] if record and time.time() - record[0] < max_age else None


def store(key: str, value):
    CACHE[key] = (time.time(), value)
    return value


def search_cities(query: str, country: str = "") -> list[dict]:
    global LAST_NOMINATIM
    query = query.strip()
    if len(query) < 2:
        return []
    demo = match_city(query, country)
    if demo:
        return [{k: demo[k] for k in ("city", "country", "country_code", "lat", "lon")} | {"source": "demo"}]
    # Local matching on city names when a user types the beginning of a demo city.
    candidates = []
    for entry in CITIES.values():
        if normalized(query) in normalized(entry["city"]) and (not country or normalized(country) in (normalized(entry['country']), entry['country_code'])):
            candidates.append({k: entry[k] for k in ("city", "country", "country_code", "lat", "lon")} | {"source": "demo"})
    if candidates:
        return candidates[:5]
    cache_key = f"geo:{normalized(query)}:{normalized(country)}"
    found = cached(cache_key)
    if found is not None:
        return found
    try:
        with NOMINATIM_LOCK:
            # Max 1 request/second across this process; no typing-triggered calls.
            wait = 1.1 - (time.monotonic() - LAST_NOMINATIM)
            if wait > 0:
                time.sleep(wait)
            LAST_NOMINATIM = time.monotonic()
            with httpx.Client(timeout=8, headers=HEADERS) as client:
                response = client.get("https://nominatim.openstreetmap.org/search", params={
                    "q": f"{query}, {country}" if country else query,
                    "format": "jsonv2", "addressdetails": 1, "limit": 5,
                    "featuretype": "city", "accept-language": "pl,en"})
                response.raise_for_status()
                result = response.json()
        cities = []
        for item in result:
            address = item.get("address", {})
            city = next((address[k] for k in ("city", "town", "municipality", "village") if k in address), None)
            if city:
                cities.append({"city": city, "country": address.get("country", country),
                    "country_code": address.get("country_code", ""), "lat": float(item["lat"]),
                    "lon": float(item["lon"]), "source": "osm"})
        return store(cache_key, cities)
    except (httpx.HTTPError, ValueError, KeyError):
        return []


def find_places(city: str, country: str, lat: float, lon: float) -> tuple[list[dict], str]:
    demo = match_city(city, country)
    if demo:
        return city_places(demo), "demo"
    key = f"poi:{round(lat, 3)}:{round(lon, 3)}"
    found = cached(key, 3600)
    if found is not None:
        return found, "osm"
    # Bounded search, cap results; omit unnamed POIs and reduce server load.
    q = f'''[out:json][timeout:16];(
        nwr["tourism"~"attraction|museum|viewpoint|gallery|information"](around:3300,{lat},{lon});
        nwr["historic"~"monument|castle|memorial"](around:3300,{lat},{lon});
        nwr["amenity"~"conference_centre|townhall"](around:3300,{lat},{lon});
        nwr["office"~"company|government"](around:2600,{lat},{lon});
        nwr["railway"="station"](around:3300,{lat},{lon});
        );out center 100;'''
    try:
        with httpx.Client(timeout=22, headers=HEADERS) as client:
            r = client.post("https://overpass.kumi.systems/api/interpreter", data={"data": q})
            r.raise_for_status()
            elements = r.json().get("elements", [])
        places, names = [], set()
        for obj in elements:
            tags = obj.get("tags", {})
            name = tags.get("name:pl") or tags.get("name") or tags.get("name:en")
            if not name or normalized(name) in names:
                continue
            loc = obj.get("center", obj)
            if loc.get("lat") is None or loc.get("lon") is None:
                continue
            names.add(normalized(name))
            category = "business" if "office" in tags or tags.get("amenity") in {"conference_centre", "townhall"} or tags.get("railway") == "station" else "tourism"
            places.append({"id": f"osm-{obj['type']}-{obj['id']}", "name": name,
                "name_en": tags.get("name:en", name), "category": category,
                "lat": loc["lat"], "lon": loc["lon"], "visit_minutes": 35 if category == 'tourism' else 25, "source": "osm"})
        places.sort(key=lambda p: (p["category"] != "tourism", (p['lat'] - lat)**2 + (p['lon'] - lon)**2))
        return store(key, places[:35]), "osm"
    except (httpx.HTTPError, ValueError, KeyError):
        return [], "unavailable"


def resolve_location(query: str, city: str, country: str, lat: float, lon: float) -> dict | None:
    """Resolve a user-entered address or landmark near a selected city.

    This is an explicit-search-only endpoint: no keystroke autocomplete. Requests
    to public Nominatim are throttled and cached, as in search_cities().
    """
    global LAST_NOMINATIM
    query = query.strip()
    if len(query) < 2:
        return None

    # Demo attraction names resolve without networking.
    demo = match_city(city, country)
    if demo:
        for item in city_places(demo):
            if normalized(query) in (normalized(item['name']), normalized(item['name_en'])):
                return {'name': item['name'], 'lat': item['lat'], 'lon': item['lon']}

    cache_key = f"address:{normalized(query)}:{normalized(city)}:{normalized(country)}"
    found = cached(cache_key)
    if found is not None:
        return found

    try:
        with NOMINATIM_LOCK:
            wait = 1.1 - (time.monotonic() - LAST_NOMINATIM)
            if wait > 0:
                time.sleep(wait)
            LAST_NOMINATIM = time.monotonic()
            with httpx.Client(timeout=8, headers=HEADERS) as client:
                response = client.get('https://nominatim.openstreetmap.org/search', params={
                    'q': f'{query}, {city}, {country}' if country else f'{query}, {city}',
                    'format': 'jsonv2', 'addressdetails': 0, 'limit': 5,
                    'accept-language': 'pl,en',
                })
                response.raise_for_status()
                candidates = response.json()
        # Do not silently route to an unrelated city with a similarly named POI.
        from math import radians, sin, cos, asin, sqrt
        for item in candidates:
            point_lat, point_lon = float(item['lat']), float(item['lon'])
            a, b, c, d = map(radians, (lat, lon, point_lat, point_lon))
            km = 6371.0088 * 2 * asin(min(1., sqrt(sin((c-a)/2)**2 + cos(a)*cos(c)*sin((d-b)/2)**2)))
            if km <= 50:
                return store(cache_key, {'name': item.get('display_name', query)[:160],
                                          'lat': point_lat, 'lon': point_lon})
        return store(cache_key, None)
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        return None
