"""Gradio UI; run in a second terminal: python -m frontend.app"""
from __future__ import annotations
import gradio as gr
import unicodedata
from frontend.client import call, ApiError
from frontend.ui import city_header, places_html, map_html, transport_html, route_html, itinerary_md, tx

MODES = [("🚶 Pieszo / Walk", "walk"), ("🚲 Rower / Bike", "bike"),
         ("🚗 Samochód / Car", "car"), ("🚋 Tramwaj / Tram", "tram"),
         ("🚌 Autobus / Bus", "bus"), ("🚇 Metro", "metro"),
         ("🚆 Pociąg / Train", "train")]
CATEGORIES = [("Wszystkie / All", "all"), ("Zwiedzanie / Sightseeing", "tourism"),
              ("Biznes / Business", "business")]

CSS = """
:root {--ink:#15352f;--green:#147b68;--pale:#e9f7f0;}
.gradio-container{font-family:Inter,ui-sans-serif,system-ui,sans-serif!important;max-width:1320px!important;}
body{background:#f6f9f7!important;}
#hero{background:linear-gradient(115deg,#113b34 0%,#1c7463 68%,#58a28b 100%);color:white!important;
 padding:30px 34px;border-radius:23px;margin-bottom:16px!important;box-shadow:0 16px 45px #16433822;}
#hero h1,#hero p{color:#fff!important}#hero h1{font-size:36px;line-height:1.1;letter-spacing:-1px;margin:4px 0 12px!important}
#hero p{opacity:.88;max-width:750px;font-size:15px;margin:0!important}
#hero .pill{display:inline-block;border:1px solid #ffffff66;border-radius:99px;font-size:10px;letter-spacing:2px;padding:5px 12px;color:#dcfff4}
.city-head{padding:14px 7px}.city-head h2{color:#15352f!important;font-size:32px;margin:5px 0 6px!important;letter-spacing:-1px}
.city-head h2 span{font-size:17px;color:#6c8b82;font-weight:500}.city-head p{color:#6c847b;margin:0;font-size:14px}
.eyebrow{color:#1c8870;font-weight:800;font-size:10px;letter-spacing:2px}
.places-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:7px}
.place{background:#fff;border:1px solid #e5eae7;border-radius:13px;padding:13px 14px;display:flex;align-items:center;justify-content:space-between;min-height:92px}
.category{font-size:10px;color:#19816b;font-weight:800;letter-spacing:.9px;margin-bottom:5px}
.place-name{font-size:15px;font-weight:700;color:#1b3b34;line-height:1.2}.place-meta{font-size:11px;color:#72867f;margin-top:6px}
.place-link{font-weight:900;color:#197a66!important;font-size:23px;text-decoration:none;padding:10px}
.map-frame{background:#fff;padding:6px;border-radius:16px;border:1px solid #e7eeeb}
.map-frame iframe{width:100%;height:267px;border:0;border-radius:10px;background:#e6eee9}
.map-caption{color:#61766e;font-size:12px;padding:8px}.map-caption a{color:#207d65!important}
.section-heading{margin:8px 0;color:#62796f;font-size:12px}
.transport-links{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.transport-item{border:1px solid #e5eee9;border-radius:11px;background:#fff;padding:12px;text-decoration:none!important;display:flex;justify-content:space-between;align-items:center;color:#21443a!important}
.transport-item strong{font-size:12px}.transport-item small{display:block;margin:3px 0 0 26px;color:#809187;font-size:10px}
.rank{font-size:11px;color:#1b967a;font-weight:800;margin-right:4px}
.route-head{display:flex;flex-wrap:wrap;gap:12px;align-items:center;padding:10px 0;color:#627e71}.route-head strong{color:#193e32}
.route-head span{font-size:10px;font-weight:700;letter-spacing:1px}
.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:12px 0}
.metrics>div{background:#ebf8f2;border:1px solid #d9f0e5;border-radius:12px;padding:20px 15px}
.metrics small{display:block;color:#5f8171;font-size:11px}.metrics strong{display:block;color:#0d735a;font-size:24px;margin-top:7px}
.disclaimer{color:#82918b;font-size:12px!important}.gmaps{background:#1b7d65;color:white!important;padding:9px 17px;border-radius:9px;display:inline-block;text-decoration:none!important}
.info-empty{padding:22px;color:#739085;font-size:14px}
@media(max-width:680px){.places-grid,.transport-links{grid-template-columns:1fr}.metrics{grid-template-columns:1fr}#hero h1{font-size:27px}}
"""


