"""HTTP boundary: frontend only talks to REST endpoints, never imports backend DB."""
from __future__ import annotations
import os
import httpx

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")


class ApiError(Exception):
    pass


def call(method: str, path: str, **kwargs):
    try:
        with httpx.Client(timeout=35) as client:
            response = client.request(method, API_URL + path, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else None
    except httpx.HTTPStatusError as exc:
        raise ApiError(f"API {exc.response.status_code}: {exc.response.text[:250]}") from exc
    except httpx.RequestError as exc:
        raise ApiError(f"Brak połączenia z API / Cannot connect to API ({API_URL}).") from exc
