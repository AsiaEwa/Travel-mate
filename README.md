# ✳ TravelMate — aplikacja MVP / Planer podróży
Python Full-Stack

**TravelMate** to niewielka aplikacja webowa z dwujęzycznym interfejsem (PL/EN), napisana w Pythonie po stronie **frontendu (Gradio)** i **backendu (FastAPI)**. Pozwala odkryć ciekawe obiekty turystyczne i biznesowe, dobrać plan zwiedzania do dostępnego czasu oraz znaleźć serwisy transportu publicznego dla danego miasta. Zapisane plany przechowuje w lokalnej bazie **SQLite**.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB) ![FastAPI](https://img.shields.io/badge/API-FastAPI-009688) ![Gradio](https://img.shields.io/badge/Frontend-Gradio-F97316) ![SQLite](https://img.shields.io/badge/Database-SQLite-003B57)

**Demonstracja:** [https://github.com/AsiaEwa/Travel-mate/releases/tag/v1.0.0 — film demonstracyjny w zakładce releases, **symulacja działania przykładowego wyboru w aplikacji oparta na wynikach API**.

## Funkcje

- **Wyszukiwanie kraju i miasta:** gotowe dane offline dla wybranyh miast: Gdańska, Warszawy, Krakowa, Londynu, Paryża i Berlina; dla innych miast geokodowanie przez OpenStreetMap Nominatim (wymaga internetu i dłuższego ładowania).
- **Miejsca warte zobaczenia:** wybrane zabytki, muzea, dworce, centra biznesowe/konferencyjne; filtrowanie: turystyka, biznes, wszystkie; opcjonalnie obiekty w promieniu 3,5 km od centrum.
- **Trasa A → B:** dwa wybrane punkty, 7 środków transportu: pieszo, rower, samochód, tramwaj, autobus, metro, pociąg; orientacyjny czas, dystans i link do Google Maps.
- **Transport lokalny:** dla miast demonstracyjnych linki do konkretnych oficjalnych przewoźników/organizatorów i planerów połączeń, uporządkowane według zgodności z wybranym środkiem komunikacji. Dla innych miast linki do map/planera ogólnego, bez zgadywania lokalnych przewoźników.
- **Smart Plan (creative twist):** algorytm wybiera kolejno najbliższe jeszcze nieodwiedzone miejsca mieszczące się w limicie czasu, uwzględniając szacowany dojazd i wizytę. Dodatkowo pokazuje uproszczone zestawienie CO₂ na pasażera i oszczędności względem auta.
- **Opcjonalne AI:** jeżeli ustawisz `OPENAI_API_KEY`, dodatkowa funkcja tworzy krótki opis *już obliczonego planu* przez OpenAI Responses API. AI nie wyznacza czasów przejazdu i nie może dopisywać nowych miejsc. **Bez klucza aplikacja działa normalnie**; opis planu przygotowuje algorytm regułowy.
- **CRUD planów:** tworzenie, lista/odczyt, aktualizacja nazwy/środka transportu/limitu czasu i usuwanie zapisanych wycieczek.

> **Istotne ograniczenia MVP:** „popularne” miejsca w 6 miastach to ** przygotowany katalog demonstracyjny**, a nie globalny ranking popularności. Dane OSM dla pozostałych miast to wybrane punkty w ograniczonej okolicy centrum — nie ranking. Czasy tramwaju, autobusu, metra, pociągu, roweru i pieszego przejścia są **uproszczonymi estymacjami**, nie rozkładami, danymi o korkach ani realnymi trasami po sieci. Dla samochodu backend próbuje dodatkowo skorzystać z publicznego demo OSRM (po niepowodzeniu też liczy estymację). Sprawdź rzeczywiste przejazdy i rozkłady u przewoźników. Ilości CO₂ mają charakter ilustracyjny, nie są audytowanym śladem węglowym. Nazwy obiektów i godziny otwarcia należy weryfikować.

## Technologie i architektura

| Warstwa | Technologie | Zadanie |
|---|---|---|
| Frontend (Python) | Gradio 6, HTML/CSS | Widoki, formularze, callbacki i komunikacja HTTP |
| Backend (Python) | FastAPI, Pydantic, Uvicorn | REST, walidacja, CORS, logika aplikacji |
| Baza danych | SQLite (`sqlite3` z Pythona) | Trwały CRUD planów; bez serwera bazy |
| Dane/mapa | OpenStreetMap / Nominatim / Overpass, opcjonalny OSRM | Miasta, punkty, mapa / orientacyjna trasa auta |
| AI (opcjonalne) | OpenAI Responses API | Krótki opis zaakceptowanego planu |
| Testy | pytest, FastAPI TestClient | Testy endpointów, reguł planowania, CRUD |

```text
travelmate-mvp/
├── backend/
│   ├── main.py                # endpointy REST + CORS
│   ├── models.py              # schematy wejścia Pydantic
│   ├── db.py                  # SQLite CRUD
│   └── services/
│       ├── geo.py             # Nominatim, Overpass, cache, offline fallback
│       ├── seed.py            # katalog demonstracyjnych miast
│       ├── travel.py          # czasy, Google Maps, transport, CO₂
│       ├── planner.py         # algorytm Smart Plan
│       └── ai.py              # opcjonalny prompt LLM
├── frontend/
│   ├── app.py                 # Gradio UI i callbacki
│   ├── client.py              # JEDYNA warstwa HTTP FE → BE
│   └── ui.py                  # renderery czystego HTML
├── tests/test_api.py
├── demo/
│   ├── travelmate_demo.mp4
│   └── create_demo.py         # generator animowanej symulacji
├── AGENTS.md                  # zasady dla ewentualnych agentów kodujących
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

Frontend i backend uruchamiają się jako **dwa procesy**. Frontend używa `httpx` przez `frontend/client.py` i **nie czyta bezpośrednio SQLite**. CORS w FastAPI pozwala domyślnie na `http://localhost:7860` i `http://127.0.0.1:7860`; można to zmienić przez `CORS_ORIGINS`.

## Lokalny start na Windows (PowerShell) — krok po kroku

**Wymagane:** Python **3.11+** z zaznaczoną opcją *Add Python to PATH*, internet do instalacji pakietów oraz przeglądarka. Git jest potrzebny do publikacji, ale nie do startu lokalnego.

1. Pobierz ZIP projektu, **rozpakuj** i otwórz terminal PowerShell w folderze `travelmate-mvp` (Shift + prawy przycisk myszy → *Otwórz w terminalu*).
2. Utwórz środowisko i zainstaluj biblioteki:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. **Terminal 1 — backend:**

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```

   Otwórz http://127.0.0.1:8000/docs — automatyczna dokumentacja **Swagger API**. Test stanu: http://127.0.0.1:8000/api/health.

4. **Terminal 2 — frontend:** otwórz **drugie okno PowerShell** w tym samym folderze projektu:

   ```powershell
   .\.venv\Scripts\python.exe -m frontend.app
   ```

5. Otwórz w przeglądarce **http://127.0.0.1:7860**. Gotowe. Domyślnie pokazuje się Gdańsk. Kliknij **Szukaj**, ustaw czas, wybierz transport, **Zaproponuj plan trasy**, a potem **Zapisz plan**. Zakładka **Moje plany** pozwala edytować i usuwać rekordy.

6. Zatrzymanie serwerów: w obu terminalach naciśnij `Ctrl+C`.

**macOS/Linux:** po rozpakowaniu projektu:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# terminal 1: uvicorn backend.main:app --reload
# terminal 2: python -m frontend.app
```

**Testy (w folderze projektu):**

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Przykładowy wynik: `6 passed` (uruchomione lokalnie przy przygotowaniu MVP).

### Jak włączyć AI (opcjonalne)

Bez AI aplikacja realizuje pełen scenariusz i wszystkie wymagane CRUD. Aby dodać generowanie 2–3 zdań o trasie, przed uruchomieniem backendu ustaw w **Terminalu 1**:

```powershell
$env:OPENAI_API_KEY = 'TWOJ_KLUCZ_API'
$env:OPENAI_MODEL = 'gpt-5.4-mini'
```

Uruchom backend, zaznacz **AI (opcjonalnie)** i wygeneruj plan. Tę funkcję uruchamia backend, a nie przeglądarka. Nie udostępniaj klucza publicznie (tylko lokalne uruchomienie).

### Sieć i tryb offline

- 6 miast demonstracyjnych działa **bez zapytań do OSM** (mapa w iframe do wyświetlenia potrzebuje internetu; punkty i plan działają offline).
- Inne miasta: internet, usługa Nominatim, punktowe zapytanie Overpass (czasem serwisy mają limity lub przerwy). W razie błędu interfejs pokazuje komunikat, a nie wymyśla wyników.
- Nominatim jest wywoływany wyłącznie po kliknięciu **Szukaj** lub Enter, nigdy dla każdej wpisanej litery; żądania są cache'owane i ograniczone do 1/s. Przy publicznym wdrożeniu ustaw poprawny `OSM_USER_AGENT` z identyfikatorem i własnym kontaktem; przestrzegaj [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/).
- Dla rozkładów i połączeń otwieramy oficjalne strony operatorów lub zewnętrzne mapy. Brak integracji z bieżącym GTFS/GTFS-RT.

## REST API

| Metoda | Endpoint | Opis |
|---|---|---|
| `GET` | `/api/health` | Stan API |
| `GET` | `/api/cities/search?q=Gdańsk&country=Polska` | Wyszukaj miasto |
| `GET` | `/api/places?city=Gdańsk&country=Polska&lat=54.35&lon=18.653` | Lista POI |
| `GET` | `/api/transport?city=Gdańsk&country=Polska&mode=tram` | Linki transportowe, sortowane wg wyboru |
| `POST` | `/api/routes/estimate` | Dystans/czas A → B, tryb, link Maps |
| `POST` | `/api/itineraries/suggest` | Trasa w zadanym budżecie czasu |
| `GET` | `/api/plans` | READ: lista planów |
| `POST` | `/api/plans` | CREATE: nowy plan |
| `GET` | `/api/plans/{id}` | READ: jeden plan |
| `PUT` | `/api/plans/{id}` | UPDATE: zmiana nazwy, transportu lub czasu (metadane) |
| `DELETE` | `/api/plans/{id}` | DELETE: usuń plan |

Przykład żądania (można wkleić do Swaggera `http://127.0.0.1:8000/docs`):

```json
{
  "origin": {"name": "Długi Targ", "lat": 54.3484, "lon": 18.6534},
  "destination": {"name": "Żuraw nad Motławą", "lat": 54.3509, "lon": 18.6570},
  "mode": "walk"
}
```

**Uwaga:** zmiana `mode` lub `minutes` w zapisanym rekordzie to edycja metadanych, a nie automatyczne przeliczenie starego planu. Aby dostosować trasę, wygeneruj i zapisz nową propozycję.

## Pomysł i podejście do AI

**Creative twist** to prosty, transparentny „Smart Plan + eko-porównanie”. Najpierw backend oblicza plan **deterministycznie** (heurystyka najbliższego dostępnego punktu z czasem wizyty i dojazdu). Jeśli użytkownik wyraźnie włączy AI, model otrzymuje **tylko** zatwierdzone nazwy przystanków, środki transportu i oszacowane czasy oraz prośbę o naturalny opis. Pozwala to oddzielić logikę i liczby od językowej części AI, ograniczając ryzyko halucynacji.

**Wykorzystanie asystenta AI przy tworzeniu kodu:** Projekt, struktura modułów, boilerplate FastAPI/Gradio, przykładowe testy, README i skrypt demonstracji zostały przygotowane przy wsparciu **ChatGPT (OpenAI)**. Kod uruchomiono lokalnie, endpointy przetestowano przez `pytest`, a scenariusz frontendu sprawdzono przez wywołania callbacków. Właściciel repozytorium powinien przejrzeć kod, wyjaśnić własnymi słowami architekturę i wykonać finalny test w przeglądarce na swoim komputerze. Plik `AGENTS.md` dokumentuje zasady dla narzędzi kodujących; nie oznacza, że użyto dedykowanego autonomicznego agenta.


## Źródła / informacje prawne

- OpenStreetMap © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright); uwzględnij licencję ODbL, szczególnie przy szerszym publicznym wykorzystaniu danych.
- [Nominatim Usage Policy](https://operations.osmfoundation.org/policies/nominatim/).
- Linki Gdańsk: [ZTM Gdańsk](https://ztm.gda.pl/rozklady), [SKM Trójmiasto](https://www.skm.pkp.pl/); pozostałe miasta mają odnośniki do operatorów w `seed.py`.
- [FastAPI](https://fastapi.tiangolo.com/), [Gradio](https://www.gradio.app/), [SQLite](https://www.sqlite.org/index.html), [OpenAI API](https://developers.openai.com/api/docs/guides/text).

**Status:** edukacyjny MVP, do uruchomienia lokalnego; nie jest produkcyjną nawigacją ani systemem rezerwacji.


## Wpisywanie punktów A i B z klawiatury / Typing A–B locations

W zakładce **Trasa A → B** znajdują się dwa pola tekstowe. Można wpisać
np. `Centrum miasta`, `Żuraw nad Motławą`, `Dworzec Gdańsk Główny`
lub pełny adres, np. `ul. Długa 1` (po wcześniejszym wyborze miasta).
Wybór środka transportu nie kasuje wpisanych adresów.

Znane miejsca demo rozpoznawane są lokalnie i działają offline.
Pozostałe adresy wymagają dostępu do internetu: frontend wywołuje
`GET /api/locations/resolve`, który geokoduje adres w OpenStreetMap
(Nominatim) na żądanie, po kliknięciu **Oblicz trasę**.
Wyniki są buforowane i wyszukiwanie jest ograniczone czasowo zgodnie
z limitem publicznego API. Jeśli miejsce nie zostanie znalezione,
użytkownik zobaczy czytelny komunikat.