def filtered(places, cat, only_center, city):
    from math import radians, sin, cos, asin, sqrt
    keep = []
    for p in places or []:
        if cat != "all" and p['category'] != cat:
            continue
        if only_center and city:
            a, b, c, d = map(radians, (city['lat'], city['lon'], p['lat'], p['lon']))
            distance = 6371.0088 * 2 * asin(sqrt(sin((c-a)/2)**2 + cos(a)*cos(c)*sin((d-b)/2)**2))
            if distance > 3.5:
                continue
        keep.append(p)
    return keep


def choices_for(places, lang):
    return [(p['name_en'] if lang == 'en' else p['name'], p['id']) for p in places]


def place_choices(places, lang):
    return [(tx('Centrum miasta', 'City center', lang), "center")] + choices_for(places, lang)


def transport_for(city, mode, lang):
    if not city:
        return ""
    return transport_html(call('GET', '/api/transport', params={'city': city['city'], 'country': city['country'], 'mode': mode})['items'], mode, lang)


def load_location(city_input, country_input, lang, mode, interest, near):
    try:
        found = call('GET', '/api/cities/search', params={'q': city_input.strip(), 'country': country_input.strip()})['items']
        if not found:
            empty = city_header(None, [], lang, '')
            return {}, [], empty, '', '', gr.update(choices=[], value=[]), gr.update(value=''), gr.update(value=''), '', tx('Nie znaleziono miasta. Sprawdź nazwę i połączenie z internetem.', 'City not found. Check spelling and internet connection.', lang)
        city = found[0]
        result = call('GET', '/api/places', params={k: city[k] for k in ('city', 'country', 'lat', 'lon')})
        places = result['items']
        visible = filtered(places, interest, near, city)
        info = tx('Wybierz punkty poniżej albo pozostaw puste, aby planer dobrał je sam.', 'Select stops below or leave them empty for an automatic suggestion.', lang)
        if result['source'] == 'unavailable':
            info = tx('Nie można teraz pobrać punktów OSM. Przykłady demo działają offline: Gdańsk, Warszawa, Kraków, London, Paris, Berlin.',
                      'OSM POIs are unavailable. Offline demos: Gdańsk, Warszawa, Kraków, London, Paris, Berlin.', lang)
        return (city, places, city_header(city, visible, lang, result['source']),
                places_html(visible, city, lang), map_html(city, visible, lang),
                gr.update(choices=choices_for(visible, lang), value=[]),
                gr.update(value=tx('Centrum miasta', 'City center', lang)),
                gr.update(value=(places[0]['name_en'] if lang == 'en' else places[0]['name']) if places else ''),
                transport_for(city, mode, lang), info)
    except ApiError as e:
        raise gr.Error(str(e)) from e


def refresh_view(city, all_places, lang, mode, interest, near):
    if not city:
        return city_header(None, [], lang, ''), '', gr.update(choices=[], value=[]), '', gr.update(), gr.update()
    visible = filtered(all_places, interest, near, city)
    return (city_header(city, visible, lang, 'demo' if all_places and all_places[0]['source'] == 'demo' else 'osm'),
            places_html(visible, city, lang), gr.update(choices=choices_for(visible, lang), value=[]),
            transport_for(city, mode, lang), gr.update(), gr.update())


def suggest(city, all_places, picked_ids, lang, mode, minutes, interest, near, want_ai):
    if not city:
        raise gr.Error(tx('Najpierw wyszukaj miasto.', 'Search for a city first.', lang))
    selected = [p for p in filtered(all_places, interest, near, city) if not picked_ids or p['id'] in picked_ids]
    try:
        result = call('POST', '/api/itineraries/suggest', json={
            'city': city['city'], 'country': city['country'], 'lat': city['lat'], 'lon': city['lon'],
            'minutes': int(minutes), 'mode': mode, 'interest': interest, 'places': selected,
            'language': lang, 'use_ai': bool(want_ai)})
        return result, itinerary_md(result, lang), ''
    except ApiError as e:
        raise gr.Error(str(e)) from e


