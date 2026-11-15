"""Transparent budget-aware, nearest-neighbour itinerary heuristic."""
from __future__ import annotations
from backend.models import Point, SmartRequest
from backend.services.travel import estimate
from backend.services.ai import describe_itinerary


def build(req: SmartRequest) -> dict:
    current = Point(name=req.city, lat=req.lat, lon=req.lon)
    remaining = req.minutes
    candidates = [place.model_dump() for place in req.places if req.interest == "all" or place.category == req.interest]
    used: set[str] = set()
    stops = []
    while candidates and len(stops) < 8:
        choices = []
        for p in candidates:
            if p["id"] in used:
                continue
            destination = Point(name=p["name"], lat=p["lat"], lon=p["lon"])
            trip = estimate(current, destination, req.mode)
            dwell = int(p.get("visit_minutes", 30))
            if trip["minutes"] + dwell <= remaining:
                choices.append((trip["minutes"], p["name"], p, trip))
        if not choices:
            break
        choices.sort(key=lambda x: (x[0], x[1]))
        _, _, point, trip = choices[0]
        stop = {**point, "travel_minutes": trip["minutes"], "travel_km": trip["distance_km"],
                "cumulative_minutes": req.minutes - remaining + trip["minutes"] + point["visit_minutes"]}
        stops.append(stop)
        remaining -= trip["minutes"] + point["visit_minutes"]
        current = Point(name=point["name"], lat=point["lat"], lon=point["lon"])
        used.add(point["id"])
    used_minutes = req.minutes - remaining
    if req.language == "pl":
        intro = (f"Zaproponowano {len(stops)} {stop_word(len(stops))} w {city_locative(req.city)}. "
                 f"Szacowany czas: {used_minutes} min / budżet {req.minutes} min. "
                 "Algorytm wybiera kolejne bliskie miejsca mieszczące się w czasie; to nie jest optymalna trasa drogowa.")
    else:
        intro = (f"Suggested {len(stops)} stops in {req.city}. "
                 f"Estimated duration: {used_minutes} min of {req.minutes} min available. "
                 "The nearest-fitting-stop heuristic is not a road-route optimizer.")
    ai_text = describe_itinerary(req.city, req.mode, req.minutes, stops, req.language) if req.use_ai and stops else None
    return {"stops": stops, "used_minutes": used_minutes, "remaining_minutes": remaining,
            "summary": intro, "ai_text": ai_text, "ai_used": bool(ai_text),
            "total_co2_kg": round(sum(s['travel_km'] for s in stops) * {"walk": 0, "bike": 0, "car": 170,
                                      "tram": 35, "bus": 85, "metro": 30, "train": 30}[req.mode] / 1000, 2)}


def city_locative(city: str) -> str:
    return {"Gdańsk": "Gdańsku", "Warszawa": "Warszawie", "Kraków": "Krakowie"}.get(city, city)


def stop_word(n: int) -> str:
    if n == 1:
        return "przystanek"
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return "przystanki"
    return "przystanków"
