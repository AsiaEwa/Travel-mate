"""Pure rendering helpers. All user-supplied text is escaped."""
from __future__ import annotations
from html import escape
from urllib.parse import urlencode
from math import radians, sin, cos, asin, sqrt

MODE_LABELS = {"walk": ("Pieszo", "Walking"), "bike": ("Rower", "Bicycle"),
               "car": ("Samochód", "Car"), "tram": ("Tramwaj", "Tram"),
               "bus": ("Autobus", "Bus"), "metro": ("Metro", "Metro"),
               "train": ("Pociąg", "Train")}


def haversine(lat1, lon1, lat2, lon2):
    a, b, c, d = map(radians, (lat1, lon1, lat2, lon2))
    return 6371.0088 * 2 * asin(sqrt(sin((c-a)/2)**2 + cos(a)*cos(c)*sin((d-b)/2)**2))


def tx(pl: str, en: str, lang: str) -> str:
    return en if lang == "en" else pl


def city_header(city: dict, places: list[dict], lang: str, source: str) -> str:
    if not city:
        return '<div class="info-empty">Wpisz miasto i kliknij „Szukaj” / Enter a city and click Search.</div>'
    summary = tx("Punkty w okolicy", "Places nearby", lang)
    origin = tx("Dane demonstracyjne", "Demonstration data", lang) if source == "demo" else "OpenStreetMap"
    return (f'<div class="city-head"><div class="eyebrow">EXPLORE · TRAVELMATE</div>'
            f'<h2>{escape(city["city"])}<span> · {escape(city["country"])}</span></h2>'
            f'<p>{len(places)} {summary.lower()} &nbsp;·&nbsp; {origin}</p></div>')


def places_html(places: list[dict], city: dict, lang: str) -> str:
    if not city:
        return ""
    blocks = []
    for p in places:
        km = haversine(city['lat'], city['lon'], p['lat'], p['lon'])
        cat = tx("BIZNES / USŁUGI", "BUSINESS / SERVICES", lang) if p['category'] == 'business' else tx("ZWIEDZANIE", "SIGHTSEEING", lang)
        title = p['name_en'] if lang == 'en' else p['name']
        link = 'https://www.google.com/maps/search/?' + urlencode({'api': 1, 'query': f'{p["lat"]},{p["lon"]}'})
        blocks.append(f'<div class="place"><div class="place-copy"><div class="category">{cat}</div>'
                      f'<div class="place-name">{escape(title)}</div>'
                      f'<div class="place-meta">{km:.1f} km · {p["visit_minutes"]} min</div></div>'
                      f'<a class="place-link" href="{escape(link)}" target="_blank">↗</a></div>')
    return '<div class="places-grid">' + ''.join(blocks) + '</div>' if blocks else '<p>Brak wyników / No results.</p>'


def map_html(city: dict, places: list[dict], lang: str) -> str:
    if not city:
        return ""
    lat, lon = city['lat'], city['lon']
    # A small, bounded OSM embed, with a non-embedded fallback for privacy blockers.
    delta_lat, delta_lon = (0.09, 0.15)
    bbox = f'{lon - delta_lon},{lat - delta_lat},{lon + delta_lon},{lat + delta_lat}'
    url = 'https://www.openstreetmap.org/export/embed.html?' + urlencode({'bbox': bbox, 'layer': 'mapnik', 'marker': f'{lat},{lon}'})
    href = 'https://www.openstreetmap.org/?' + urlencode({'mlat': lat, 'mlon': lon, 'zoom': 13})
    note = tx('Interaktywna mapa OSM (wymaga internetu)', 'OSM interactive map (internet required)', lang)
    return (f'<div class="map-frame"><iframe title="{escape(note)}" '
            f'src="{escape(url)}" loading="lazy" referrerpolicy="no-referrer" '
            f'allowfullscreen></iframe><div class="map-caption">📍 {escape(city["city"])} &nbsp;·&nbsp; '
            f'<a href="{escape(href)}" target="_blank">{escape(note)} ↗</a></div></div>')


def transport_html(items: list[dict], mode: str, lang: str) -> str:
    sub = tx("Oficjalne serwisy i planery · priorytet dla wybranego środka transportu", "Official services and planners · selected mode first", lang)
    rows = []
    for i, t in enumerate(items):
        label = t['name_en'] if lang == 'en' else t['name_pl']
        kinds = ', '.join(MODE_LABELS[x][1 if lang == 'en' else 0] for x in t['modes'])
        rows.append(f'<a class="transport-item" href="{escape(t["url"])}" target="_blank" rel="noopener noreferrer">'
                    f'<div><span class="rank">{i+1:02d}</span> <strong>{escape(label)}</strong><small>{escape(kinds)}</small></div><span>↗</span></a>')
    return f'<div class="section-heading"><span>{escape(sub)}</span></div><div class="transport-links">' + ''.join(rows) + '</div>'


def route_html(result: dict, origin: dict, destination: dict, lang: str) -> str:
    label = tx("Przybliżony czas", "Approximate time", lang)
    dist = tx("Dystans", "Distance", lang)
    saved = tx("Oszczędność CO₂ względem auta*", "CO₂ saved versus car*", lang)
    method = tx("dane trasy OSRM", "OSRM road route", lang) if result['source'] == 'osrm' else tx("model szacunkowy (nie rozkład jazdy)", "rough estimate (not a timetable)", lang)
    caution = tx("*Szacunek porównawczy na pasażera, bez emisji infrastruktury. Sprawdź trasę i rozkład w mapach.",
                 "*Illustrative per-passenger estimate; excludes infrastructure. Verify route and timetables in Maps.", lang)
    return (f'<div class="route-head"><span>POINT A</span><strong>{escape(origin["name"])}</strong><span>→ &nbsp;POINT B</span><strong>{escape(destination["name"])}</strong></div>'
            f'<div class="metrics"><div><small>{label}</small><strong>{result["minutes"]} min</strong></div>'
            f'<div><small>{dist}</small><strong>{result["distance_km"]:.1f} km</strong></div>'
            f'<div><small>{saved}</small><strong>{result["savings_vs_car_kg"]:.2f} kg</strong></div></div>'
            f'<p class="disclaimer">{escape(method)} · {escape(caution)}</p>'
            f'<a class="gmaps" href="{escape(result["google_maps_url"])}" target="_blank">Google Maps ↗</a>')


def itinerary_md(result: dict, lang: str) -> str:
    lines = [f"### {tx('Twój plan dnia', 'Your itinerary', lang)}", result['summary'], ""]
    for i, p in enumerate(result['stops'], 1):
        label = p['name_en'] if lang == 'en' else p['name']
        lines.append(f"**{i:02d}. {label}**  ·  {tx('dojazd', 'travel', lang)} ~{p['travel_minutes']} min  ·  {tx('pobyt', 'visit', lang)} {p['visit_minutes']} min")
    if not result['stops']:
        lines.append(tx('Nie ma punktów mieszczących się w limicie czasu. Zwiększ limit lub zmień sposób podróży.',
                        'No stops fit your time budget. Increase time or change your mode.', lang))
    lines.append(f"\n**{tx('Pozostało', 'Remaining', lang)}:** {result['remaining_minutes']} min · **CO₂:** ~{result['total_co2_kg']:.2f} kg")
    if result.get('ai_text'):
        lines.append(f"\n**AI:** {result['ai_text']}")
    return "\n\n".join(lines)
