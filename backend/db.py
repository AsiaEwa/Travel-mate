"""SQLite persistence, intentionally independent of the HTTP layer."""
from __future__ import annotations
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from backend.models import PlanCreate, PlanUpdate

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "plans.db"


def connect() -> sqlite3.Connection:
    path = Path(os.getenv("TRAVELMATE_DB", str(DEFAULT_PATH)))
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn


def initialize() -> None:
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            mode TEXT NOT NULL,
            minutes INTEGER NOT NULL,
            stops_json TEXT NOT NULL,
            itinerary TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""")


def row_to_plan(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    data = dict(row)
    data["stops"] = json.loads(data.pop("stops_json"))
    return data


def list_plans() -> list[dict]:
    with connect() as db:
        rows = db.execute("SELECT * FROM plans ORDER BY id DESC").fetchall()
    return [row_to_plan(row) for row in rows]


def get_plan(plan_id: int) -> dict | None:
    with connect() as db:
        row = db.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
    return row_to_plan(row)


def create_plan(data: PlanCreate) -> dict:
    with connect() as db:
        cur = db.execute("""INSERT INTO plans
            (name, city, country, mode, minutes, stops_json, itinerary, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (data.name, data.city, data.country, data.mode, data.minutes,
             json.dumps(data.stops, ensure_ascii=False), data.itinerary,
             datetime.now(timezone.utc).isoformat()))
        plan_id = cur.lastrowid
    return get_plan(plan_id)


def update_plan(plan_id: int, data: PlanUpdate) -> dict | None:
    changes = data.model_dump(exclude_none=True)
    if not get_plan(plan_id):
        return None
    if changes:
        sets = ", ".join(f"{field} = ?" for field in changes)
        with connect() as db:
            db.execute(f"UPDATE plans SET {sets} WHERE id = ?", [*changes.values(), plan_id])
    return get_plan(plan_id)


def delete_plan(plan_id: int) -> bool:
    with connect() as db:
        cur = db.execute("DELETE FROM plans WHERE id = ?", (plan_id,))
    return cur.rowcount > 0