def normalized_input(value: str) -> str:
    """Normalize accents and whitespace for matching local POI names."""
    decomposed = unicodedata.normalize('NFKD', (value or '').strip())
    return ' '.join(''.join(ch for ch in decomposed if not unicodedata.combining(ch)).casefold().split())


def resolve_route_point(text: str, city: dict, all_places: list[dict], lang: str) -> dict:
    """Use loaded POIs offline; geocode any other text through our REST API."""
    query = (text or '').strip()
    if not query:
        raise gr.Error(tx('Wpisz nazwę lub adres punktu.', 'Enter a place name or address.', lang))

    q = normalized_input(query)
    if q in {'center', 'centrum', 'centrum miasta', 'city centre', 'city center',
             normalized_input(city['city'])}:
        return {'name': tx('Centrum miasta', 'City centre', lang),
                'lat': city['lat'], 'lon': city['lon']}

    for point in all_places:
        if q in {normalized_input(point.get('id', '')), normalized_input(point['name']),
                 normalized_input(point.get('name_en', ''))}:
            return {'name': point['name'], 'lat': point['lat'], 'lon': point['lon']}

    # Allow a short partial name only if it uniquely identifies one loaded place.
    matches = [p for p in all_places if len(q) >= 4 and
               (q in normalized_input(p['name']) or q in normalized_input(p.get('name_en', '')))]
    if len(matches) == 1:
        p = matches[0]
        return {'name': p['name'], 'lat': p['lat'], 'lon': p['lon']}

    try:
        # This endpoint calls OSM only on button click, not on every keystroke.
        return call('GET', '/api/locations/resolve', params={
            'q': query, 'city': city['city'], 'country': city['country'],
            'lat': city['lat'], 'lon': city['lon']})
    except ApiError as e:
        raise gr.Error(tx(
            f'Nie udało się znaleźć „{query}” w pobliżu miasta {city["city"]}. '
            'Wpisz dokładniejszy adres lub wybierz nazwę atrakcji widoczną na liście. '
            'Wyszukiwanie nowych adresów wymaga internetu.',
            f'Could not find “{query}” near {city["city"]}. '
            'Try a more precise address or an attraction shown in the list. '
            'Searching new addresses requires internet.', lang)) from e


def routes(city, all_places, origin_text, dest_text, mode, lang):
    if not city:
        raise gr.Error(tx('Najpierw wyszukaj miasto.', 'Search for a city first.', lang))
    origin = resolve_route_point(origin_text, city, all_places, lang)
    dest = resolve_route_point(dest_text, city, all_places, lang)
    if abs(origin['lat'] - dest['lat']) + abs(origin['lon'] - dest['lon']) < 1e-7:
        raise gr.Error(tx('Punkty A i B muszą być różne.', 'A and B must be different.', lang))
    try:
        result = call('POST', '/api/routes/estimate', json={
            'origin': {k: origin[k] for k in ('name', 'lat', 'lon')},
            'destination': {k: dest[k] for k in ('name', 'lat', 'lon')}, 'mode': mode})
        return route_html(result, origin, dest, lang)
    except ApiError as e:
        raise gr.Error(str(e)) from e


def plan_options():
    items = call('GET', '/api/plans')['items']
    return gr.update(choices=[(f"#{p['id']} · {p['name']} · {p['city']}", p['id']) for p in items], value=items[0]['id'] if items else None)


def load_plan(p_id, lang):
    if p_id is None:
        return '', '', 'walk', 180
    p = call('GET', f'/api/plans/{p_id}')
    stops = ', '.join(s.get('name', '') for s in p['stops']) or '—'
    md = f"### {p['name']}\n\n**{p['city']} · {p['country']}** · {p['minutes']} min · {p['mode']}\n\n{p['itinerary']}\n\n**{tx('Punkty', 'Stops', lang)}:** {stops}"
    return md, p['name'], p['mode'], p['minutes']


