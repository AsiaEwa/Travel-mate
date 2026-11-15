# Instructions for coding assistants (TravelMate MVP)

These are project-level rules, not a claim about any specific agent tool.

- Use Python 3.11+, type hints, and descriptive function names.
- Keep backend REST endpoints in `backend/main.py`, business logic in `backend/services/`, SQLite in `backend/db.py`, and UI in `frontend/`.
- The frontend must access backend data through HTTP (`frontend/client.py`), not direct SQL calls.
- Do not fake transit schedules, real-time departures, travel availability, or live traffic.
- Do not present heuristic times or CO₂ factors as precise measurements.
- Attribute OpenStreetMap and comply with Nominatim usage policy; never implement per-keystroke autocomplete.
- Any external network call must fail gracefully; demo cities must work offline.
- Do not hard-code API secrets or commit `.env` files.
- Keep CRUD tests covering create/list/get/update/delete.
- Prioritize a simple, demonstrable MVP over extra dependencies.
