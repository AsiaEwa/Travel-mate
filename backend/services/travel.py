"""Approximate route times and independent links to real journey planners."""
from __future__ import annotations
import math
import os
from urllib.parse import urlencode
import httpx
from backend.models import Point
from backend.services.seed import match_city

MODE_LABELS = {"walk": ("Pieszo", "Walking"), "bike": ("Rower", "Bicycle"),
               "car": ("Samochód", "Car"), "tram": ("Tramwaj", "Tram"),
               "bus": ("Autobus", "Bus"), "metro": ("Metro", "Metro"),
               "train": ("Pociąg", "Train")}
SPEED_KMH = {"walk": 4.7, "bike": 14, "car": 27, "tram": 20,
             "bus": 17, "metro": 28, "train": 32}
FACTOR = {"walk": 1.22, "bike": 1.24, "car": 1.38, "tram": 1.37,
          "bus": 1.5, "metro": 1.55, "train": 1.6}
WAIT_MIN = {"walk": 0, "bike": 1, "car": 4, "tram": 7, "bus": 8, "metro": 6, "train": 10}
# Simple gram CO₂e / passenger-km indicative assumptions, not a lifecycle model.
GRAM_KM = {"walk": 0, "bike": 0, "car": 170, "tram": 35,
           "bus": 85, "metro": 30, "train": 30}


def haversine(a: Point, b: Point) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (a.lat, a.lon, b.lat, b.lon))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    return 6371.0088 * 2 * math.asin(math.sqrt(math.sin(dlat / 2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon / 2)**2))


def maps_url(origin: Point, dest: Point, mode: str) -> str:
    travelmode = {"walk": "walking", "bike": "bicycling", "car": "driving"}.get(mode, "transit")
    return "https://www.google.com/maps/dir/?" + urlencode({
        "api": 1, "origin": f"{origin.lat},{origin.lon}",
        "destination": f"{dest.lat},{dest.lon}", "travelmode": travelmode})


def estimate(origin: Point, dest: Point, mode: str, external: bool = False) -> dict:
    straight = haversine(origin, dest)
    km = round(max(0.05, straight * FACTOR[mode]), 2)
    mins = max(1, math.ceil(km / SPEED_KMH[mode] * 60 + WAIT_MIN[mode]))
    source = "heuristic"
    # OSRM's public demo route is only attempted for explicit A→B car lookups.
    if mode == "car" and external and os.getenv("ALLOW_OSRM", "1") == "1":
        try:
            url = ("https://router.project-osrm.org/route/v1/driving/"
                   f"{origin.lon},{origin.lat};{dest.lon},{dest.lat}")
            r = httpx.get(url, params={"overview": "false", "steps": "false"}, timeout=6)
            r.raise_for_status()
            route = r.json()["routes"][0]
            km = round(route["distance"] / 1000, 2)
            mins = max(1, math.ceil(route["duration"] / 60))
            source = "osrm"
        except (httpx.HTTPError, ValueError, KeyError, IndexError):
            pass
    return {"distance_km": km, "minutes": mins, "mode": mode, "source": source,
            "co2_kg": round(km * GRAM_KM[mode] / 1000, 2),
            "savings_vs_car_kg": round(km * (GRAM_KM['car'] - GRAM_KM[mode]) / 1000, 2),
            "google_maps_url": maps_url(origin, dest, mode)}


def transport(city: str, country: str, mode: str) -> list[dict]:
    demo = match_city(city, country)
    choices = []
    if demo:
        for pl, en, modes, url in demo["transport"]:
            choices.append({"name_pl": pl, "name_en": en, "modes": modes, "url": url,
                            "priority": 0 if mode in modes else 1, "kind": "official_or_partner"})
        choices.sort(key=lambda option: (option["priority"], option["name_pl"]))
    # Always provide general navigation alternatives without claiming a local operator.
    choices.append({"name_pl": "Google Maps — sprawdź realną trasę", "name_en": "Google Maps — check a real route",
                    "modes": [mode], "url": "https://www.google.com/maps", "priority": 2, "kind": "journey_planner"})
    if not demo:
        choices.insert(0, {"name_pl": "OpenStreetMap — mapa miasta", "name_en": "OpenStreetMap — city map",
                           "modes": [mode], "url": "https://www.openstreetmap.org/", "priority": 1, "kind": "map"})
    return choices