def save_plan(city, itinerary, name, mode, minutes, lang):
    if not city or not itinerary or not itinerary.get('stops'):
        raise gr.Error(tx('Najpierw wygeneruj plan z przystankami.', 'Generate an itinerary with stops first.', lang))
    if not (name or '').strip():
        raise gr.Error(tx('Podaj nazwę planu.', 'Enter a plan name.', lang))
    try:
        item = call('POST', '/api/plans', json={'name': name.strip(), 'city': city['city'], 'country': city['country'],
             'mode': mode, 'minutes': int(minutes), 'stops': itinerary['stops'],
             'itinerary': itinerary['summary']})
        return tx(f"✅ Zapisano plan #{item['id']} w SQLite.", f"✅ Saved plan #{item['id']} to SQLite.", lang), plan_options()
    except ApiError as e:
        raise gr.Error(str(e)) from e


def update_plan(p_id, name, mode, minutes, lang):
    if p_id is None:
        raise gr.Error(tx('Wybierz plan.', 'Select a plan.', lang))
    try:
        call('PUT', f'/api/plans/{p_id}', json={'name': name, 'mode': mode, 'minutes': int(minutes)})
        data = load_plan(p_id, lang)
        return data[0], plan_options(), tx('✅ Zaktualizowano.', '✅ Updated.', lang)
    except ApiError as e:
        raise gr.Error(str(e)) from e


def delete_plan(p_id, lang):
    if p_id is None:
        raise gr.Error(tx('Wybierz plan.', 'Select a plan.', lang))
    try:
        call('DELETE', f'/api/plans/{p_id}')
        return plan_options(), '', tx('🗑️ Usunięto plan.', '🗑️ Plan deleted.', lang)
    except ApiError as e:
        raise gr.Error(str(e)) from e


