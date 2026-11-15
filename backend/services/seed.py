"""Small verified-looking demo catalog; illustrative curation, not a live ranking."""
from __future__ import annotations

CITIES = {
    "gdansk": {"city": "Gdańsk", "country": "Polska", "country_code": "pl", "lat": 54.3500, "lon": 18.6530,
        "aliases": ["gdańsk", "gdansk", "danzig", "gdańsk, polska"],
        "places": [
            ("Długi Targ", "Long Market", "tourism", 54.3484, 18.6534, 45),
            ("Fontanna Neptuna", "Neptune's Fountain", "tourism", 54.3488, 18.6536, 20),
            ("Bazylika Mariacka", "St. Mary's Basilica", "tourism", 54.3501, 18.6531, 40),
            ("Żuraw nad Motławą", "Historic Crane", "tourism", 54.3509, 18.6570, 30),
            ("Muzeum II Wojny Światowej", "Museum of the Second World War", "tourism", 54.3561, 18.6607, 90),
            ("Europejskie Centrum Solidarności", "European Solidarity Centre", "tourism", 54.3610, 18.6496, 70),
            ("Dworzec Gdańsk Główny", "Gdańsk Main Station", "business", 54.3559, 18.6447, 20),
            ("Politechnika Gdańska", "Gdańsk University of Technology", "business", 54.3714, 18.6185, 45),
            ("AMBEREXPO", "AMBEREXPO Exhibition Centre", "business", 54.3902, 18.6360, 45),
            ("Olivia Centre", "Olivia Business Centre", "business", 54.4055, 18.5713, 40),
        ],
        "transport": [
            ("ZTM Gdańsk — tramwaje", "ZTM Gdańsk — trams", ["tram"], "https://ztm.gda.pl/rozklady"),
            ("ZTM Gdańsk — autobusy", "ZTM Gdańsk — buses", ["bus"], "https://ztm.gda.pl/rozklady"),
            ("SKM Trójmiasto — kolej miejska", "SKM Tri-City — suburban rail", ["train"], "https://www.skm.pkp.pl/"),
            ("Jakdojade — planowanie przesiadek", "Jakdojade — transit journey planning", ["tram", "bus", "train"], "https://jakdojade.pl/gdansk/trasa/"),
        ]},
    "warszawa": {"city": "Warszawa", "country": "Polska", "country_code": "pl", "lat": 52.2319, "lon": 21.0067,
        "aliases": ["warszawa", "warsaw"],
        "places": [
            ("Zamek Królewski", "Royal Castle", "tourism", 52.2475, 21.0145, 70),
            ("Rynek Starego Miasta", "Old Town Market Square", "tourism", 52.2499, 21.0122, 35),
            ("Pałac Kultury i Nauki", "Palace of Culture and Science", "tourism", 52.2318, 21.0067, 55),
            ("Łazienki Królewskie", "Royal Łazienki Park", "tourism", 52.2151, 21.0354, 70),
            ("Warszawskie Centrum EXPO XXI", "EXPO XXI Warsaw", "business", 52.2248, 20.9633, 40),
            ("Warszawa Centralna", "Warsaw Central Station", "business", 52.2285, 21.0026, 20),
        ],
        "transport": [
            ("Warszawski Transport Publiczny — metro", "Warsaw Public Transport — metro", ["metro"], "https://www.wtp.waw.pl/"),
            ("Warszawski Transport Publiczny — tramwaje", "Warsaw Public Transport — trams", ["tram"], "https://www.wtp.waw.pl/"),
            ("Warszawski Transport Publiczny — autobusy", "Warsaw Public Transport — buses", ["bus"], "https://www.wtp.waw.pl/"),
            ("SKM Warszawa — pociągi", "Warsaw suburban rail", ["train"], "https://www.skm.warszawa.pl/"),
        ]},
    "krakow": {"city": "Kraków", "country": "Polska", "country_code": "pl", "lat": 50.0614, "lon": 19.9366,
        "aliases": ["krakow", "kraków", "cracow"],
        "places": [
            ("Rynek Główny", "Main Market Square", "tourism", 50.0616, 19.9373, 50),
            ("Sukiennice", "Cloth Hall", "tourism", 50.0617, 19.9373, 30),
            ("Zamek Królewski na Wawelu", "Wawel Royal Castle", "tourism", 50.0540, 19.9354, 80),
            ("Bazylika Mariacka", "St. Mary's Basilica", "tourism", 50.0616, 19.9390, 35),
            ("Kraków Główny", "Kraków Main Station", "business", 50.0678, 19.9475, 20),
            ("ICE Kraków Congress Centre", "ICE Kraków Congress Centre", "business", 50.0474, 19.9311, 50),
        ],
        "transport": [
            ("ZTP Kraków — tramwaje", "Kraków transit — trams", ["tram"], "https://ztp.krakow.pl/"),
            ("ZTP Kraków — autobusy", "Kraków transit — buses", ["bus"], "https://ztp.krakow.pl/"),
            ("Koleje Małopolskie — kolej", "Małopolskie Railways", ["train"], "https://kolejemalopolskie.com.pl/"),
        ]},
    "london": {"city": "London", "country": "United Kingdom", "country_code": "gb", "lat": 51.5074, "lon": -0.1278,
        "aliases": ["london", "londyn"],
        "places": [
            ("Big Ben", "Big Ben", "tourism", 51.5007, -0.1246, 30),
            ("British Museum", "British Museum", "tourism", 51.5194, -0.1269, 80),
            ("Trafalgar Square", "Trafalgar Square", "tourism", 51.5080, -0.1281, 35),
            ("Tower of London", "Tower of London", "tourism", 51.5081, -0.0759, 90),
            ("ExCeL London", "ExCeL London", "business", 51.5079, 0.0295, 45),
            ("King's Cross Station", "King's Cross Station", "business", 51.5308, -0.1238, 20),
        ],
        "transport": [
            ("TfL — Underground", "TfL — Underground", ["metro"], "https://tfl.gov.uk/plan-a-journey/"),
            ("TfL — buses", "TfL — buses", ["bus"], "https://tfl.gov.uk/modes/buses/"),
            ("TfL — trams", "TfL — trams", ["tram"], "https://tfl.gov.uk/modes/trams/"),
            ("TfL — rail/Overground", "TfL — rail/Overground", ["train"], "https://tfl.gov.uk/plan-a-journey/"),
        ]},
    "paris": {"city": "Paris", "country": "France", "country_code": "fr", "lat": 48.8566, "lon": 2.3522,
        "aliases": ["paris", "paryż", "paryz"],
        "places": [
            ("Tour Eiffel", "Eiffel Tower", "tourism", 48.8584, 2.2945, 60),
            ("Musée du Louvre", "Louvre Museum", "tourism", 48.8606, 2.3376, 100),
            ("Cathédrale Notre-Dame", "Notre-Dame Cathedral", "tourism", 48.8530, 2.3499, 40),
            ("Arc de Triomphe", "Arc de Triomphe", "tourism", 48.8738, 2.2950, 40),
            ("Palais des Congrès de Paris", "Paris Convention Centre", "business", 48.8796, 2.2838, 40),
            ("Gare du Nord", "Gare du Nord", "business", 48.8809, 2.3553, 20),
        ],
        "transport": [
            ("Île-de-France Mobilités — métro", "Île-de-France Mobilités — metro", ["metro"], "https://www.iledefrance-mobilites.fr/"),
            ("Île-de-France Mobilités — bus", "Île-de-France Mobilités — buses", ["bus"], "https://www.iledefrance-mobilites.fr/"),
            ("Île-de-France Mobilités — tram", "Île-de-France Mobilités — trams", ["tram"], "https://www.iledefrance-mobilites.fr/"),
            ("Île-de-France Mobilités — RER/rail", "Île-de-France Mobilités — rail", ["train"], "https://www.iledefrance-mobilites.fr/"),
        ]},
    "berlin": {"city": "Berlin", "country": "Germany", "country_code": "de", "lat": 52.5200, "lon": 13.4050,
        "aliases": ["berlin", "berlin niemcy"],
        "places": [
            ("Brandenburger Tor", "Brandenburg Gate", "tourism", 52.5163, 13.3777, 35),
            ("Museumsinsel", "Museum Island", "tourism", 52.5169, 13.4010, 70),
            ("Reichstagsgebäude", "Reichstag Building", "tourism", 52.5186, 13.3762, 50),
            ("Alexanderplatz", "Alexanderplatz", "tourism", 52.5219, 13.4132, 35),
            ("Messe Berlin", "Messe Berlin", "business", 52.5054, 13.2757, 45),
            ("Berlin Hauptbahnhof", "Berlin Central Station", "business", 52.5252, 13.3694, 20),
        ],
        "transport": [
            ("BVG — U-Bahn", "BVG — metro", ["metro"], "https://www.bvg.de/en/connections/route-planner"),
            ("BVG — tram", "BVG — tram", ["tram"], "https://www.bvg.de/en/connections/route-planner"),
            ("BVG — bus", "BVG — bus", ["bus"], "https://www.bvg.de/en/connections/route-planner"),
            ("VBB — S-Bahn/rail", "VBB — rail", ["train"], "https://www.vbb.de/en/"),
        ]},
}


def normalized(value: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", value.casefold()) if not unicodedata.combining(c)).strip()


COUNTRY_ALIASES = {
    "pl": ["Polska", "Poland", "PL"],
    "gb": ["United Kingdom", "UK", "Wielka Brytania", "Anglia", "Great Britain", "GB"],
    "fr": ["Francja", "France", "FR"],
    "de": ["Niemcy", "Germany", "Deutschland", "DE"],
}


def match_city(city: str, country: str = ""):
    key = normalized(city)
    country_key = normalized(country)
    for data in CITIES.values():
        aliases = [normalized(a) for a in [data["city"], *data["aliases"]]]
        countries = [normalized(c) for c in COUNTRY_ALIASES[data['country_code']]]
        if key in aliases and (not country_key or country_key in countries):
            return data
    return None


def city_places(data: dict) -> list[dict]:
    return [
        {"id": f"demo-{data['country_code']}-{i}", "name": name, "name_en": en,
         "category": category, "lat": lat, "lon": lon, "visit_minutes": duration, "source": "demo"}
        for i, (name, en, category, lat, lon, duration) in enumerate(data["places"], 1)
    ]