with gr.Blocks(title='TravelMate · Planer podróży') as demo:
    gr.HTML('''<div id="hero"><span class="pill"> :) · travel app 🗺️  MVP</span>
      <h1>✳ TravelMate <span style="font-weight:400;opacity:.9">/ Explore smarter</span></h1>
      <p>Odkrywaj miasta, dopasuj trasę do wolnego czasu i sprawdź transport lokalny.<br>
      Discover cities, plan your time and find the right way to get around.</p></div>''')

    city_state = gr.State({})
    places_state = gr.State([])
    itinerary_state = gr.State({})

    with gr.Row():
        country_input = gr.Textbox(label='🌍 Państwo / Country (optional)', value='Polska', scale=2)
        city_input = gr.Textbox(label='📍 Miasto / City', value='Gdańsk', scale=2)
        language = gr.Radio(choices=[('Polski', 'pl'), ('English', 'en')], value='pl', label='Language / Język', scale=1)
        search_button = gr.Button('🔎 Szukaj / Search', variant='primary', scale=1)
    with gr.Row():
        mode = gr.Dropdown(choices=MODES, value='walk', label='🚉 Transport / Mobility', scale=2)
        budget = gr.Slider(30, 480, value=180, step=15, label='⏳ Czas na trasę / Time budget (min)', scale=2)
        interest = gr.Radio(CATEGORIES, value='all', label='🎯 Preferencje / Interests', scale=2)
        near_center = gr.Checkbox(value=True, label='Centrum / City centre (3.5 km)', scale=1)
        with_ai = gr.Checkbox(value=False, label='✨ AI (opcjonalnie / optional)', scale=1)

    with gr.Tabs():
        with gr.Tab('🧭 Odkrywaj / Explore'):
            with gr.Row():
                with gr.Column(scale=3):
                    city_summary = gr.HTML()
                    place_cards = gr.HTML()
                with gr.Column(scale=2):
                    map_panel = gr.HTML()
                    info = gr.Markdown()
            gr.Markdown('#### 📌 Wybierz punkty / Choose destinations')
            selected = gr.CheckboxGroup(choices=[], label='Własny wybór (pozostaw puste = wybór automatyczny) / Your selection (empty = automatic)')
            generate = gr.Button('✨ Zaproponuj plan trasy / Suggest itinerary', variant='primary')
            itinerary_view = gr.Markdown()
            with gr.Row():
                plan_name = gr.Textbox(value='Mój plan zwiedzania', label='Nazwa planu / Plan name', scale=3)
                save_button = gr.Button('💾 Zapisz plan / Save plan', scale=1)
            saved_feedback = gr.Markdown()
            gr.Markdown('#### 🚉 Transport lokalny / Local transport')
            transit = gr.HTML()
        with gr.Tab('🗺️ Trasa A → B / Route'):
            gr.Markdown('**Wpisz z klawiatury nazwę atrakcji lub adres** (np. „Dworzec Gdańsk Główny”, „Długi Targ”, „ul. Długa 1”). Kliknij **Oblicz trasę**. Nowe adresy wymagają internetu. / **Type a place name or address** and click **Estimate route**. New addresses require internet. Estimated times are not live transit data.')
            with gr.Row():
                origin = gr.Textbox(label='A · Start / Origin', placeholder='Wpisz punkt A / Type start address', scale=2)
                destination = gr.Textbox(label='B · Koniec / Destination', placeholder='Wpisz punkt B / Type destination', scale=2)
                route_button = gr.Button('Oblicz trasę / Estimate route', variant='primary', scale=1)
            route_view = gr.HTML()
        with gr.Tab('💾 Moje plany / Saved plans'):
            with gr.Row():
                saved_list = gr.Dropdown(choices=[], label='Zapisane plany / Saved plans', scale=3)
                refresh = gr.Button('🔄 Odśwież / Refresh', scale=1)
            plan_details = gr.Markdown()
            with gr.Row():
                edit_name = gr.Textbox(label='Zmień nazwę / Rename')
                edit_mode = gr.Dropdown(MODES, value='walk', label='Zmień środek / Change mode')
                edit_minutes = gr.Slider(30, 1440, value=180, step=15, label='Zmień limit / Change minutes')
            with gr.Row():
                edit_button = gr.Button('✏️ Aktualizuj / Update', variant='primary')
                delete_button = gr.Button('🗑️ Usuń / Delete', variant='stop')
            crud_feedback = gr.Markdown()

    gr.Markdown('---\n<small>TravelMate MVP · Python FastAPI + Gradio + SQLite · OSM © OpenStreetMap contributors · Demo results are curated, not a global popularity ranking. Schedules and opening hours must be confirmed with providers.</small>')

    search_outputs = [city_state, places_state, city_summary, place_cards, map_panel,
                      selected, origin, destination, transit, info]
    search_button.click(load_location, [city_input, country_input, language, mode, interest, near_center], search_outputs)
    city_input.submit(load_location, [city_input, country_input, language, mode, interest, near_center], search_outputs)
    refresh_outputs = [city_summary, place_cards, selected, transit, origin, destination]
    for ctrl in (language, mode, interest, near_center):
        ctrl.change(refresh_view, [city_state, places_state, language, mode, interest, near_center], refresh_outputs)
    generate.click(suggest, [city_state, places_state, selected, language, mode, budget, interest, near_center, with_ai],
                   [itinerary_state, itinerary_view, saved_feedback])
    route_button.click(routes, [city_state, places_state, origin, destination, mode, language], route_view)
    save_button.click(save_plan, [city_state, itinerary_state, plan_name, mode, budget, language], [saved_feedback, saved_list])
    refresh.click(plan_options, None, saved_list)
    saved_list.change(load_plan, [saved_list, language], [plan_details, edit_name, edit_mode, edit_minutes])
    edit_button.click(update_plan, [saved_list, edit_name, edit_mode, edit_minutes, language], [plan_details, saved_list, crud_feedback])
    delete_button.click(delete_plan, [saved_list, language], [saved_list, plan_details, crud_feedback])
    demo.load(load_location, [city_input, country_input, language, mode, interest, near_center], search_outputs)
    demo.load(plan_options, None, saved_list)


if __name__ == '__main__':
    demo.launch(server_name='127.0.0.1', server_port=7860, share=False, inbrowser=False, show_error=True,
                theme=gr.themes.Soft(primary_hue='emerald', neutral_hue='slate'), css=CSS)
